# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication without a scheduler.
"""

import time
from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd
import numpy as np
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

# Stocks to analyze
sys.path.append('C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation')
from et1_stock_tickers_test import shares

# Generate trading session
try:
    with open("access_token.txt", 'r') as token_file:
        access_token = token_file.read().strip()

    with open("api_key.txt", 'r') as key_file:
        key_secret = key_file.read().split()

    kite = KiteConnect(api_key=key_secret[0])
    kite.set_access_token(access_token)
    logging.info("Kite session established successfully.")

except FileNotFoundError as e:
    logging.error(f"File not found: {e}")
    raise
except Exception as e:
    logging.error(f"Error setting up Kite session: {e}")
    raise

# Get dump of all NSE instruments
try:
    instrument_dump = kite.instruments("NSE")
    instrument_df = pd.DataFrame(instrument_dump)
    logging.info("NSE instrument data fetched successfully.")
    
except Exception as e:
    logging.error(f"Error fetching instruments: {e}")
    raise

# Function to lookup instrument token
def instrument_lookup(instrument_df, symbol):
    """Looks up instrument token for a given symbol in the instrument dump."""
    try:
        instrument_token = instrument_df[instrument_df.tradingsymbol == symbol].instrument_token.values[0]
        return instrument_token
    except IndexError:
        logging.error(f"Symbol {symbol} not found in instrument dump.")
        return -1
    except Exception as e:
        logging.error(f"Error in instrument lookup: {e}")
        return -1

# Function to fetch OHLC data
def fetch_ohlc(ticker, interval, start_date, end_date):
    """Extracts historical OHLC data for a specific date range and returns it as a DataFrame."""
    try:
        instrument = instrument_lookup(instrument_df, ticker)
        if instrument == -1:
            raise ValueError(f"Instrument lookup failed for ticker {ticker}")

        # Fetch historical data for the given date range
        data = pd.DataFrame(
            kite.historical_data(
                instrument, 
                start_date, 
                end_date, 
                interval
            )
        )

        if not data.empty:
            data.set_index("date", inplace=True)
            return data
        else:
            print(f"No data returned for {ticker}")  # Simplified message for no data
            return pd.DataFrame()

    except Exception as e:
        print(f"Error fetching OHLC data for {ticker}: {e}")  # Reduced logging to print
        return None

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

# Initialize a list to store results
results = []

# Loop through each stock in the shares list
for ticker in shares:
    end_date = dt.datetime.today()  # Use the current date as the end date
    start_date = end_date - dt.timedelta(days=180)  # 6 months ago (approximately 180 days)
    
    # Fetch OHLC data for the current ticker
    ohlc_data = fetch_ohlc(ticker, 'day', start_date, end_date)
    
    if ohlc_data is not None and not ohlc_data.empty:
        # Calculate RSI
        ohlc_data['RSI'] = RSI(ohlc_data)
        
        if 'RSI' in ohlc_data.columns:
            current_rsi = ohlc_data['RSI'].iloc[-1]  # Get the latest RSI value
            
            # Append the results to the list
            results.append({
                'Ticker': ticker,
                'Last Close Price': ohlc_data['close'].iloc[-1],
                'Current Price': ohlc_data['close'].iloc[-1],
                'RSI': current_rsi
            })
        else:
            print(f"RSI calculation did not produce expected results for {ticker}.")
    else:
        print(f"OHLC data is empty or None for {ticker}.")

# Create a DataFrame from the results list
results_df = pd.DataFrame(results)

# Store the results in an output CSV file
output_csv_file = 'output.csv'
results_df.to_csv(output_csv_file, index=False)

print(f"RSI values stored in {output_csv_file}.")
def select_stocks_with_rsi_above_50(kite, instrument_df, shares, interval='day', days=180, rsi_threshold=40):
    """
    Select stocks with RSI greater than 50 and store them in a file 'et1_select_stocklist.py'.
    
    Args:
    - kite (KiteConnect): Kite Connect instance for fetching live prices.
    - instrument_df (pd.DataFrame): DataFrame containing instrument information.
    - shares (list): List of stock tickers.
    - interval (str): Interval for OHLC data (default is 'day').
    - days (int): Number of days for fetching historical data (default is 180).
    - rsi_threshold (float): The RSI threshold (default is 50).
    
    Returns:
    - selected_stocks (list): List of stock tickers with RSI > rsi_threshold.
    """
    selected_stocks = []
    end_date = dt.datetime.today()
    start_date = end_date - dt.timedelta(days=days)
    
    for ticker in shares:
        ohlc_data = fetch_ohlc(ticker, interval, start_date, end_date)
        
        if ohlc_data is not None and not ohlc_data.empty:
            ohlc_data['RSI'] = RSI(ohlc_data)
            current_rsi = ohlc_data['RSI'].iloc[-1]  # Get the latest RSI value
            
            if current_rsi > rsi_threshold:
                selected_stocks.append(ticker)
                print(f"Selected stock: {ticker} with RSI: {current_rsi}")
    
    # Save the selected stocks to a file in the required format
    with open('et1_select_stocklist.py', 'w') as f:
        f.write("shares = [\n")
        for stock in selected_stocks:
            f.write(f"    '{stock}',\n")
        f.write("]\n")
    
    print("Selected stocks written to 'et1_select_stocklist.py'.")

    return selected_stocks


selected_stocks = select_stocks_with_rsi_above_50(kite, instrument_df, shares)