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

# Function to calculate Connors RSI
def calculate_connors_rsi(df, rsi_period=3, streak_rsi_period=2, roc_period=100):
    """
    Calculate Connors RSI, which is a composite of three indicators: RSI, Streak Length, and Rate of Change (ROC).
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing stock data with 'close' column.
    rsi_period (int): The period for the RSI component (default 3).
    streak_rsi_period (int): The period for the streak RSI component (default 2).
    roc_period (int): The period for the rate of change (ROC) component (default 100).
    
    Returns:
    pd.DataFrame: A DataFrame with Connors RSI values.
    """
    # Standard RSI
    delta = df['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()
    
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Streak RSI (Streak Length)
    df['streak'] = 0
    for i in range(1, len(df)):
        if df.loc[i, 'close'] > df.loc[i-1, 'close']:
            df.loc[i, 'streak'] = df.loc[i-1, 'streak'] + 1
        elif df.loc[i, 'close'] < df.loc[i-1, 'close']:
            df.loc[i, 'streak'] = df.loc[i-1, 'streak'] - 1
        else:
            df.loc[i, 'streak'] = 0

    delta_streak = df['streak'].diff(1)
    gain_streak = delta_streak.where(delta_streak > 0, 0)
    loss_streak = -delta_streak.where(delta_streak < 0, 0)
    
    avg_gain_streak = gain_streak.rolling(window=streak_rsi_period).mean()
    avg_loss_streak = loss_streak.rolling(window=streak_rsi_period).mean()
    
    rs_streak = avg_gain_streak / avg_loss_streak
    df['Streak_RSI'] = 100 - (100 / (1 + rs_streak))
    
    # Rate of Change (ROC)
    df['ROC'] = ((df['close'] - df['close'].shift(roc_period)) / df['close'].shift(roc_period)) * 100
    
    # Connors RSI is the average of the three components
    df['Connors_RSI'] = (df['RSI'] + df['Streak_RSI'] + df['ROC']) / 3
    
    # Handle NaN values using forward fill and backward fill
    df.ffill(inplace=True)
    df.bfill(inplace=True)

    return df[['Connors_RSI']]

# Function to fetch historical price data and calculate Connors RSI
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates Connors RSI.

    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.

    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data, and Connors RSI values.
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

        # Calculate Connors RSI
        df['Connors_RSI'] = calculate_connors_rsi(df)

        logging.info(f"Historical data fetched with Connors RSI calculated for {stock_symbol} from {from_date} to {to_date}.")

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

    # Display the combined DataFrame with Connors RSI
    print(combined_df[['symbol', 'close', 'Connors_RSI']].head())  # Show key columns

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_Connors_RSI.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'Connors_RSI']].head())  # Show the first few rows with Connors RSI
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
