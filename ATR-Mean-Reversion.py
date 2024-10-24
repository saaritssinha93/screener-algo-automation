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

# Function to calculate ATR (Average True Range)
def calculate_atr(df, atr_window=14):
    """
    Calculate ATR (Average True Range).
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing stock data with 'high', 'low', 'close' columns.
    atr_window (int): The window size for ATR calculation (default 14).
    
    Returns:
    pd.Series: A Series representing the ATR values.
    """
    # Calculate True Range (TR)
    df['high-low'] = df['high'] - df['low']
    df['high-close_prev'] = abs(df['high'] - df['close'].shift(1))
    df['low-close_prev'] = abs(df['low'] - df['close'].shift(1))
    
    df['TR'] = df[['high-low', 'high-close_prev', 'low-close_prev']].max(axis=1)
    
    # Calculate ATR (Average True Range)
    ATR = df['TR'].rolling(window=atr_window, min_periods=1).mean()
    
    return ATR

# Function to use ATR as a Mean-Reversion Indicator
def atr_mean_reversion(df, atr_multiplier=1.5):
    """
    Use ATR as a mean-reversion indicator.
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing stock data with 'close' and 'ATR' columns.
    atr_multiplier (float): The multiplier to apply on the ATR to detect extreme levels (default 1.5).
    
    Returns:
    pd.DataFrame: A DataFrame with mean-reversion signals ('buy_signal', 'sell_signal').
    """
    # Calculate mean of the closing price
    mean_price = df['close'].rolling(window=14).mean()
    
    # Define buy/sell thresholds based on ATR
    df['buy_signal'] = (df['close'] < mean_price - atr_multiplier * df['ATR']).astype(int)
    df['sell_signal'] = (df['close'] > mean_price + atr_multiplier * df['ATR']).astype(int)
    
    return df

# Function to fetch historical price data and apply ATR as a mean-reversion indicator
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day', atr_window=14, atr_multiplier=1.5):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and applies ATR-based mean-reversion strategy.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    atr_window (int): Window size for ATR calculation (default 14).
    atr_multiplier (float): Multiplier for ATR to trigger mean-reversion signals (default 1.5).
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data, ATR, buy/sell signals for mean reversion.
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

        # Calculate ATR
        df['ATR'] = calculate_atr(df, atr_window)

        # Apply ATR as a mean-reversion indicator
        df = atr_mean_reversion(df, atr_multiplier)

        logging.info(f"Historical data fetched with ATR-based mean-reversion signals for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with ATR-based mean-reversion signals
    print(combined_df[['symbol', 'close', 'ATR', 'buy_signal', 'sell_signal']].head())  # Show key columns

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_ATR_mean_reversion.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'ATR', 'buy_signal', 'sell_signal']].head())  # Show the first few rows with ATR-based signals
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
