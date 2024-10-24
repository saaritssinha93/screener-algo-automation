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

# Function to calculate Acceleration Bands (ABands)
def calculate_acceleration_bands(df, period=20, width_multiplier=4):
    """
    Calculate Acceleration Bands (Upper, Lower, and Middle Bands).
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing stock data with 'high', 'low', and 'close' columns.
    period (int): The period over which to calculate the bands (default 20).
    width_multiplier (int): The multiplier to calculate the upper and lower bands (default 4).
    
    Returns:
    pd.DataFrame: A DataFrame with the upper, lower, and middle bands.
    """
    # Calculate the simple moving average
    df['SMA'] = df['close'].rolling(window=period).mean()

    # Calculate upper and lower bands
    df['Upper_Band'] = df['high'] * (1 + width_multiplier * (df['high'] - df['low']) / df['high'])
    df['Lower_Band'] = df['low'] * (1 - width_multiplier * (df['high'] - df['low']) / df['low'])
    
    # Middle Band is the SMA
    df['Middle_Band'] = df['SMA']

    # Handle NaN values using forward fill and backward fill
    df.ffill(inplace=True)
    df.bfill(inplace=True)

    return df[['Upper_Band', 'Lower_Band', 'Middle_Band']]

# Function to fetch historical price data and calculate Acceleration Bands
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates Acceleration Bands.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data, and Acceleration Bands (upper, lower, middle).
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

        # Calculate Acceleration Bands
        df[['Upper_Band', 'Lower_Band', 'Middle_Band']] = calculate_acceleration_bands(df)

        logging.info(f"Historical data fetched with Acceleration Bands calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with Acceleration Bands
    print(combined_df[['symbol', 'close', 'Upper_Band', 'Lower_Band', 'Middle_Band']].head())  # Show key columns

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_Acceleration_Bands.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'Upper_Band', 'Lower_Band', 'Middle_Band']].head())  # Show the first few rows with Acceleration Bands
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
