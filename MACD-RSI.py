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

# Function to calculate RSI using Exponential Weighted Moving Average (EWM)
def calculate_rsi(df, n=14):
    """Calculate RSI using Exponential Weighted Moving Average (EWM)."""
    df['change'] = df['close'].diff()
    df['gain'] = np.where(df['change'] > 0, df['change'], 0)
    df['loss'] = np.where(df['change'] < 0, -df['change'], 0)
    df['avg_gain'] = df['gain'].ewm(alpha=1/n, min_periods=n).mean()
    df['avg_loss'] = df['loss'].ewm(alpha=1/n, min_periods=n).mean()
    df['rs'] = df['avg_gain'] / df['avg_loss']
    df['rsi'] = 100 - (100 / (1 + df['rs']))
    return df['rsi']

# Function to detect RSI divergence
def find_rsi_divergence(price_data, rsi_data):
    """
    Function to detect RSI divergence.
    Detects bullish and bearish divergence between price and RSI.
    """
    if len(price_data) < 3 or len(rsi_data) < 3:
        return 'no_divergence'

    # Find local peaks and troughs in price and RSI
    price_highs = (price_data.shift(1) < price_data) & (price_data.shift(-1) < price_data)
    price_lows = (price_data.shift(1) > price_data) & (price_data.shift(-1) > price_data)

    rsi_highs = (rsi_data.shift(1) < rsi_data) & (rsi_data.shift(-1) < rsi_data)
    rsi_lows = (rsi_data.shift(1) > rsi_data) & (rsi_data.shift(-1) > rsi_data)

    # Check for bearish divergence
    if price_highs.iloc[-3:].sum() > 0 and rsi_highs.iloc[-3:].sum() > 0:
        recent_price_high = price_data[price_highs].iloc[-1]
        previous_price_high = price_data[price_highs].iloc[-2]
        recent_rsi_high = rsi_data[rsi_highs].iloc[-1]
        previous_rsi_high = rsi_data[rsi_highs].iloc[-2]

        if recent_price_high > previous_price_high and recent_rsi_high < previous_rsi_high:
            return 'bearish_divergence'

    # Check for bullish divergence
    if price_lows.iloc[-3:].sum() > 0 and rsi_lows.iloc[-3:].sum() > 0:
        recent_price_low = price_data[price_lows].iloc[-1]
        previous_price_low = price_data[price_lows].iloc[-2]
        recent_rsi_low = rsi_data[rsi_lows].iloc[-1]
        previous_rsi_low = rsi_data[rsi_lows].iloc[-2]

        if recent_price_low < previous_price_low and recent_rsi_low > previous_rsi_low:
            return 'bullish_divergence'

    return 'no_divergence'

# Function to calculate MACD and combine with RSI
def calculate_macd_rsi(df, fast_period=12, slow_period=26, signal_period=9, rsi_period=14):
    """
    Calculate MACD, RSI, and detect MACD-RSI signals.
    """
    # MACD calculation
    df['EMA_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
    df['EMA_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
    df['MACD_Line'] = df['EMA_fast'] - df['EMA_slow']
    df['Signal_Line'] = df['MACD_Line'].ewm(span=signal_period, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD_Line'] - df['Signal_Line']

    # RSI calculation
    df['RSI'] = calculate_rsi(df, rsi_period)

    # Detect MACD-RSI combined signals (both indicators show bullish or bearish momentum)
    df['MACD_RSI_Signal'] = np.where(
        (df['MACD_Line'] > df['Signal_Line']) & (df['RSI'] > 50), 'bullish_macd_rsi',
        np.where((df['MACD_Line'] < df['Signal_Line']) & (df['RSI'] < 50), 'bearish_macd_rsi', 'neutral_macd_rsi')
    )

    # Resolve NaN values using forward and backward fill
    df.ffill(inplace=True)  # Forward fill NaN values
    df.bfill(inplace=True)  # Backward fill for remaining NaNs (edge cases)

    return df

# Function to fetch historical price data and calculate indicators
def fetch_historical_data(kite, stock_symbol, from_date, to_date, interval='day'):
    """
    Fetches historical price data for a stock using Zerodha KiteConnect API and calculates indicators.
    """
    try:
        # Fetch instrument token for the stock symbol
        instrument_token = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]['instrument_token']

        # Fetch historical data from Kite API
        historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(historical_data)
        df['symbol'] = stock_symbol  # Add a column for the stock symbol

        # Calculate MACD, RSI, and combined signals
        df = calculate_macd_rsi(df)

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
    print(combined_df[['symbol', 'close', 'RSI', 'MACD_Line', 'Signal_Line', 'MACD_Histogram', 'MACD_RSI_Signal']].head())  # Show first few rows

    # Save the combined data to a CSV file
    combined_df.to_csv("combined_historical_data_with_macd_rsi.csv", index=False)

    # Display individual DataFrames for each stock
    for stock, df in stock_data.items():
        print(f"\nData for {stock.replace('_df', '')}:")
        print(df[['close', 'RSI', 'MACD_Line', 'Signal_Line', 'MACD_Histogram', 'MACD_RSI_Signal']].head())  # Show first few rows
        df.to_csv(f"{stock}.csv", index=False)  # Save each individual DataFrame to a separate CSV
