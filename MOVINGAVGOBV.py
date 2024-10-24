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

# Function to fetch historical price data and calculate OBV
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates OBV.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data and OBV.
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

        logging.info(f"Historical data fetched for {stock_symbol} from {from_date} to {to_date}.")
        
        return df

    except Exception as e:
        logging.error(f"Error fetching historical data for {stock_symbol}: {e}")
        raise

# Function to calculate OBV
def calculate_obv(df):
    """
    Calculate the On Balance Volume (OBV) indicator.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'close' and 'volume').
    
    Returns:
    pd.Series: OBV values.
    """
    df['OBV'] = 0  # Initialize OBV
    
    # Iterate through each row and calculate OBV using loc
    for i in range(1, len(df)):
        if df.loc[i, 'close'] > df.loc[i-1, 'close']:
            df.loc[i, 'OBV'] = df.loc[i-1, 'OBV'] + df.loc[i, 'volume']
        elif df.loc[i, 'close'] < df.loc[i-1, 'close']:
            df.loc[i, 'OBV'] = df.loc[i-1, 'OBV'] - df.loc[i, 'volume']
        else:
            df.loc[i, 'OBV'] = df.loc[i-1, 'OBV']  # No change in OBV if close price is the same

    return df['OBV']

# Function to calculate SMA of OBV
def calculate_sma_obv(df, period=20):
    """
    Calculate the Simple Moving Average (SMA) of OBV.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing OBV values.
    period (int): Window size for the SMA (default 20).
    
    Returns:
    pd.Series: SMA of OBV values.
    """
    df['SMA_OBV'] = df['OBV'].rolling(window=period).mean()
    return df['SMA_OBV']

# Function to calculate EMA of OBV
def calculate_ema_obv(df, period=20):
    """
    Calculate the Exponential Moving Average (EMA) of OBV.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing OBV values.
    period (int): Window size for the EMA (default 20).
    
    Returns:
    pd.Series: EMA of OBV values.
    """
    df['EMA_OBV'] = df['OBV'].ewm(span=period, adjust=False).mean()
    return df['EMA_OBV']

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
        
        # Calculate OBV for each stock
        df['OBV'] = calculate_obv(df)

        # Calculate SMA and EMA of OBV
        df['SMA_OBV'] = calculate_sma_obv(df)
        df['EMA_OBV'] = calculate_ema_obv(df)

        # Preprocess NaN values using ffill and bfill directly
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        # Save individual stock DataFrame (e.g., HDFCBANK_df, TCS_df)
        stock_data[f"{share}_df"] = df  
        all_data.append(df)  # Add the DataFrame to the list for combined data

    # Concatenate all DataFrames into one combined DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)  # Store the combined DataFrame in memory as 'combined_df'

    # Display the combined DataFrame with OBV, SMA OBV, and EMA OBV
    print("Combined DataFrame with OBV, SMA OBV, and EMA OBV (combined_df):")
    print(combined_df[['symbol', 'close', 'OBV', 'SMA_OBV', 'EMA_OBV']].head())  # Show the first few rows with OBV and its moving averages

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_moving_avg_obv.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'OBV', 'SMA_OBV', 'EMA_OBV']].head())  # Show the first few rows of individual stock data with OBV, SMA OBV, EMA OBV
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
