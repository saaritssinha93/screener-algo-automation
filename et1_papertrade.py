# et1_vol_2%_rsi_60_selection.py
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 17:41:53 2024

@author: Saarit
"""

from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd
from datetime import datetime

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
def setup_kite_session():
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
def fetch_nse_instruments(kite):
    try:
        instrument_dump = kite.instruments("NSE")
        instrument_df = pd.DataFrame(instrument_dump)
        logging.info("NSE instrument data fetched successfully.")
        return instrument_df
        
    except Exception as e:
        logging.error(f"Error fetching instruments: {e}")
        raise

def paper_trade_from_significant_changes(file_path='significant_change.csv', trade_amount=20000, output_file='papertrade.csv'):
    """
    Read significant_change.csv, and place a paper trade for the second iteration of each ticker.
    Invest approximately ₹20,000 at the 'Close' price for each second occurrence of a ticker.
    
    Args:
    - file_path (str): Path to the significant_change.csv file.
    - trade_amount (int): The amount of money to invest in each trade (default ₹20,000).
    - output_file (str): Path to save the paper trade details (default 'papertrade.csv').
    
    Prints:
    - Buy price, quantity, and total value bought for each trade.
    - Total invested amount across all trades.
    """
    
    try:
        # Read the significant_changes.csv file
        significant_changes = pd.read_csv(file_path)
    except FileNotFoundError as e:
        print(f"File {file_path} not found: {e}")
        return
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Keep track of ticker occurrences
    ticker_counts = {}
    paper_trades = []
    total_invested = 0  # To keep track of the total invested amount

    # Iterate through the data
    for index, row in significant_changes.iterrows():
        ticker = row['ticker']
        
        # Increment the ticker count
        if ticker not in ticker_counts:
            ticker_counts[ticker] = 1
        else:
            ticker_counts[ticker] += 1

        # Place a paper trade only on the second iteration of a ticker
        if ticker_counts[ticker] == 2:
            close_price = row['Close']
            quantity = trade_amount // close_price  # Approximate quantity of shares to buy
            total_value = quantity * close_price  # Total value of the trade

            # Update total invested amount
            total_invested += total_value

            # Print trade details
            print(f"Buy Trade - Ticker: {ticker}, Buy Price: ₹{close_price}, Quantity: {quantity}, Total Value: ₹{total_value}")

            # Append the trade details to the paper_trades list
            paper_trades.append({
                'Ticker': ticker,
                'Buy Price': close_price,
                'Quantity': quantity,
                'Total Value Bought': total_value,
                'Time': row['Time']
            })

    # Save the paper trades to papertrade.csv
    if paper_trades:
        paper_trades_df = pd.DataFrame(paper_trades)
        paper_trades_df.to_csv(output_file, index=False)
        print(f"Paper trades saved to {output_file}")
        print(f"Total invested amount: ₹{total_invested}")
    else:
        print("No trades were made.")

def main():
    
    logging.info("Starting the trading algorithm...")
    kite = setup_kite_session()
    instrument_df = fetch_nse_instruments(kite)
    paper_trade_from_significant_changes()

if __name__ == "__main__":
    main()
    logging.shutdown()

