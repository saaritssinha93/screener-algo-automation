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

# Function to calculate ATR Trailing Stop
def calculate_atr_trailing_stop(df, atr_multiplier=3, window=14):
    """
    Calculate the ATR Trailing Stop based on ATR values.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'close', 'high', 'low').
    atr_multiplier (float): The multiplier applied to ATR for setting stop levels (default is 3).
    window (int): The window size for ATR calculation (default is 14).
    
    Returns:
    pd.DataFrame: Updated DataFrame with ATR Trailing Stop for long and short positions.
    """
    df['ATR'] = calculate_atr(df, window=window)

    # Initialize columns for the trailing stops
    df['ATR_Trailing_Stop_Long'] = np.nan
    df['ATR_Trailing_Stop_Short'] = np.nan

    # Set initial stop values for long and short positions using .loc to avoid chained assignment
    for i in range(1, len(df)):
        # For long positions (stop below price)
        df.loc[i, 'ATR_Trailing_Stop_Long'] = df.loc[i, 'close'] - (atr_multiplier * df.loc[i, 'ATR'])
        
        # For short positions (stop above price)
        df.loc[i, 'ATR_Trailing_Stop_Short'] = df.loc[i, 'close'] + (atr_multiplier * df.loc[i, 'ATR'])

    return df


# Function to fetch historical price data and calculate ATR Trailing Stop
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates ATR Trailing Stop.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with ATR Trailing Stop for long and short positions.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol

        # Calculate ATR Trailing Stop
        df = calculate_atr_trailing_stop(df)

        # Preprocess NaN values
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        logging.info(f"Historical data fetched and ATR Trailing Stop calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with ATR Trailing Stops
    print(combined_df[['symbol', 'close', 'ATR_Trailing_Stop_Long', 'ATR_Trailing_Stop_Short']].head())  # Show the first few rows with ATR Trailing Stops

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_atr_trailing_stop.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'ATR_Trailing_Stop_Long', 'ATR_Trailing_Stop_Short']].head())  # Show the first few rows of individual stock data with ATR Trailing Stops
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV

