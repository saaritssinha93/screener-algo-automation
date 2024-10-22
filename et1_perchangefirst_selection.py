# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication without a scheduler.
"""

import time
from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd
import numpy as np
import sys

# Set up logging to a file
logging.basicConfig(filename='trading_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

sys.path.append('C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation')
from et1_select_stocklist import shares


# Known market holidays for 2024 (example)
market_holidays = [
    dt.date(2024, 10, 2),  # Gandhi Jayanti
    # Add other known holidays for the year here
]

# Generate trading session
try:
    with open("access_token.txt", 'r') as token_file:
        access_token = token_file.read().strip()

    with open("api_key.txt", 'r') as key_file:
        key_secret = key_file.read().split()

    kite = KiteConnect(api_key=key_secret[0])
    kite.set_access_token(access_token)
    logging.info("Kite session established successfully.")

except FileNotFoundError as e:
    logging.error(f"File not found: {e}")
    raise
except Exception as e:
    logging.error(f"Error setting up Kite session: {e}")
    raise

# Get dump of all NSE instruments
try:
    instrument_dump = kite.instruments("NSE")
    instrument_df = pd.DataFrame(instrument_dump)
    logging.info("NSE instrument data fetched successfully.")
    
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
    return day.weekday() < 5 and day not in market_holidays  # Monday=0, ..., Friday=4 (market open), skip weekends and holidays

# Function to find the most recent trading day
def get_last_trading_day():
    """Returns the most recent trading day (skips weekends and holidays)."""
    today = dt.date.today()
    day = today - dt.timedelta(days=1)  # Start with yesterday
    
    # Keep going back until we find a market open day
    while not is_market_open(day):
        day -= dt.timedelta(days=1)
    
    return day

# Dictionary to store stocks with their percentage and volume change
high_growth_stocks = {}

def fetch_ohlc(ticker, interval, start_date, end_date):
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
            print(f"No data returned for {ticker}")  # Simplified message for no data
            return pd.DataFrame()

    except Exception as e:
        print(f"Error fetching OHLC data for {ticker}: {e}")  # Reduced logging to print
        return None


# Function to fetch live price
def fetch_live_price(symbol):
    """Fetches the current live price of the given stock."""
    try:
        instrument = instrument_lookup(instrument_df, symbol)
        live_price_data = kite.ltp(f"NSE:{symbol}")
        return live_price_data[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        logging.error(f"Error fetching live price for {symbol}: {e}")
        return None

def print_price_comparison(symbol):
    """Prints last market day closing price, current price, and percentage change."""    
    # Find the last trading day
    last_trading_day = get_last_trading_day()
    
    # Set date range for the last trading day and last 15 minutes
    start_date = last_trading_day
    end_date = last_trading_day
    
    # Fetch OHLC data for last trading day and today's live price
    ohlc_data = fetch_ohlc(symbol, "day", start_date, end_date)
    volume_data_15m = fetch_ohlc(symbol, "15minute", last_trading_day, last_trading_day)  # Fetch last 15-minute volume

    if ohlc_data is not None and not ohlc_data.empty:
        if 'close' in ohlc_data.columns:
            last_close = ohlc_data['close'].iloc[-1]
            live_price = fetch_live_price(symbol)
            
            if live_price is not None:
                percent_change = ((live_price - last_close) / last_close) * 100
                
                # Only output if price change is >= 2%
                if percent_change >= 2:
                    # Calculate volume change if volume data is available
                    if volume_data_15m is not None and not volume_data_15m.empty:
                        last_volume = volume_data_15m['volume'].iloc[-1]
                        last_day_volume = ohlc_data['volume'].iloc[-1]

                        if last_day_volume > 0:
                            volume_change = ((last_volume - last_day_volume) / last_day_volume) * 100
                        else:
                            volume_change = float('inf')  # Handle zero volume edge case
                        
                        # Output result in concise format
                        print(f"{symbol}: Price +{percent_change:.2f}%, Volume Change: {volume_change:.2f}%")
                        high_growth_stocks[symbol] = (percent_change, volume_change)
                    else:
                        print(f"{symbol}: Price +{percent_change:.2f}%, Volume Change: N/A")
                # If price change < 2%, minimal output
                else:
                    print(f"{symbol}: Price Change: {percent_change:.2f}%")
            else:
                print(f"Error: Live price not available for {symbol}")
        else:
            print(f"Error: Missing 'close' data for {symbol}")
    else:
        print(f"Error: Historical data not available for {symbol}")



def print_high_growth_stocks():
    """
    Prints the stock symbols with a growth of 2% or more and saves to perchangeprice.csv.
    """
    logging.info("Stocks with 2% or more increase:")

    if high_growth_stocks:
        # Sort the high_growth_stocks dictionary by the percent change in descending order
        sorted_stocks = sorted(high_growth_stocks.items(), key=lambda x: x[1][0], reverse=True)
        
        # Prepare a list for the stock symbols and corresponding data for saving
        stock_data = []
        
        for stock, (percent, volume_change) in sorted_stocks:
            if percent >= 2:  # Only consider stocks with 2% growth or more
                stock_data.append({
                    'Stock': stock,
                    'Percent Change': percent,
                    'Volume Change': volume_change
                })
                print(f"{stock}: {percent:.2f}%   Volume Change: {volume_change:.2f}%")
        
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(stock_data)
        
        # Save the DataFrame to a CSV file
        df.to_csv("perchangeprice.csv", index=False)

        logging.info("Saved high-growth stocks to perchangeprice.csv")

    else:
        logging.info("No stocks have increased by 2% or more.")
        print("No stocks have increased by 2% or more.")



        
        
for share in shares:
    print_price_comparison(share)

# Print high-growth stocks
print_high_growth_stocks()