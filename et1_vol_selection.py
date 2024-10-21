# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 17:41:53 2024

@author: Saarit
"""

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

sys.path.append('C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation')
from et1_stock_tickers import shares

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

# Get dump of all NSE instruments
def fetch_instruments(kite):
    try:
        instrument_dump = kite.instruments("NSE")
        instrument_df = pd.DataFrame(instrument_dump)
        logging.info("NSE instrument data fetched successfully.")
        return instrument_df

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

# Function to check if a day is a market open day (skips weekends and holidays)
def is_market_open(day):
    """Returns True if the day is a market open day (i.e., not a weekend or a holiday)."""
    return day.weekday() < 5 and day not in market_holidays  # Monday=0, ..., Friday=4 (market open), skip weekends and holidays

# Function to find the most recent trading day
def get_last_trading_day():
    """Returns the most recent trading day (skips weekends and holidays)."""
    today = dt.date.today()
    day = today - dt.timedelta(days=1)  # Start with yesterday
    
    # Keep going back until we find a market open day
    while not is_market_open(day):
        day -= dt.timedelta(days=1)
    
    return day

def fetch_ohlc(ticker, interval, start_date, end_date, kite, instrument_df):
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


def get_last_closing_price(ticker, start_date, end_date, kite, instrument_df):
    """Function to get the last closing price of a stock."""
    try:
        # Fetch historical data for the given date range
        data = pd.DataFrame(
            kite.historical_data(
                instrument_lookup(instrument_df, ticker), 
                start_date, 
                end_date, 
                interval='day'  # Using daily interval to get closing prices
            )
        )

        if not data.empty:
            # Get the last closing price
            last_close = data['close'].iloc[-1]
            return last_close
        else:
            logging.info(f"No historical data returned for {ticker}.")
            return None

    except Exception as e:
        logging.error(f"Error fetching last closing price for {ticker}: {e}")
        return None

# Function to fetch live price
def fetch_live_price(symbol, kite, instrument_df):
    """Fetches the current live price of the given stock."""
    try:
        instrument = instrument_lookup(instrument_df, symbol)
        live_price_data = kite.ltp(f"NSE:{symbol}")
        return live_price_data[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        logging.error(f"Error fetching live price for {symbol}: {e}")
        return None
  
# Function to get live price using the Kite API
def get_live_price(ticker, kite, instrument_df):
    try:
        live_price_data = kite.ltp(f"NSE:{ticker}")
        live_price = live_price_data[f'NSE:{ticker}']['last_price']
        return live_price
    except Exception as e:
        logging.error(f"Error fetching live price for {ticker}: {e}")
        return None  

def calculate_30_day_sma_volume(ticker, start_date, end_date, kite, instrument_df):
    """Function to calculate 30-day simple moving average of volume for a given stock."""
    try:
        # Fetch OHLC data for the stock
        data = fetch_ohlc(ticker, "day", start_date, end_date, kite, instrument_df)
        
        if data is not None and not data.empty:
            # Calculate the 30-day SMA of the volume
            data['30_day_sma_volume'] = data['volume'].rolling(window=30).mean()

            # Return only relevant columns: volume and 30-day SMA of volume
            return data[['volume', '30_day_sma_volume']].tail(30)
        else:
            logging.error(f"No data available for {ticker}")
            return pd.DataFrame()

    except Exception as e:
        logging.error(f"Error calculating 30-day SMA for {ticker}: {e}")
        return pd.DataFrame()

def select_high_volume_stocks(ticker, start_date, end_date, kite, instrument_df, volume_multiplier=1.3):
    """Function to select stocks where the current volume is 1.5 times the 30-day SMA of volume."""
    today = dt.date.today()

    # If today is Monday, set yesterday to the previous Friday
    if today.weekday() == 0:  # Monday is 0
        yesterday = today - dt.timedelta(days=3)
    # For all other days, just subtract 1 day
    else:
        yesterday = today - dt.timedelta(days=1)

    try:
        # Fetch the 30-day SMA volume data
        data = calculate_30_day_sma_volume(ticker, start_date, end_date, kite, instrument_df)
        
        # Fetch OHLC data for start_date (daily) and specified_date (5-minute intervals)
        last_close_price = get_last_closing_price(ticker, yesterday, yesterday, kite, instrument_df)
        
        if not data.empty:
            # Get the current volume (latest date) and 30-day SMA of the volume
            current_volume = data['volume'].iloc[-1]
            sma_volume = data['30_day_sma_volume'].iloc[-1]

            # Fetch the current live price using Kite API or other service
            current_price = get_live_price(ticker, kite, instrument_df)

            # Check if the current volume is greater than or equal to 1.5 times the 30-day SMA
            if current_volume >= volume_multiplier * sma_volume:
                # If the condition is met, return the ticker, prices, and volume details
                return {
                    'ticker': ticker,
                    'current_volume': current_volume,
                    'sma_volume': sma_volume,
                    'last_close_price': last_close_price,
                    'current_price': current_price
                }
        else:
            logging.info(f"No valid data available for {ticker}")

    except Exception as e:
        logging.error(f"Error selecting stock {ticker}: {e}")

    return None  # Return None if the stock doesn't meet the criteria

# Function to filter and store the selected stocks
def store_high_volume_stocks(start_date, end_date, kite, instrument_df, volume_multiplier=1.3, output_file='high_volume_stocks.csv'):
    """Function to filter and store stocks where the current volume is 1.3 times the 30-day SMA of volume."""
    selected_stocks = []

    for stock in shares:
        result = select_high_volume_stocks(stock, start_date, end_date, kite, instrument_df, volume_multiplier)

        if result is not None:
            selected_stocks.append(result)

    # Convert the selected stocks list to a DataFrame and store it as a CSV
    if selected_stocks:
        df = pd.DataFrame(selected_stocks)
        df.to_csv(output_file, index=False)
        print(f"Selected high-volume stocks saved to {output_file}")
    else:
        print("No stocks met the criteria.")

def main():
    
    logging.info("Starting the trading algorithm...")
    kite = initialize_kite()
    instrument_df = fetch_instruments(kite)

    start_date = dt.datetime(2024, 8, 15)  # Set appropriate start date
    end_date = dt.datetime.now()  # Automatically sets to today's date and current time

    # Store stocks with current volume 1.3x of 30-day SMA
    store_high_volume_stocks(start_date, end_date, kite, instrument_df)

if __name__ == "__main__":
    main()
    logging.shutdown()
