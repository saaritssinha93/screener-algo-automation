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

# Function to calculate MACD with more sensitive filters (Volume, Moving Averages, and Bollinger Bands)
def calculate_macd_with_filters(df, fast_period=9, slow_period=21, signal_period=5, sma_period=20, ema_period=10, bb_window=15, bb_std_dev=1.5):
    """
    Calculate MACD with more sensitive filters: Volume, Moving Averages, and Bollinger Bands.
    """
    # MACD calculation (with shorter periods for faster response)
    df['EMA_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
    df['EMA_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
    df['MACD_Line'] = df['EMA_fast'] - df['EMA_slow']
    df['Signal_Line'] = df['MACD_Line'].ewm(span=signal_period, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD_Line'] - df['Signal_Line']

    # Volume Filter: Identify volume spikes as 1.2 times the average volume for higher sensitivity
    df['avg_volume'] = df['volume'].rolling(window=15).mean()  # Reduced window for quicker volume changes
    df['volume_spike'] = np.where(df['volume'] > 1.2 * df['avg_volume'], 'volume_spike', 'normal_volume')

    # Simple Moving Average (SMA) Filter (shorter window for faster response)
    df['SMA'] = df['close'].rolling(window=sma_period).mean()

    # Exponential Moving Average (EMA) Filter (shorter window for quicker trend detection)
    df['EMA'] = df['close'].ewm(span=ema_period, adjust=False).mean()

    # Bollinger Bands (BB) with narrower bands (smaller window and std_dev for increased sensitivity)
    df['BB_Middle'] = df['close'].rolling(window=bb_window).mean()
    df['BB_Upper'] = df['BB_Middle'] + bb_std_dev * df['close'].rolling(window=bb_window).std()
    df['BB_Lower'] = df['BB_Middle'] - bb_std_dev * df['close'].rolling(window=bb_window).std()

    # Strategy Signal: MACD with sensitive filters (Volume spike, Price above SMA, Price near Bollinger Bands)
    df['MACD_Strategy_Signal'] = np.where(
        (df['MACD_Line'] > df['Signal_Line']) &  # Bullish MACD crossover
        (df['close'] > df['SMA']) &  # Price above SMA
        (df['volume_spike'] == 'volume_spike') &  # Confirmed by volume spike
        (df['close'] < df['BB_Upper']),  # Price below upper Bollinger Band
        'buy_signal',
        np.where(
            (df['MACD_Line'] < df['Signal_Line']) &  # Bearish MACD crossover
            (df['close'] < df['SMA']) &  # Price below SMA
            (df['volume_spike'] == 'volume_spike') &  # Confirmed by volume spike
            (df['close'] > df['BB_Lower']),  # Price above lower Bollinger Band
            'sell_signal',
            'neutral_signal'
        )
    )

    # Resolve NaN values using forward and backward fill
    df.ffill(inplace=True)  # Forward fill NaN values
    df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

    return df

# Function to fetch historical price data and apply MACD with sensitive filters
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and applies MACD with sensitive filters.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol

        # Apply MACD with sensitive filters (Volume, Moving Averages, Bollinger Bands)
        df = calculate_macd_with_filters(df)

        logging.info(f"Historical data fetched and indicators calculated for {stock_symbol} from {from_date} to {to_date}.")
        
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

    # Display the combined DataFrame with indicators
    print(combined_df[['symbol', 'close', 'MACD_Line', 'Signal_Line', 'MACD_Histogram', 'SMA', 'EMA', 'volume_spike', 'BB_Upper', 'BB_Lower', 'MACD_Strategy_Signal']].head())  # Show first few rows

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_macd_strategy.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'MACD_Line', 'Signal_Line', 'SMA', 'EMA', 'volume_spike', 'BB_Upper', 'BB_Lower', 'MACD_Strategy_Signal']].head())  # Show first few rows
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
