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
from datetime import datetime

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

# Set up logging
logging.basicConfig(filename='trading_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Known market holidays for 2024 (example)
market_holidays = [
    dt.date(2024, 10, 2),  # Gandhi Jayanti
    # Add other known holidays for the year here
]

# Function to setup Kite Connect session
def setup_kite_session():
    """Establishes a Kite Connect session."""
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

# Function to get dump of all NSE instruments
def fetch_instruments(kite):
    """Fetches all NSE instruments and returns a DataFrame."""
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

# Function to fetch live price
def fetch_current_price(ticker, kite, instrument_df):
    """Fetches the current live price of the given stock."""
    try:
        instrument = instrument_lookup(instrument_df, ticker)
        live_price_data = kite.ltp(f"NSE:{ticker}")
        return live_price_data[f"NSE:{ticker}"]["last_price"]
    except Exception as e:
        logging.error(f"Error fetching live price for {ticker}: {e}")
        return None

def monitor_paper_trades(kite, instrument_df, file_path='papertrade.csv', target_percentage=2.0, check_interval=60):
    """
    Monitor the paper trades for target conditions.
    
    Args:
    - kite (KiteConnect): Kite Connect instance for fetching live prices.
    - instrument_df (pd.DataFrame): DataFrame containing instrument information.
    - file_path (str): Path to the papertrade.csv file.
    - target_percentage (float): Percentage target for profit (default 2%).
    - check_interval (int): Time interval in seconds to check prices (default 60 seconds).
    """
    
    try:
        # Read the paper trades
        paper_trades = pd.read_csv(file_path)
        
        # Initialize active_trades from paper_trades
        active_trades = paper_trades.copy()
        
    except FileNotFoundError as e:
        print(f"File {file_path} not found: {e}")
        return
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    if active_trades.empty:
        print("No active trades found.")
        return

    sold_trades = pd.DataFrame(columns=['Ticker', 'Sell Price', 'Quantity Sold', 'Total Value Sold', 'Profit', 'Time'])

    while not active_trades.empty:
        current_time = datetime.now()

        for index, row in active_trades.iterrows():
            ticker = row['Ticker']
            buy_price = row['Buy Price']
            quantity = row['Quantity']
            total_value_bought = row['Total Value Bought']

            current_price = fetch_current_price(ticker, kite, instrument_df)
            target_price = buy_price * (1 + target_percentage / 100)

            # Check for target hit
            if current_price >= target_price:
                total_value_sold = current_price * quantity
                profit = total_value_sold - total_value_bought
                print(f"Target hit for {ticker}! Sold at ₹{current_price}, Total Value Sold: ₹{total_value_sold}, Profit: ₹{profit}")

                new_trade = pd.DataFrame({
                    'Ticker': [ticker], 'Sell Price': [current_price], 'Quantity Sold': [quantity],
                    'Total Value Sold': [total_value_sold], 'Profit': [profit], 'Time': [time.strftime('%Y-%m-%d %H:%M:%S')]
                })

                if not new_trade.isna().all().all():
                    sold_trades = pd.concat([sold_trades, new_trade], ignore_index=True)

                active_trades = active_trades.drop(index)

        calculate_and_print_investment_status(active_trades, sold_trades)

        if (current_time.hour > 15) or (current_time.hour == 15 and current_time.minute >= 30):
            print("End of trading day reached. Stopping monitoring.")
            break

        time.sleep(check_interval)

    # Save the sold trades to a CSV file with 5 blank rows before the next entry
    if not sold_trades.empty:
        # Create a DataFrame with 5 blank rows
        blank_rows = pd.DataFrame([[''] * sold_trades.shape[1]] * 2, columns=sold_trades.columns)
        
        # Concatenate the blank rows with sold trades
        to_save = pd.concat([sold_trades, blank_rows], ignore_index=True)
        
        # Append to the CSV file
        to_save.to_csv('papertrade_result.csv', mode='a', header=not pd.io.common.file_exists('papertrade_result.csv'), index=False)

    print("Monitoring complete. All results have been logged to papertrade_result.csv.")





def calculate_and_print_investment_status(active_trades, sold_trades):
    """
    Calculate and print the net investment sold, net capital still invested,
    and net investment change based on trades that have hit target or stop-loss.
    
    Args:
    - active_trades (pd.DataFrame): DataFrame of ongoing trades that haven't hit target or stop-loss.
    - sold_trades (pd.DataFrame): DataFrame of trades where target or stop-loss was hit and sold.
    """

    # Calculate net investment sold
    if not sold_trades.empty:
        net_investment_sold = sold_trades['Total Value Sold'].sum()
        print(f"Net Investment Sold (after target/SL hit): ₹{net_investment_sold:.2f}")
    else:
        net_investment_sold = 0
        print("No trades have hit target or stop-loss yet.")

    # Calculate net capital still invested
    if not active_trades.empty:
        net_capital_invested = active_trades['Total Value Bought'].sum()
        print(f"Net Capital Still Invested: ₹{net_capital_invested:.2f}")
    else:
        net_capital_invested = 0
        print("No capital is still invested in active trades.")
        
    # Calculate net investment bought
    net_investment_bought = calculate_net_investment_bought()

    # Calculate net investment change
    net_investment_change = net_investment_sold - net_investment_bought
    print(f"Net Change: ₹{net_investment_change:.2f}")

    # Calculate percentage change
    if net_investment_bought != 0:  # Avoid division by zero
        percentage_change = (net_investment_change / net_investment_bought) * 100
        print(f"Percentage Change: {percentage_change:.2f}%")
    else:
        print("No investment bought to calculate percentage change.")




def calculate_net_investment_bought(sold_trades_file='papertrade_result.csv', active_trades_file='papertrade.csv'):
    """
    Calculate the net investment bought based on trades in the sold trades file.

    Args:
    - sold_trades_file (str): Path to the papertrade_result.csv file.
    - active_trades_file (str): Path to the papertrade.csv file.
    
    Returns:
    - float: Total net investment bought.
    """
    try:
        # Read the sold trades
        sold_trades = pd.read_csv(sold_trades_file)
        # Read the active trades
        active_trades = pd.read_csv(active_trades_file)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return 0.0
    except Exception as e:
        print(f"Error reading files: {e}")
        return 0.0

    # Initialize total investment bought
    total_investment_bought = 0.0

    # Loop through each ticker in sold trades
    for ticker in sold_trades['Ticker'].unique():
        # Get corresponding active trades for the ticker
        active_trade = active_trades[active_trades['Ticker'] == ticker]
        
        if not active_trade.empty:
            # Sum the Total Value Bought for the current ticker
            total_value_bought = active_trade['Total Value Bought'].sum()
            total_investment_bought += total_value_bought

    print(f"Net Investment Bought: ₹{total_investment_bought:.2f}")
    return total_investment_bought





def main():
    
    logging.info("Starting the trading algorithm...")
    
    # Setup Kite session
    kite = setup_kite_session()     
    
    # Fetch instruments
    instrument_df = fetch_instruments(kite)

    
    # Run the monitoring function
    monitor_paper_trades(kite, instrument_df)

if __name__ == "__main__":
    main()
    logging.shutdown()

