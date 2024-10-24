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

# Function to calculate various Rate of Change (ROC) indicators
def calculate_roc(df, roc_window=10):
    """
    Calculate various types of Rate of Change (ROC) indicators.
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing stock data with 'close' and 'volume' columns.
    roc_window (int): The window size for ROC calculation (default 10).
    
    Returns:
    pd.DataFrame: A DataFrame with added columns for different ROC types.
    """
    # Standard Rate of Change (ROC)
    df['ROC'] = (df['close'].diff(roc_window) / df['close'].shift(roc_window)) * 100
    
    # Smoothed Rate of Change (SROC)
    df['SROC'] = (df['close'].ewm(span=roc_window).mean().diff(roc_window) / df['close'].ewm(span=roc_window).mean().shift(roc_window)) * 100
    
    # Momentum Rate of Change (MROC)
    df['MROC'] = (df['close'].rolling(window=roc_window).sum().diff(roc_window) / df['close'].rolling(window=roc_window).sum().shift(roc_window)) * 100
    
    # Relative Rate of Change (RROC)
    df['RROC'] = (df['close'].pct_change(roc_window) / df['close'].rolling(window=roc_window).mean()) * 100
    
    # Exponential Rate of Change (EROC)
    df['EROC'] = (df['close'].ewm(span=roc_window).mean().diff(roc_window) / df['close'].ewm(span=roc_window).mean().shift(roc_window)) * 100
    
    # Zero-Centered Rate of Change (ZROC)
    df['ZROC'] = df['close'] - df['close'].shift(roc_window)
    
    # Volume Rate of Change (VROC)
    df['VROC'] = (df['volume'].diff(roc_window) / df['volume'].shift(roc_window)) * 100
    
    # Cumulative Rate of Change (CROC)
    df['CROC'] = df['ROC'].cumsum()
    
    # Weighted Rate of Change (WROC)
    weights = np.arange(1, roc_window + 1)
    df['WROC'] = df['close'].rolling(roc_window).apply(lambda prices: np.dot(prices, weights) / weights.sum())
    
    # Handle NaN values using forward fill and backward fill
    df.ffill(inplace=True)  # Forward fill missing values
    df.bfill(inplace=True)  # Backward fill remaining NaNs
    
    return df

# Function to fetch historical price data and calculate all ROC indicators
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day', roc_window=10):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates various ROC indicators.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    roc_window (int): Window size for ROC calculation (default 10).
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data, and various ROC indicators.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol
        
        # Preprocess NaN values
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        # Calculate various Rate of Change (ROC) indicators
        df = calculate_roc(df, roc_window)

        logging.info(f"Historical data fetched with various ROC indicators calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with various ROC indicators
    print(combined_df[['symbol', 'close', 'ROC', 'SROC', 'MROC', 'RROC', 'EROC', 'ZROC', 'VROC', 'CROC', 'WROC']].head())  # Show key columns

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_ROC_indicators.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'ROC', 'SROC', 'MROC', 'RROC', 'EROC', 'ZROC', 'VROC', 'CROC', 'WROC']].head())  # Show the first few rows with ROC indicators
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
