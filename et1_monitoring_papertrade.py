# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 15:22:58 2024

@author: Saarit
"""

import time
from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd
import numpy as np
import sys
import datetime as dt
import pandas as pd
import logging
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import threading

# Known market holidays for 2024 (example)
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
        return instrument_token
    except IndexError:
        logging.error(f"Symbol {symbol} not found in instrument dump.")
        return -1
    except Exception as e:
        logging.error(f"Error in instrument lookup: {e}")
        return -1
import pandas as pd
import time

def monitor_paper_trades(file_path='papertrade.csv', target_percentage=2.0, sl_percentage=1.5, check_interval=60):
    """
    Monitor the paper trades for target and stop-loss conditions.
    
    Args:
    - file_path (str): Path to the papertrade.csv file.
    - target_percentage (float): Percentage target for profit (default 2%).
    - sl_percentage (float): Percentage stop-loss (default 1.5%).
    - check_interval (int): Time interval in seconds to check prices (default 60 seconds).
    """
    
    try:
        # Read the paper trades
        paper_trades = pd.read_csv(file_path)
    except FileNotFoundError as e:
        print(f"File {file_path} not found: {e}")
        return
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Keep a list of active trades
    active_trades = paper_trades.copy()

    # Initialize or create the results file
    results_file = 'papertrade_result.csv'
    if not os.path.exists(results_file):
        with open(results_file, 'w') as f:
            f.write('Ticker,Sell Price,Quantity Sold,Total Value Sold,Profit,Loss,Time\n')  # Write header

    while not active_trades.empty:
        for index, row in active_trades.iterrows():
            ticker = row['Ticker']
            buy_price = row['Buy Price']
            quantity = row['Quantity']
            total_value_bought = row['Total Value Bought']

            # Fetch the current price of the ticker (placeholder function)
            current_price = fetch_current_price(ticker)

            # Calculate target and stop-loss prices
            target_price = buy_price * (1 + target_percentage / 100)
            sl_price = buy_price * (1 - sl_percentage / 100)

            # Check for target hit
            if current_price >= target_price:
                total_value_sold = current_price * quantity
                profit = total_value_sold - total_value_bought
                print(f"Target hit for {ticker}! Sold at ₹{current_price}, Total Value Sold: ₹{total_value_sold}, Profit: ₹{profit}")

                # Append the result to the results file
                with open(results_file, 'a') as f:
                    f.write(f"{ticker},{current_price},{quantity},{total_value_sold},{profit},, {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

                active_trades = active_trades.drop(index)  # Remove from active trades

            # Check for stop-loss hit
            elif current_price <= sl_price:
                total_value_sold = current_price * quantity
                loss = total_value_bought - total_value_sold
                print(f"Stop-loss hit for {ticker}! Sold at ₹{current_price}, Total Value Sold: ₹{total_value_sold}, Loss: ₹{loss}")

                # Append the result to the results file
                with open(results_file, 'a') as f:
                    f.write(f"{ticker},{current_price},{quantity},{total_value_sold},,{loss},{time.strftime('%Y-%m-%d %H:%M:%S')}\n")

                active_trades = active_trades.drop(index)  # Remove from active trades

        # Sleep for the specified interval before the next check
        time.sleep(check_interval)

    print("Monitoring complete. All results have been logged to papertrade_result.csv.")


# Function to fetch live price
def fetch_current_price(ticker):
    """Fetches the current live price of the given stock."""
    try:
        instrument = instrument_lookup(instrument_df, ticker)
        live_price_data = kite.ltp(f"NSE:{ticker}")
        return live_price_data[f"NSE:{ticker}"]["last_price"]
    except Exception as e:
        logging.error(f"Error fetching live price for {ticker}: {e}")
        return None


# Run the monitoring function
monitor_paper_trades()