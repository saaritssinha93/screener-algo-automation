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

# Function to calculate Moving Average Crossovers
def calculate_moving_average_crossover(df, short_window=50, long_window=200):
    """
    Calculate Moving Average Crossovers between a short-term and long-term moving average.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data.
    short_window (int): Short window for the moving average (default is 50).
    long_window (int): Long window for the moving average (default is 200).
    
    Returns:
    pd.DataFrame: Updated DataFrame with Moving Averages and crossover signals.
    """
    # Calculate Short-Term Moving Average (e.g., 50-period MA)
    df['MA_Short'] = df['close'].rolling(window=short_window).mean()

    # Calculate Long-Term Moving Average (e.g., 200-period MA)
    df['MA_Long'] = df['close'].rolling(window=long_window).mean()

    # Detect crossovers
    df['Crossover_Signal'] = np.where((df['MA_Short'] > df['MA_Long']) & (df['MA_Short'].shift(1) <= df['MA_Long'].shift(1)), 'Bullish Crossover',
                                      np.where((df['MA_Short'] < df['MA_Long']) & (df['MA_Short'].shift(1) >= df['MA_Long'].shift(1)), 'Bearish Crossover', 'No Crossover'))

    return df

# Function to fetch historical price data and calculate Bollinger Bands with Moving Average Crossovers
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates Bollinger Bands with Moving Average Crossovers.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with Bollinger Bands and Moving Average Crossovers.
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

        # Calculate Moving Averages and detect crossovers
        df = calculate_moving_average_crossover(df)

        # Preprocess NaN values
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        logging.info(f"Historical data fetched and Bollinger Bands with Moving Average Crossovers calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with Bollinger Bands and Moving Average Crossovers
    print(combined_df[['symbol', 'close', 'BB_Upper', 'BB_Lower', 'MA_Short', 'MA_Long', 'Crossover_Signal']].head())  # Show the first few rows with Bollinger Bands and crossovers

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_bollinger_bands_ma_crossovers.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'BB_Upper', 'BB_Lower', 'MA_Short', 'MA_Long', 'Crossover_Signal']].head())  # Show the first few rows of individual stock data with Bollinger Bands and crossovers
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
