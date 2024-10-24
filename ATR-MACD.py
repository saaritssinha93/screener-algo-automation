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

# Function to calculate the Average True Range (ATR)
def calculate_atr(df, window=14):
    """
    Calculate the Average True Range (ATR).
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'high', 'low', 'close').
    window (int): The window size for ATR calculation (default is 14).
    
    Returns:
    pd.Series: A series containing the ATR values.
    """
    df['High-Low'] = df['high'] - df['low']
    df['High-Close'] = np.abs(df['high'] - df['close'].shift(1))
    df['Low-Close'] = np.abs(df['low'] - df['close'].shift(1))
    
    df['True_Range'] = df[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
    atr = df['True_Range'].rolling(window=window).mean()
    
    return atr

# Function to calculate MACD
def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate the MACD (Moving Average Convergence Divergence) and Signal Line.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'close').
    fast_period (int): Fast EMA period for MACD calculation (default is 12).
    slow_period (int): Slow EMA period for MACD calculation (default is 26).
    signal_period (int): Signal line EMA period (default is 9).
    
    Returns:
    pd.DataFrame: A DataFrame with MACD Line, Signal Line, and MACD Histogram.
    """
    df['EMA_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
    df['EMA_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
    
    df['MACD_Line'] = df['EMA_fast'] - df['EMA_slow']
    df['Signal_Line'] = df['MACD_Line'].ewm(span=signal_period, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD_Line'] - df['Signal_Line']
    
    return df

# Function to calculate ATR with MACD combined strategy
def calculate_atr_macd_strategy(df, atr_window=14, macd_fast=12, macd_slow=26, macd_signal=9):
    """
    Combine ATR and MACD strategy. ATR measures volatility, and MACD identifies momentum changes.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'close', 'high', 'low').
    atr_window (int): The window size for ATR calculation (default is 14).
    macd_fast (int): Fast EMA period for MACD calculation (default is 12).
    macd_slow (int): Slow EMA period for MACD calculation (default is 26).
    macd_signal (int): Signal line EMA period for MACD (default is 9).
    
    Returns:
    pd.DataFrame: A DataFrame with ATR, MACD, and MACD Signal combined.
    """
    # Calculate ATR
    df['ATR'] = calculate_atr(df, window=atr_window)
    
    # Calculate MACD and Signal Line
    df = calculate_macd(df, fast_period=macd_fast, slow_period=macd_slow, signal_period=macd_signal)

    return df

# Function to fetch historical price data and calculate ATR with MACD strategy
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates ATR with MACD strategy.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with ATR and MACD values.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol

        # Calculate ATR with MACD
        df = calculate_atr_macd_strategy(df)

        # Preprocess NaN values
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        logging.info(f"Historical data fetched and ATR with MACD strategy calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with ATR and MACD
    print(combined_df[['symbol', 'close', 'ATR', 'MACD_Line', 'Signal_Line', 'MACD_Histogram']].head())  # Show the first few rows with ATR and MACD

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_atr_macd.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'ATR', 'MACD_Line', 'Signal_Line', 'MACD_Histogram']].head())  # Show the first few rows of individual stock data with ATR and MACD
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
