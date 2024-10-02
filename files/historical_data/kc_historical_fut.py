# -*- coding: utf-8 -*-
"""
Getting historical data using Kite API
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

# Get dump of all NSE instruments for NFO
try:
    instrument_dump = kite.instruments("NFO")
    instrument_df = pd.DataFrame(instrument_dump)
    
    # Filter for NFO Futures
    fut_df = instrument_df[instrument_df["segment"] == "NFO-FUT"]
    logging.info("Futures instrument data fetched successfully.")
    
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

# Function to fetch OHLC data
def fetch_ohlc(ticker, interval, duration):
    """Extracts historical OHLC data and returns it as a DataFrame."""
    try:
        instrument = instrument_lookup(fut_df, ticker)
        if instrument == -1:
            raise ValueError(f"Instrument lookup failed for ticker {ticker}")

        # Fetch historical data
        data = pd.DataFrame(
            kite.historical_data(
                instrument, 
                dt.date.today() - dt.timedelta(days=duration), 
                dt.date.today(), 
                interval
            )
        )
        data.set_index("date", inplace=True)
        logging.info(f"OHLC data fetched for {ticker}")
        return data
    except Exception as e:
        logging.error(f"Error fetching OHLC data for {ticker}: {e}")
        return None

# Example usage: Fetch historical OHLC data for BANKNIFTY futures
ohlc_data = fetch_ohlc("BANKNIFTY24NOVFUT", "5minute", 4)
if ohlc_data is not None:
    print(ohlc_data.head())



"""
from kiteconnect import KiteConnect
import os
import datetime as dt
import pandas as pd

cwd = os.chdir("D:\\Udemy\\Zerodha KiteConnect API\\1_account_authorization")

#generate trading session
access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)


#get dump of all NSE instruments
instrument_dump = kite.instruments("NFO")
instrument_df = pd.DataFrame(instrument_dump)
fut_df = instrument_df[instrument_df["segment"]=="NFO-FUT"]

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1


def fetchOHLC(ticker,interval,duration):
    """extracts historical data and outputs in the form of dataframe"""
    instrument = instrumentLookup(instrument_df,ticker)
    data = pd.DataFrame(kite.historical_data(instrument,dt.date.today()-dt.timedelta(duration), dt.date.today(),interval))
    data.set_index("date",inplace=True)
    return data

fetchOHLC("NIFTY20MAYFUT","5minute",4)
"""