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

# Function to fetch historical price data and calculate Stochastic Oscillator
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day', k_window=14, d_window=3):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates the Stochastic Oscillator.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    k_window (int): Window size for %K calculation (default 14).
    d_window (int): Window size for %D calculation (default 3).
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data, Stochastic %K and %D.
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

        logging.info(f"Historical data fetched and Stochastic Oscillator calculated for {stock_symbol} from {from_date} to {to_date}.")
        
        return df

    except Exception as e:
        logging.error(f"Error fetching historical data for {stock_symbol}: {e}")
        raise

# Function to calculate Williams %R
def calculate_williams_r(df, period=14):
    """
    Calculate the Williams %R indicator.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'high', 'low', 'close').
    period (int): Window size for calculating %R (default 14).
    
    Returns:
    pd.Series: Williams %R values.
    """
    df = df.copy()

    # Calculate the Highest High and Lowest Low for the period
    df['Highest_High'] = df['high'].rolling(window=period).max()
    df['Lowest_Low'] = df['low'].rolling(window=period).min()

    # Calculate Williams %R
    df['Williams_%R'] = ((df['Highest_High'] - df['close']) / (df['Highest_High'] - df['Lowest_Low'])) * -100

    return df['Williams_%R']

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
        
        # Calculate Williams %R for each stock
        df['Williams_%R'] = calculate_williams_r(df)

        # Preprocess NaN values using ffill and bfill directly
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        # Save individual stock DataFrame (e.g., HDFCBANK_df, TCS_df)
        stock_data[f"{share}_df"] = df  
        all_data.append(df)  # Add the DataFrame to the list for combined data

    # Concatenate all DataFrames into one combined DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)  # Store the combined DataFrame in memory as 'combined_df'

    # Display the combined DataFrame with Williams %R
    print("Combined DataFrame with Williams %R (combined_df):")
    print(combined_df[['symbol', 'close', 'Williams_%R']].head())  # Show the first few rows with Williams %R

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_williams_r.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'Williams_%R']].head())  # Show the first few rows of individual stock data with Williams %R
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
