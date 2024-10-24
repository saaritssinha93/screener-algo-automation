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

# Function to calculate Bollinger Bands
def calculate_bollinger_bands(df, window=20, num_std_dev=2):
    """
    Calculate Bollinger Bands.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data.
    window (int): Rolling window size (default is 20).
    num_std_dev (int): Number of standard deviations for band calculation (default is 2).
    
    Returns:
    pd.DataFrame: Updated DataFrame with Bollinger Bands.
    """
    df['BB_Middle'] = df['close'].rolling(window=window).mean()
    df['BB_Std_Dev'] = df['close'].rolling(window=window).std()
    df['BB_Upper'] = df['BB_Middle'] + num_std_dev * df['BB_Std_Dev']
    df['BB_Lower'] = df['BB_Middle'] - num_std_dev * df['BB_Std_Dev']
    return df

# Function to detect Bollinger Band Divergence
def detect_bollinger_band_divergence(df):
    """
    Detect Bollinger Band Divergence: 
    - Bullish divergence: Price makes lower lows, but the lower Bollinger Band does not.
    - Bearish divergence: Price makes higher highs, but the upper Bollinger Band does not.
    
    Parameters:
    df (pd.DataFrame): DataFrame with Bollinger Bands and price data.
    
    Returns:
    pd.DataFrame: Updated DataFrame with Bollinger Band Divergence flags.
    """
    df['BB_Divergence'] = 'No Divergence'
    
    for i in range(2, len(df)):
        # Bullish Divergence (Price lower lows, Bollinger Lower Band doesn't make a lower low)
        if df['close'][i] < df['close'][i-1] and df['close'][i-1] < df['close'][i-2]:
            if df['BB_Lower'][i] >= df['BB_Lower'][i-1]:
                df.loc[i, 'BB_Divergence'] = 'Bullish Divergence'

        # Bearish Divergence (Price higher highs, Bollinger Upper Band doesn't make a higher high)
        elif df['close'][i] > df['close'][i-1] and df['close'][i-1] > df['close'][i-2]:
            if df['BB_Upper'][i] <= df['BB_Upper'][i-1]:
                df.loc[i, 'BB_Divergence'] = 'Bearish Divergence'

    return df

# Function to fetch historical price data and calculate Bollinger Band Divergence
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates Bollinger Band Divergence.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with Bollinger Bands and Bollinger Band Divergence.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol

        # Calculate Bollinger Bands
        df = calculate_bollinger_bands(df)

        # Detect Bollinger Band Divergence
        df = detect_bollinger_band_divergence(df)

        # Preprocess NaN values
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        logging.info(f"Historical data fetched and Bollinger Band Divergence calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with Bollinger Band Divergence
    print(combined_df[['symbol', 'close', 'BB_Upper', 'BB_Lower', 'BB_Divergence']].head())  # Show the first few rows with Bollinger Band Divergence

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_bollinger_band_divergence.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'BB_Upper', 'BB_Lower', 'BB_Divergence']].head())  # Show the first few rows of individual stock data with Bollinger Band Divergence
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
