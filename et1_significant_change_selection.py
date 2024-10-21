# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 17:41:53 2024

@author: Saarit
"""

import time
from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import scrolledtext

# Set up logging to a file
logging.basicConfig(filename='trading_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

# Known market holidays for 2024 (example)
market_holidays = [
    dt.date(2024, 10, 2),  # Gandhi Jayanti
    # Add other known holidays for the year here
]

# Generate trading session
def setup_kite_session():
    """Set up the KiteConnect session and return the kite object."""
    try:
        with open("access_token.txt", 'r') as token_file:
            access_token = token_file.read().strip()

        with open("api_key.txt", 'r') as key_file:
            key_secret = key_file.read().split()

        kite = KiteConnect(api_key=key_secret[0])
        kite.set_access_token(access_token)
        logging.info("Kite session established successfully.")
        return kite

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise
    except Exception as e:
        logging.error(f"Error setting up Kite session: {e}")
        raise

# Get dump of all NSE instruments
def fetch_instruments(kite):
    """Fetch all NSE instruments and return as a DataFrame."""
    try:
        instrument_dump = kite.instruments("NSE")
        instrument_df = pd.DataFrame(instrument_dump)
        logging.info("NSE instrument data fetched successfully.")
        return instrument_df

    except Exception as e:
        logging.error(f"Error fetching instruments: {e}")
        raise

# Function to lookup instrument token
def instrument_lookup(instrument_df, symbol):
    """Looks up instrument token for a given symbol in the instrument dump."""
    try:
        instrument_token = instrument_df[instrument_df.tradingsymbol == symbol].instrument_token.values[0]
        return instrument_token
    except IndexError:
        logging.error(f"Symbol {symbol} not found in instrument dump.")
        return -1
    except Exception as e:
        logging.error(f"Error in instrument lookup: {e}")
        return -1

# Function to check if a day is a market open day (skips weekends and holidays)
def is_market_open(day):
    """Returns True if the day is a market open day (i.e., not a weekend or a holiday)."""
    return day.weekday() < 5 and day not in market_holidays  # Monday=0, ..., Friday=4

# Function to find the most recent trading day
def get_last_trading_day():
    """Returns the most recent trading day (skips weekends and holidays)."""
    today = dt.date.today()
    day = today - dt.timedelta(days=1)  # Start with yesterday
    
    while not is_market_open(day):
        day -= dt.timedelta(days=1)
    
    return day

def fetch_ohlc(kite, ticker, interval, start_date, end_date):
    """Extracts historical OHLC data for a specific date range and returns it as a DataFrame."""
    try:
        instrument = instrument_lookup(instrument_df, ticker)
        if instrument == -1:
            raise ValueError(f"Instrument lookup failed for ticker {ticker}")

        # Fetch historical data for the given date range
        data = pd.DataFrame(
            kite.historical_data(
                instrument, 
                start_date, 
                end_date, 
                interval
            )
        )

        if not data.empty:
            data.set_index("date", inplace=True)
            return data
        else:
            logging.warning(f"No data returned for {ticker}")
            return pd.DataFrame()

    except Exception as e:
        logging.error(f"Error fetching OHLC data for {ticker}: {e}")
        return None

# Function to show a popup with significant price changes
def show_significant_changes_popup(changes):
    """Creates a popup window to display significant price changes."""
    window = tk.Tk()
    window.title("Significant Price Changes")

    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=100, height=40)
    text_area.pack(padx=10, pady=10)

    if changes:
        for change in changes:
            text_area.insert(tk.END, f"Ticker: {change['ticker']}, Time: {change['Time']}, "
                                       f"Close: {change['Close']}, Price Change: {change['Price Change']:.2f}%\n")
    else:
        text_area.insert(tk.END, "No significant price changes found.\n")

    window.after(120000, window.destroy)  # Close after 120 seconds
    window.mainloop()

def fetch_2min_intervals_for_high_growth_stocks(kite, file_path='rsi_60.csv', threshold=0.75, verbose=True):
    """Continuously fetch 2-minute interval data for high-growth stocks."""
    
    end_time = dt.datetime.now()
    start_time = end_time - dt.timedelta(minutes=2)

    # Read tickers from rsi_result.csv
    try:
        growth_stocks_df = pd.read_csv(file_path)
        growth_stocks = growth_stocks_df['ticker'].tolist()
        logging.info(f"Fetched {len(growth_stocks)} stocks from {file_path}.")
    except FileNotFoundError as e:
        logging.error(f"File {file_path} not found: {e}")
        return
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return

    today = dt.datetime.now()
    start_date = today.replace(hour=9, minute=15, second=0, microsecond=0)
    end_date = today.replace(hour=15, minute=30, second=0, microsecond=0)

    logging.info(f"Scanning 2-minute data for high-growth stocks on {today.date()}.")

    all_significant_changes = []

    for ticker in growth_stocks:
        try:
            ohlc_data_2min = fetch_ohlc(kite, ticker, '2minute', start_date, end_date)

            if ohlc_data_2min is None or ohlc_data_2min.empty:
                logging.warning(f"No 2-minute data available for {ticker}. Skipping.")
                continue

            ohlc_data_2min = get_price_changes(ohlc_data_2min)

            significant_changes = ohlc_data_2min[ohlc_data_2min['price_change'] > threshold]

            if not significant_changes.empty:
                if verbose:
                    print(f"\nSignificant positive price changes (> {threshold}% change) for {ticker} on {today.date()}:")
                    print(significant_changes[['close', 'price_change']])

                for index, row in significant_changes.iterrows():
                    all_significant_changes.append({
                        "ticker": ticker,
                        "Time": index,
                        "Close": row['close'],
                        "Price Change": row['price_change']
                    })

        except KeyError as e:
            logging.error(f"Ticker error for {ticker}: {e}")
            print(f"Error with ticker {ticker}: {e}")
        except Exception as e:
            logging.error(f"Error fetching 2-minute data for {ticker}: {e}")
            print(f"Error fetching data for {ticker}: {e}")

    if all_significant_changes:
        changes_df = pd.DataFrame(all_significant_changes)
        changes_df.to_csv("significant_change.csv", index=False)
        print(f"Significant price changes saved to significant_change.csv")
        show_significant_changes_popup(all_significant_changes)
    else:
        print("No significant price changes found for any stocks.")

    print(f"Fetched data for the 2-minute interval from {start_time} to {end_time}.")

def get_price_changes(df):
    """Calculates the percentage change in 'close' price between consecutive rows."""
    df['price_change'] = df['close'].pct_change() * 100
    return df

def main():
    
    logging.info("Starting the trading algorithm...")
    kite = setup_kite_session()
    global instrument_df
    instrument_df = fetch_instruments(kite)
    fetch_2min_intervals_for_high_growth_stocks(kite, threshold=0.75)

if __name__ == "__main__":
    main()
    logging.shutdown()
