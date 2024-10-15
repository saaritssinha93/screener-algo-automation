# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication
"""

from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

# Nifty 50 stocks list (as of the most recent known set of companies)
nifty50_stocks = [
    'ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 
    'BAJAJFINSV', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 
    'COALINDIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GRASIM', 
    'HCLTECH', 'HDFCBANK', 'HDFC', 'HEROMOTOCO', 'HINDALCO', 
    'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY', 
    'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 
    'NESTLEIND', 'NTPC', 'ONGC', 'POWERGRID', 'RELIANCE', 
    'SBILIFE', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 
    'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'ULTRACEMCO', 
    'UPL', 'WIPRO'
]

# Known market holidays for 2024 (example, you can update this list)
market_holidays = [
    dt.date(2024, 10, 2),  # Gandhi Jayanti
    # Add other known holidays for the year here
]

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
        logging.info(f"Instrument token for {symbol}: {instrument_token}")
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

# Function to fetch OHLC data for a specific date range
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

        # Print full response for debugging
        logging.info(f"Raw API response for {ticker}: {kite.historical_data(instrument, start_date, end_date, interval)}")

        if not data.empty:
            logging.info(f"Fetched data columns for {ticker}: {data.columns}")
            data.set_index("date", inplace=True)
            return data
        else:
            logging.error(f"No data returned for {ticker}")
            return pd.DataFrame()

    except Exception as e:
        logging.error(f"Error fetching OHLC data for {ticker}: {e}")
        return None

# Function to fetch live price
def fetch_live_price(symbol):
    """Fetches the current live price of the given stock."""
    try:
        instrument = instrument_lookup(instrument_df, symbol)
        live_price_data = kite.ltp(f"NSE:{symbol}")
        return live_price_data[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        logging.error(f"Error fetching live price for {symbol}: {e}")
        return None

# Global list to store stocks with 2% or more growth
high_growth_stocks = []

# Function to print last closing price, current price, and percentage change
def print_price_comparison(symbol):
    """Prints last market day closing price, current price, and percentage change."""    
    # Find the last trading day
    last_trading_day = get_last_trading_day()
    
    # Set date range (last trading day to today)
    start_date = last_trading_day
    end_date = last_trading_day
    
    logging.info(f"Fetching data for {symbol} on last trading day: {last_trading_day}")
    
    # Fetch OHLC data for last trading day and today's live price
    ohlc_data = fetch_ohlc(symbol, "day", start_date, end_date)
    
    if ohlc_data is not None and not ohlc_data.empty:
        if 'close' in ohlc_data.columns:
            last_close = ohlc_data['close'].iloc[-1]
            live_price = fetch_live_price(symbol)
            
            if live_price is not None:
                percent_change = ((live_price - last_close) / last_close) * 100
                
                logging.info(f"{symbol}:")
                logging.info(f"Last Trading Day Close: {last_close}")
                logging.info(f"Current Price: {live_price}")
                logging.info(f"Percentage Change: {percent_change:.2f}%")
                
                # Check if the percentage change is 2% or more
                if percent_change >= 2:
                    logging.info(f"{symbol} has increased by {percent_change:.2f}%, which is above 2%.")
                    print(f"{symbol}: Last Close: {last_close}, Current Price: {live_price}, Percentage Change: {percent_change:.2f}% (Above 2% growth)")
                    high_growth_stocks.append(symbol)  # Add to the list of high growth stocks
                else:
                    print(f"{symbol}: Last Close: {last_close}, Current Price: {live_price}, Percentage Change: {percent_change:.2f}%")
            else:
                logging.error(f"Could not fetch live price for {symbol}")
        else:
            logging.error(f"'close' column missing in OHLC data for {symbol}")
    else:
        logging.error(f"Could not fetch historical data for {symbol}")

# Function to print all stocks with 2% or more change
def print_high_growth_stocks():
    """Prints all stocks with a percentage change of 2% or more."""
    if high_growth_stocks:
        logging.info("Stocks with 2% or more increase:")
        print("Stocks with 2% or more increase:")
        for stock in high_growth_stocks:
            print(stock)
    else:
        logging.info("No stocks have increased by 2% or more.")
        print("No stocks have increased by 2% or more.")

# Example usage: Fetch last close, live price, and percentage change for Nifty 50 stocks
for stock in nifty50_stocks:
    print_price_comparison(stock)

# Print all stocks with 2% or more change
print_high_growth_stocks()