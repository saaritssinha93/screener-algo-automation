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

# Function to calculate Vortex Indicator (VI)
def calculate_vortex_indicator(df, period=14):
    """
    Calculate Vortex Indicator (VI).
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing stock data with 'high', 'low', and 'close' columns.
    period (int): The period over which to calculate the VI (default 14).
    
    Returns:
    pd.DataFrame: A DataFrame with the VI+ and VI- values.
    """
    # Calculate the True Range (TR)
    df['TR'] = pd.concat([df['high'] - df['low'], 
                          abs(df['high'] - df['close'].shift(1)), 
                          abs(df['low'] - df['close'].shift(1))], axis=1).max(axis=1)

    # Calculate the positive and negative Vortex movements
    df['VM+'] = abs(df['high'] - df['low'].shift(1))
    df['VM-'] = abs(df['low'] - df['high'].shift(1))

    # Sum the TR and Vortex movements over the period
    df['sum_TR'] = df['TR'].rolling(window=period).sum()
    df['sum_VM+'] = df['VM+'].rolling(window=period).sum()
    df['sum_VM-'] = df['VM-'].rolling(window=period).sum()

    # Calculate the Vortex Indicator
    df['VI+'] = df['sum_VM+'] / df['sum_TR']
    df['VI-'] = df['sum_VM-'] / df['sum_TR']

    # Handle NaN values using forward fill and backward fill
    df.ffill(inplace=True)
    df.bfill(inplace=True)

    # Return only the Vortex Indicator columns
    return df[['VI+', 'VI-']]

# Function to fetch historical price data and calculate VI
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates VI.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data, and VI+ and VI-.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol
        
        # Preprocess NaN values in the historical data
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill remaining NaNs (edge cases)

        # Calculate Vortex Indicator (VI+ and VI-)
        df[['VI+', 'VI-']] = calculate_vortex_indicator(df)

        logging.info(f"Historical data fetched with VI calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with VI+ and VI-
    print(combined_df[['symbol', 'close', 'VI+', 'VI-']].head())  # Show key columns

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_VI.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'VI+', 'VI-']].head())  # Show the first few rows with VI+ and VI-
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
