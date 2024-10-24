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

# Function to calculate Keltner Channels
def calculate_keltner_channels(df, ema_window=20, atr_window=20, atr_multiplier=1.5):
    """
    Calculate Keltner Channels using EMA and ATR.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data.
    ema_window (int): EMA window size (default is 20).
    atr_window (int): ATR window size (default is 20).
    atr_multiplier (float): Multiplier for ATR to set the channel width (default is 1.5).
    
    Returns:
    pd.DataFrame: Updated DataFrame with Keltner Channels.
    """
    # Calculate EMA
    df['KC_Middle'] = df['close'].ewm(span=ema_window, adjust=False).mean()

    # Calculate ATR (Average True Range)
    df['High-Low'] = df['high'] - df['low']
    df['High-Close_Prev'] = np.abs(df['high'] - df['close'].shift(1))
    df['Low-Close_Prev'] = np.abs(df['low'] - df['close'].shift(1))
    df['True_Range'] = df[['High-Low', 'High-Close_Prev', 'Low-Close_Prev']].max(axis=1)
    df['ATR'] = df['True_Range'].rolling(window=atr_window).mean()

    # Calculate Keltner Channel upper and lower bands
    df['KC_Upper'] = df['KC_Middle'] + atr_multiplier * df['ATR']
    df['KC_Lower'] = df['KC_Middle'] - atr_multiplier * df['ATR']
    return df

# Function to calculate the Bollinger-Keltner Squeeze
def calculate_bollinger_keltner_squeeze(df):
    """
    Identify Bollinger-Keltner Squeeze.
    
    Parameters:
    df (pd.DataFrame): DataFrame with Bollinger Bands and Keltner Channels.
    
    Returns:
    pd.DataFrame: Updated DataFrame with the Bollinger-Keltner Squeeze condition.
    """
    # Identify when Bollinger Bands are within the Keltner Channels (squeeze condition)
    df['Squeeze'] = np.where(
        (df['BB_Upper'] < df['KC_Upper']) & (df['BB_Lower'] > df['KC_Lower']), 
        'squeeze', 
        'no_squeeze'
    )
    return df

# Function to fetch historical price data and calculate Bollinger-Keltner Squeeze
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates the 
    Bollinger-Keltner Squeeze.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with Bollinger Bands, Keltner Channels, and Squeeze condition.
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

        # Calculate Keltner Channels
        df = calculate_keltner_channels(df)

        # Identify Bollinger-Keltner Squeeze
        df = calculate_bollinger_keltner_squeeze(df)

        # Preprocess NaN values
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        logging.info(f"Historical data fetched and Bollinger-Keltner Squeeze calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with Bollinger-Keltner Squeeze
    print(combined_df[['symbol', 'close', 'BB_Upper', 'BB_Lower', 'KC_Upper', 'KC_Lower', 'Squeeze']].head())  # Show the first few rows with Bollinger-Keltner Squeeze

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_bollinger_keltner_squeeze.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'BB_Upper', 'BB_Lower', 'KC_Upper', 'KC_Lower', 'Squeeze']].head())  # Show the first few rows of individual stock data with Bollinger-Keltner Squeeze
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
