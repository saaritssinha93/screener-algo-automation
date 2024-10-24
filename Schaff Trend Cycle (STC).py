# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication without a scheduler.
"""

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

# Function to calculate Schaff Trend Cycle (STC)
def calculate_stc(df, short_cycle=23, long_cycle=50, macd_cycle=10):
    """
    Calculate the Schaff Trend Cycle (STC) indicator.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'close').
    short_cycle (int): Short period for MACD calculation (default 23).
    long_cycle (int): Long period for MACD calculation (default 50).
    macd_cycle (int): Cycle period for MACD signal (default 10).
    
    Returns:
    pd.Series: Schaff Trend Cycle (STC) values.
    """
    # Calculate fast and slow EMAs
    short_ema = df['close'].ewm(span=short_cycle, adjust=False).mean()
    long_ema = df['close'].ewm(span=long_cycle, adjust=False).mean()

    # Calculate MACD line
    macd_line = short_ema - long_ema

    # Calculate signal line
    signal_line = macd_line.ewm(span=macd_cycle, adjust=False).mean()

    # Calculate the initial MACD Oscillator
    macd_oscillator = macd_line - signal_line

    # Perform the fast %K and %D calculations
    fast_k = (macd_oscillator - macd_oscillator.rolling(window=10).min()) / (macd_oscillator.rolling(window=10).max() - macd_oscillator.rolling(window=10).min()) * 100
    fast_d = fast_k.rolling(window=3).mean()

    # Calculate the Schaff Trend Cycle
    stc = (fast_d - fast_d.rolling(window=10).min()) / (fast_d.rolling(window=10).max() - fast_d.rolling(window=10).min()) * 100

    return stc

# Function to fetch historical price data and calculate STC
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data and calculates the Schaff Trend Cycle (STC).
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data, and STC.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol

        # Calculate Schaff Trend Cycle (STC)
        df['STC'] = calculate_stc(df)

        # Handle NaN values using ffill and bfill
        df.ffill(inplace=True)
        df.bfill(inplace=True)

        logging.info(f"Historical data fetched and STC calculated for {stock_symbol} from {from_date} to {to_date}.")
        
        return df

    except Exception as e:
        logging.error(f"Error fetching historical data for {stock_symbol}: {e}")
        raise

# Main execution block
if __name__ == "__main__":
    kite = initialize_kite()
    
    shares = ['HDFCBANK', 'TCS']
    from_date = '2022-01-01'
    to_date = '2024-12-31'

    # Dictionary to store individual DataFrames for each stock
    stock_data = {}

    # List to store the DataFrames for each stock for combined DataFrame creation
    all_data = []

    # Loop through each share and fetch the historical data
    for share in shares:
        df = fetch_historical_data(kite, share, from_date, to_date)
        
        # Save individual stock DataFrame (e.g., HDFCBANK_df, TCS_df)
        stock_data[f"{share}_df"] = df  
        all_data.append(df)  # Add the DataFrame to the list for combined data

    # Concatenate all DataFrames into one combined DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)  # Store the combined DataFrame in memory as 'combined_df'

    # Display the combined DataFrame with STC
    print(combined_df[['symbol', 'close', 'STC']].head())  # Show key columns with STC

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_stc.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'STC']].head())  # Show the first few rows of individual stock data with STC
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
