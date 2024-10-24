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

# Function to calculate ADX (Average Directional Index)
def calculate_adx(df, period=14):
    """
    Calculate the Average Directional Index (ADX), +DI, and -DI.
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing stock data with 'high', 'low', and 'close' columns.
    period (int): The period over which to calculate the ADX (default 14).
    
    Returns:
    pd.DataFrame: A DataFrame with ADX, +DI, and -DI values.
    """
    # Calculate True Range (TR)
    df['TR'] = np.maximum(df['high'] - df['low'], 
                          np.maximum(abs(df['high'] - df['close'].shift(1)), 
                                     abs(df['low'] - df['close'].shift(1))))
    
    # Calculate the directional movement (DM)
    df['DM+'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']), 
                         np.maximum(df['high'] - df['high'].shift(1), 0), 0)
    df['DM-'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)), 
                         np.maximum(df['low'].shift(1) - df['low'], 0), 0)
    
    # Calculate the smoothed DM and TR over the period
    df['smoothed_TR'] = df['TR'].rolling(window=period).sum()
    df['smoothed_DM+'] = df['DM+'].rolling(window=period).sum()
    df['smoothed_DM-'] = df['DM-'].rolling(window=period).sum()

    # Calculate the Directional Indicators (+DI and -DI)
    df['DI+'] = 100 * (df['smoothed_DM+'] / df['smoothed_TR'])
    df['DI-'] = 100 * (df['smoothed_DM-'] / df['smoothed_TR'])
    
    # Calculate the DX (Directional Index)
    df['DX'] = 100 * abs(df['DI+'] - df['DI-']) / (df['DI+'] + df['DI-'])

    # Calculate ADX (average of DX over the period)
    df['ADX'] = df['DX'].rolling(window=period).mean()
    
    # Handle NaN values using forward fill and backward fill
    df.ffill(inplace=True)
    df.bfill(inplace=True)
    
    return df[['ADX', 'DI+', 'DI-']]

# Function to fetch historical price data and calculate ADX
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates ADX, +DI, and -DI.

    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.

    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data, ADX, +DI, and -DI.
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

        # Calculate ADX, +DI, and -DI
        df[['ADX', 'DI+', 'DI-']] = calculate_adx(df)

        logging.info(f"Historical data fetched with ADX, +DI, and -DI calculated for {stock_symbol} from {from_date} to {to_date}.")

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

    # Display the combined DataFrame with ADX, +DI, and -DI
    print(combined_df[['symbol', 'close', 'ADX', 'DI+', 'DI-']].head())  # Show key columns

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_ADX.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'ADX', 'DI+', 'DI-']].head())  # Show the first few rows with ADX, +DI, and -DI
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
