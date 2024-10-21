# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 17:48:04 2024

@author: Saarit
"""

from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd
import sys

# Set up logging to a file
logging.basicConfig(filename='trading_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

sys.path.append(cwd)
from et1_stock_tickers_test import shares

# Known market holidays for 2024 (example)
market_holidays = [
    dt.date(2024, 10, 2),  # Gandhi Jayanti
    # Add other known holidays for the year here
]

# Generate trading session
def initialize_kite():
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
    return day.weekday() < 5 and day not in market_holidays  # Assuming market_holidays is defined

# Function to find the most recent trading day
def get_last_trading_day():
    """Returns the most recent trading day (skips weekends and holidays)."""
    today = dt.date.today()
    day = today - dt.timedelta(days=1)  # Start with yesterday
    
    # Keep going back until we find a market open day
    while not is_market_open(day):
        day -= dt.timedelta(days=1)
    
    return day

def fetch_ohlc(ticker, interval, start_date, end_date, kite, instrument_df):
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
            print(f"No data returned for {ticker}")
            return pd.DataFrame()

    except Exception as e:
        print(f"Error fetching OHLC data for {ticker}: {e}")
        return None

def get_last_closing_price(ticker, start_date, end_date, kite, instrument_df):
    """Function to get the last closing price of a stock."""
    try:
        # Fetch historical data for the given date range
        data = pd.DataFrame(
            kite.historical_data(
                instrument_lookup(instrument_df, ticker), 
                start_date, 
                end_date, 
                interval='day'  # Using daily interval to get closing prices
            )
        )

        if not data.empty:
            # Get the last closing price
            last_close = data['close'].iloc[-1]
            return last_close
        else:
            logging.info(f"No historical data returned for {ticker}.")
            return None

    except Exception as e:
        logging.error(f"Error fetching last closing price for {ticker}: {e}")
        return None

def save_last_closing_prices(tickers, kite, instrument_df, output_file='print.csv'):
    """
    Fetch the last closing prices for a list of tickers and save to a CSV file.

    Args:
    - tickers (list): List of stock tickers to fetch closing prices for.
    - kite (KiteConnect): Kite Connect instance for fetching live prices.
    - instrument_df (pd.DataFrame): DataFrame containing instrument information.
    - output_file (str): The name of the output CSV file.
    """
    today = dt.date.today()
    last_trading_day = get_last_trading_day()  # Get the last trading day

    closing_prices = []

    for ticker in tickers:
        last_price = get_last_closing_price(ticker, last_trading_day, last_trading_day, kite, instrument_df)
        
        if last_price is not None:
            closing_prices.append({'Ticker': ticker, 'Last Closing Price': last_price})
            print(f"{ticker}: Last Closing Price: ₹{last_price}")
        else:
            print(f"{ticker}: Last Closing Price not found.")

    # Create a DataFrame and save to CSV
    if closing_prices:
        prices_df = pd.DataFrame(closing_prices)
        prices_df.to_csv(output_file, index=False)
        print(f"Last closing prices saved to {output_file}.")
    else:
        print("No closing prices to save.")

# Example usage
if __name__ == "__main__":
    kite = initialize_kite()  # Initialize your KiteConnect instance
    instrument_df = fetch_instruments(kite)  # Fetch instrument data

    # Make sure you have the KiteConnect instance and instrument_df initialized
    if kite and not instrument_df.empty:
        save_last_closing_prices(shares, kite, instrument_df)
    else:
        print("Kite Connect instance or instrument DataFrame not initialized.")



def get_high_price_stocks_from_csv(file_path):
    """
    Read high_volume_stocks from a CSV file and select stocks
    where current_price is above 20.
    
    Args:
    - file_path (str): Path to the CSV file containing high volume stocks.
    
    Returns:
    - list: A list of tickers of stocks with current_price above 20.
    """
    try:
        # Read the CSV file into a DataFrame
        high_volume_stocks = pd.read_csv(file_path) 

        # Check if required columns exist
        required_columns = ['Ticker', 'Last Closing Price']
        if not all(col in high_volume_stocks.columns for col in required_columns):
            raise ValueError("CSV file must contain the required columns: " + ", ".join(required_columns))

        # Filter stocks with current_price greater than 20
        filtered_stocks = high_volume_stocks[high_volume_stocks['Last Closing Price'] > 20]

        # Extract the tickers
        shares = filtered_stocks['Ticker'].tolist()

        return shares
    
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []



# Example usage
if __name__ == "__main__":
    file_path = 'print.csv'  # Specify your CSV file path here
    shares = get_high_price_stocks_from_csv(file_path)
    print("Shares with current_price above 20:", shares)