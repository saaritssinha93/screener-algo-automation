# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication without a scheduler.
"""

from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd

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

# Function to calculate Ultimate Oscillator with NaN handling
def calculate_ultimate_oscillator(df, short_period=7, medium_period=14, long_period=28):
    """
    Calculate the Ultimate Oscillator (UO) indicator and handle NaN values using forward and backward fill.
    
    Parameters:
    df (pd.DataFrame): DataFrame with historical data (must include 'close', 'high', 'low').
    short_period (int): Short period for UO calculation.
    medium_period (int): Medium period for UO calculation.
    long_period (int): Long period for UO calculation.
    
    Returns:
    pd.Series: Ultimate Oscillator values.
    """
    df['bp'] = df['close'] - df[['low', 'close']].min(axis=1)

    # Calculate True Range (TR)
    df['previous_close'] = df['close'].shift(1)
    df['tr'] = df[['high', 'low', 'previous_close']].apply(lambda x: max(x['high'] - x['low'], abs(x['high'] - x['previous_close']), abs(x['low'] - x['previous_close'])), axis=1)

    # Calculate average values for different periods
    avg_bp_short = df['bp'].rolling(window=short_period).sum()
    avg_tr_short = df['tr'].rolling(window=short_period).sum()
    avg_bp_medium = df['bp'].rolling(window=medium_period).sum()
    avg_tr_medium = df['tr'].rolling(window=medium_period).sum()
    avg_bp_long = df['bp'].rolling(window=long_period).sum()
    avg_tr_long = df['tr'].rolling(window=long_period).sum()

    # Calculate Ultimate Oscillator
    df['UO'] = 100 * ((4 * (avg_bp_short / avg_tr_short)) + (2 * (avg_bp_medium / avg_tr_medium)) + (avg_bp_long / avg_tr_long)) / (4 + 2 + 1)

    # Handle NaN values by applying forward fill and backward fill
    df.ffill(inplace=True)  # Forward fill NaN values
    df.bfill(inplace=True)  # Backward fill remaining NaN values

    return df['UO']

# Example usage in historical data fetching
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data and calculates Ultimate Oscillator.
    
    Parameters:
    kite (KiteConnect): KiteConnect session instance.
    stock_symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS').
    from_date (str): Start date in 'YYYY-MM-DD' format.
    to_date (str): End date in 'YYYY-MM-DD' format.
    interval (str): Interval of the data ('day', 'minute', '5minute', etc.). Default is 'day'.
    
    Returns:
    pd.DataFrame: A DataFrame with open, high, low, close, volume data and Ultimate Oscillator.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol

        # Calculate Ultimate Oscillator
        df['Ultimate_Oscillator'] = calculate_ultimate_oscillator(df)

        # Handle NaN values in the entire DataFrame
        df.ffill(inplace=True)
        df.bfill(inplace=True)

        logging.info(f"Historical data fetched and Ultimate Oscillator calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame
    print(combined_df[['symbol', 'close', 'Ultimate_Oscillator']].head())  # Show key columns

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_UO.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'Ultimate_Oscillator']].head())  # Show the first few rows of individual stock data
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV

