# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication without a scheduler.
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

# Function to fetch historical price data (open, high, low, close, volume) for a stock using Zerodha API
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol
        logging.info(f"Historical data fetched for {stock_symbol} from {from_date} to {to_date}.")
        
        return df

    except Exception as e:
        logging.error(f"Error fetching historical data for {stock_symbol}: {e}")
        raise

# Function to calculate the Full Stochastic Oscillator (%K and %D)
def calculate_full_stochastic_oscillator(df, k_window=14, k_smooth=3, d_smooth=3):
    """
    Calculate the Full Stochastic Oscillator (%K and %D).
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (with 'high', 'low', 'close').
    k_window (int): Window size for %K calculation (default 14).
    k_smooth (int): Smoothing window size for Full %K (default 3).
    d_smooth (int): Smoothing window size for Full %D (default 3).
    
    Returns:
    pd.DataFrame: DataFrame with Full %K and Full %D columns.
    """
    df = df.copy()

    # Calculate %K (unsmoothed)
    df['lowest_low'] = df['low'].rolling(window=k_window).min()
    df['highest_high'] = df['high'].rolling(window=k_window).max()
    df['%K_unsmoothed'] = 100 * ((df['close'] - df['lowest_low']) / (df['highest_high'] - df['lowest_low']))

    # Smooth %K (Full %K)
    df['%K_full'] = df['%K_unsmoothed'].rolling(window=k_smooth).mean()

    # Smooth %D (Full %D)
    df['%D_full'] = df['%K_full'].rolling(window=d_smooth).mean()

    return df[['%K_full', '%D_full']]

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
        
        # Calculate the Full Stochastic Oscillator for each stock
        stoch_df = calculate_full_stochastic_oscillator(df)
        df = pd.concat([df, stoch_df], axis=1)

        # Preprocess NaN values using ffill and bfill directly
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        stock_data[f"{share}_df"] = df  # Save individual stock DataFrame (e.g., HDFCBANK_df, TCS_df)
        all_data.append(df)  # Add the DataFrame to the list for combined data

    # Concatenate all DataFrames into one combined DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)  # Store the combined DataFrame in memory as 'combined_df'

    # Display the combined DataFrame with Full Stochastic Oscillator (%K, %D)
    print("Combined DataFrame with Full Stochastic Oscillator (combined_df):")
    print(combined_df[['symbol', 'close', '%K_full', '%D_full']].head())  # Show the first few rows with %K_full and %D_full

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_full_stochastic.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', '%K_full', '%D_full']].head())  # Show the first few rows of individual stock data with %K_full and %D_full
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
