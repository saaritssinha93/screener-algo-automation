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
from et1_select_stocklist import shares

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

import pandas as pd
import numpy as np

def find_divergence(price_data, rsi_data):
    """
    Function to detect RSI divergence.
    Looks for price making higher highs or lower lows while RSI makes lower highs or higher lows.
    
    Args:
        price_data (pd.Series): Series of closing prices.
        rsi_data (pd.Series): Series of RSI values.
    
    Returns:
        str: 'bullish_divergence', 'bearish_divergence', or 'no_divergence'.
    """
    if len(price_data) < 3 or len(rsi_data) < 3:
        return 'no_divergence'

    # Find local peaks and troughs in price
    price_highs = (price_data.shift(1) < price_data) & (price_data.shift(-1) < price_data)
    price_lows = (price_data.shift(1) > price_data) & (price_data.shift(-1) > price_data)

    # Find local peaks and troughs in RSI
    rsi_highs = (rsi_data.shift(1) < rsi_data) & (rsi_data.shift(-1) < rsi_data)
    rsi_lows = (rsi_data.shift(1) > rsi_data) & (rsi_data.shift(-1) > rsi_data)

    # Check for bearish divergence (price higher highs, RSI lower highs)
    if price_highs.iloc[-3:].sum() > 0 and rsi_highs.iloc[-3:].sum() > 0:
        recent_price_high = price_data[price_highs].iloc[-1]
        previous_price_high = price_data[price_highs].iloc[-2]
        recent_rsi_high = rsi_data[rsi_highs].iloc[-1]
        previous_rsi_high = rsi_data[rsi_highs].iloc[-2]

        if recent_price_high > previous_price_high and recent_rsi_high < previous_rsi_high:
            return 'bearish_divergence'

    # Check for bullish divergence (price lower lows, RSI higher lows)
    if price_lows.iloc[-3:].sum() > 0 and rsi_lows.iloc[-3:].sum() > 0:
        recent_price_low = price_data[price_lows].iloc[-1]
        previous_price_low = price_data[price_lows].iloc[-2]
        recent_rsi_low = rsi_data[rsi_lows].iloc[-1]
        previous_rsi_low = rsi_data[rsi_lows].iloc[-2]

        if recent_price_low < previous_price_low and recent_rsi_low > previous_rsi_low:
            return 'bullish_divergence'

    return 'no_divergence'


def check_rsi_divergence(input_csv_file, output_csv_file, kite, instrument_df):
    """
    Function to check for RSI divergence for all tickers in the input CSV file.
    
    Args:
        input_csv_file (str): Path to the CSV file containing ticker and RSI data.
        output_csv_file (str): Path to the output CSV file to store divergence results.
        kite (KiteConnect): KiteConnect instance for fetching historical data.
        instrument_df (pd.DataFrame): DataFrame containing instrument information.
    
    Returns:
        pd.DataFrame: DataFrame containing tickers with their divergence status.
    """
    # Load the RSI results from the CSV file
    rsi_data = pd.read_csv(input_csv_file)

    # Initialize an empty list to store the results
    divergence_results = []

    # Loop through each stock in the DataFrame
    for index, row in rsi_data.iterrows():
        ticker = row['Ticker']
        current_price = row['Current Price']
        rsi_value = row['RSI']
        
        # Fetch historical OHLC data for the current ticker (last 180 days)
        end_date = dt.datetime.today()
        start_date = end_date - dt.timedelta(days=180)
        ohlc_data = fetch_ohlc(ticker, 'day', start_date, end_date)

        if ohlc_data is not None and not ohlc_data.empty:
            closing_prices = ohlc_data['close']  # Get closing prices
            rsi_values = RSI(ohlc_data)  # Calculate RSI using historical data

            # Check for divergence
            divergence = find_divergence(closing_prices, rsi_values)

            # Append results
            divergence_results.append({
                'Ticker': ticker,
                'Current Price': current_price,
                'RSI': rsi_value,
                'divergence': divergence
            })
        else:
            divergence_results.append({
                'Ticker': ticker,
                'Current Price': current_price,
                'RSI': rsi_value,
                'divergence': 'no_data'
            })

    # Convert the results to a DataFrame
    divergence_df = pd.DataFrame(divergence_results)

    # Save the divergence results to the output CSV file
    divergence_df.to_csv(output_csv_file, index=False)

    print(f"Divergence results saved in {output_csv_file}.")
    return divergence_df

def select_stocks_with_rsi_above_50(kite, instrument_df, shares, interval='day', days=180, rsi_threshold=50):
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





# Example usage
input_csv_file = 'output.csv'
output_csv_file = 'rsi_divergence_output.csv'

# Check RSI divergence for all tickers
check_rsi_divergence(input_csv_file, output_csv_file, kite, instrument_df)


