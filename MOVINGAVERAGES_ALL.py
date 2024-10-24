# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication with various moving averages.
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

# Function to calculate Simple Moving Average (SMA)
def calculate_sma(df, window):
    return df['close'].rolling(window=window).mean()

# Function to calculate Exponential Moving Average (EMA)
def calculate_ema(df, window):
    return df['close'].ewm(span=window, adjust=False).mean()

# Function to calculate Weighted Moving Average (WMA)
def calculate_wma(df, window):
    weights = np.arange(1, window + 1)
    return df['close'].rolling(window=window).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

# Function to calculate Hull Moving Average (HMA)
def calculate_hma(df, window):
    half_window = int(window / 2)
    sqrt_window = int(np.sqrt(window))
    wma_half = calculate_wma(df, half_window)
    wma_full = calculate_wma(df, window)
    
    hma = 2 * wma_half - wma_full
    return hma.rolling(window=sqrt_window).mean()

# Function to calculate Smoothed Moving Average (SMMA)
def calculate_smma(df, window):
    return df['close'].ewm(alpha=1/window, adjust=False).mean()

# Function to calculate Triangular Moving Average (TMA)
def calculate_tma(df, window):
    sma = calculate_sma(df, window)
    return sma.rolling(window=window).mean()

# Function to calculate Double Exponential Moving Average (DEMA)
def calculate_dema(df, window):
    ema = calculate_ema(df, window)
    ema_of_ema = ema.ewm(span=window, adjust=False).mean()
    return 2 * ema - ema_of_ema

# Function to calculate Triple Exponential Moving Average (TEMA)
def calculate_tema(df, window):
    ema = calculate_ema(df, window)
    dema = calculate_dema(df, window)
    ema_of_dema = dema.ewm(span=window, adjust=False).mean()
    return 3 * ema - 3 * dema + ema_of_dema

# Function to calculate Variable Moving Average (VMA)
def calculate_vma(df, window):
    volatility = df['close'].rolling(window=window).std()
    vma = df['close'].rolling(window=window).mean() + volatility
    return vma

# Function to calculate Kaufman Adaptive Moving Average (KAMA)
def calculate_kama(df, window, fast=2, slow=30):
    """
    Calculate the Kaufman Adaptive Moving Average (KAMA).
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'close').
    window (int): Period for the KAMA calculation.
    fast (int): Fastest smoothing constant (default 2).
    slow (int): Slowest smoothing constant (default 30).
    
    Returns:
    pd.Series: KAMA values.
    """
    df = df.copy()

    # Step 1: Calculate the change (absolute difference between current close and close from 'window' days ago)
    change = abs(df['close'] - df['close'].shift(window))

    # Step 2: Calculate the volatility (sum of absolute changes over 'window' period)
    volatility = df['close'].diff(1).abs().rolling(window).sum()

    # Step 3: Calculate the efficiency ratio (ER)
    efficiency_ratio = change / volatility

    # Step 4: Calculate the smoothing constant
    fast_sc = 2 / (fast + 1)
    slow_sc = 2 / (slow + 1)

    smoothing_constant = (efficiency_ratio * (fast_sc - slow_sc) + slow_sc) ** 2

    # Step 5: Initialize KAMA with the first 'window' periods of the 'close' price
    kama = pd.Series(index=df.index, dtype=float)
    kama.iloc[window] = df['close'].iloc[window]  # Initialize the first value of KAMA

    # Step 6: Calculate KAMA iteratively for each data point
    for i in range(window + 1, len(df)):
        kama.iloc[i] = kama.iloc[i-1] + smoothing_constant.iloc[i] * (df['close'].iloc[i] - kama.iloc[i-1])

    return kama


# Function to calculate Least Squares Moving Average (LSMA)
def calculate_lsma(df, window):
    return df['close'].rolling(window).apply(lambda x: np.polyfit(np.arange(len(x)), x, 1)[0] * (len(x) - 1) + np.polyfit(np.arange(len(x)), x, 1)[1])

# Function to fetch historical price data and calculate various moving averages
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates various moving averages.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with various moving averages.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol

        # Calculate moving averages
        df['SMA_50'] = calculate_sma(df, 50)
        df['EMA_50'] = calculate_ema(df, 50)
        df['WMA_50'] = calculate_wma(df, 50)
        df['HMA_50'] = calculate_hma(df, 50)
        df['SMMA_50'] = calculate_smma(df, 50)
        df['TMA_50'] = calculate_tma(df, 50)
        df['DEMA_50'] = calculate_dema(df, 50)
        df['TEMA_50'] = calculate_tema(df, 50)
        df['VMA_50'] = calculate_vma(df, 50)
        df['KAMA_50'] = calculate_kama(df, 50)
        df['LSMA_50'] = calculate_lsma(df, 50)

        # Preprocess NaN values
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        logging.info(f"Historical data fetched and moving averages calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with Moving Averages
    print(combined_df[['symbol', 'close', 'SMA_50', 'EMA_50']].head())  # Show the first few rows with MAs

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_moving_averages.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'SMA_50', 'EMA_50']].head())  # Show the first few rows of individual stock data with MAs
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
