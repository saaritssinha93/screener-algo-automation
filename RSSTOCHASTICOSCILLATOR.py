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

# Function to fetch historical price data and calculate Stochastic Oscillator
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day', k_window=14, d_window=3):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates the Stochastic Oscillator.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    k_window (int): Window size for %K calculation (default 14).
    d_window (int): Window size for %D calculation (default 3).
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data, Stochastic %K and %D.
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

        logging.info(f"Historical data fetched and Stochastic Oscillator calculated for {stock_symbol} from {from_date} to {to_date}.")
        
        return df

    except Exception as e:
        logging.error(f"Error fetching historical data for {stock_symbol}: {e}")
        raise

# Function to calculate RSI using Exponential Weighted Moving Average (EWM)
def RSI(DF, n=14):
    """Function to calculate RSI using Exponential Weighted Moving Average (EWM)"""
    df = DF.copy()
    
    # Calculating changes in 'close' prices
    df['change'] = df['close'].diff()
    
    # Calculating gains and losses
    df['gain'] = np.where(df['change'] > 0, df['change'], 0)
    df['loss'] = np.where(df['change'] < 0, -df['change'], 0)
    
    # Calculate Exponential Moving Averages of gains and losses using EWM
    df['avgGain'] = df['gain'].ewm(alpha=1/n, min_periods=n).mean()
    df['avgLoss'] = df['loss'].ewm(alpha=1/n, min_periods=n).mean()

    # Calculate Relative Strength (RS)
    df['rs'] = df['avgGain'] / df['avgLoss']
    
    # Calculate RSI based on RS
    df['rsi'] = 100 - (100 / (1 + df['rs']))
    
    return df['rsi']

# Function to calculate RS Stochastic Oscillator
def calculate_rs_stochastic_oscillator(df, rsi_window=14, k_window=14, d_window=3):
    """
    Calculate the RS Stochastic Oscillator (%K and %D based on RSI).
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'close').
    rsi_window (int): Period for RSI calculation (default 14).
    k_window (int): Window size for RS Stochastic %K calculation (default 14).
    d_window (int): Window size for RS Stochastic %D calculation (default 3).
    
    Returns:
    pd.DataFrame: DataFrame with RS Stochastic %K and %D columns.
    """
    df = df.copy()

    # Step 1: Calculate RSI
    df['RSI'] = RSI(df, n=rsi_window)

    # Step 2: Calculate Stochastic %K of RSI
    df['RSI_low'] = df['RSI'].rolling(window=k_window).min()
    df['RSI_high'] = df['RSI'].rolling(window=k_window).max()
    df['%K_RS'] = 100 * ((df['RSI'] - df['RSI_low']) / (df['RSI_high'] - df['RSI_low']))

    # Step 3: Calculate Stochastic %D (SMA of %K_RS)
    df['%D_RS'] = df['%K_RS'].rolling(window=d_window).mean()

    return df[['RSI', '%K_RS', '%D_RS']]

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
        
        # Calculate the RS Stochastic Oscillator for each stock
        rs_stoch_df = calculate_rs_stochastic_oscillator(df)
        df = pd.concat([df, rs_stoch_df], axis=1)

        # Preprocess NaN values using ffill and bfill directly
        df.ffill(inplace=True)  # Forward fill NaN values
        df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

        stock_data[f"{share}_df"] = df  # Save individual stock DataFrame (e.g., HDFCBANK_df, TCS_df)
        all_data.append(df)  # Add the DataFrame to the list for combined data

    # Concatenate all DataFrames into one combined DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)  # Store the combined DataFrame in memory as 'combined_df'

    # Display the combined DataFrame with RS Stochastic Oscillator (%K_RS, %D_RS)
    print("Combined DataFrame with RS Stochastic Oscillator (combined_df):")
    print(combined_df[['symbol', 'close', 'RSI', '%K_RS', '%D_RS']].head())  # Show the first few rows with RSI, %K_RS, and %D_RS

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_rs_stochastic.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'RSI', '%K_RS', '%D_RS']].head())  # Show the first few rows of individual stock data with RSI, %K_RS, %D_RS
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
