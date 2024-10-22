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

def fetch_current_price(ticker, kite, instrument_df):
    """Function to fetch current price (can be modified to use historical data or live data)."""
    # Implement this based on your KiteConnect setup
    instrument_token = instrument_lookup(instrument_df, ticker)
    if instrument_token == -1:
        print(f"Instrument lookup failed for {ticker}")
        return None
    try:
        ltp_data = kite.ltp([f'NSE:{ticker}'])  # Assuming NSE tickers, adjust if needed
        return ltp_data[f'NSE:{ticker}']['last_price']
    except Exception as e:
        print(f"Error fetching current price for {ticker}: {e}")
        return None

import time
from datetime import datetime
import pandas as pd
import pytz

def fetch_historical_price(ticker, kite, instrument_df, start_time, end_time, interval='minute'):
    """
    Fetch historical price data for backtesting.
    
    Args:
    - ticker (str): Stock ticker symbol.
    - kite (KiteConnect): Kite Connect instance.
    - instrument_df (pd.DataFrame): DataFrame containing instrument information.
    - start_time (datetime): Start time for historical data.
    - end_time (datetime): End time for historical data.
    - interval (str): Time interval for the data (e.g., 'minute', '5minute').
    
    Returns:
    - pd.DataFrame: DataFrame of historical price data.
    """
    instrument_token = instrument_lookup(instrument_df, ticker)
    if instrument_token == -1:
        print(f"Instrument lookup failed for {ticker}")
        return None
    
    try:
        # Adjust the start and end time format
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Fetch historical data from KiteConnect
        historical_data = kite.historical_data(instrument_token, from_date=start_time_str, to_date=end_time_str, interval=interval)
        return pd.DataFrame(historical_data)
    
    except Exception as e:
        print(f"Error fetching historical data for {ticker}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error



import tkinter as tk
import pandas as pd
import pytz
from datetime import datetime
import time
import threading

def monitor_ticker_in_window(ticker, buy_price, quantity, total_value_bought, trade_time, kite, instrument_df, target_percentage, interval):
    """
    Monitor a single ticker in a separate tkinter window.
    
    Args:
    - ticker (str): The stock ticker to monitor.
    - buy_price (float): Buy price of the ticker.
    - quantity (int): Quantity of stocks bought.
    - total_value_bought (float): Total value of the stocks bought.
    - trade_time (datetime): Time the trade was made.
    - kite (KiteConnect): Kite Connect instance for fetching historical prices.
    - instrument_df (pd.DataFrame): DataFrame containing instrument information.
    - target_percentage (float): Percentage target for profit.
    - interval (str): Time interval for historical price data (default 'minute').
    """

    # Create a pop-up window for the ticker
    root = tk.Tk()
    root.title(f"Monitoring {ticker}")
    
    # Create a text widget to display results for each ticker
    text_widget = tk.Text(root, height=20, width=100)
    text_widget.pack()

    # Function to append text to the text widget
    def append_text(message, window=text_widget):
        window.insert(tk.END, message + '\n')
        window.see(tk.END)  # Scroll to the end of the text widget
        root.update()  # Update the window to refresh the UI

    append_text(f"Monitoring {ticker} from {trade_time}...")

    # Calculate target price
    target_price = buy_price * (1 + target_percentage / 100)

    # Define historical data time range (for backtesting)
    local_tz = pytz.timezone('Asia/Kolkata')
    start_time = trade_time
    end_time = datetime.now(local_tz)  # Simulate monitoring until current time
    
    # Fetch historical prices
    historical_prices = fetch_historical_price(ticker, kite, instrument_df, start_time, end_time, interval)
    if historical_prices.empty:
        append_text(f"No historical data available for {ticker}. Skipping.")
        root.mainloop()
        return

    # Monitor each row in historical data
    for _, price_row in historical_prices.iterrows():
        current_time = pd.to_datetime(price_row['date']).tz_convert(local_tz)
        current_price = price_row['close']

        # Display monitoring data in the respective ticker window
        append_text(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Ticker: {ticker}, Current Price: ₹{current_price}")

        # Check for target hit
        if current_price >= target_price:
            total_value_sold = current_price * quantity
            profit = total_value_sold - total_value_bought
            percentage_profit = (profit / total_value_bought) * 100

            append_text(f"Target hit for {ticker}! Sold at ₹{current_price}, Total Value Sold: ₹{total_value_sold}, "
                        f"Profit: ₹{profit}, Percentage Profit: {percentage_profit:.2f}%, Sold Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            break

        # Simulate time passing (1 second delay)
        time.sleep(1)

    root.mainloop()

def monitor_paper_trades_backtest(kite, instrument_df, file_path='papertrade.csv', target_percentage=2, interval='minute'):
    """
    Continuously monitor paper trades using historical price data for backtesting and open separate pop-up windows for each ticker.
    
    Args:
    - kite (KiteConnect): Kite Connect instance for fetching historical prices.
    - instrument_df (pd.DataFrame): DataFrame containing instrument information.
    - file_path (str): Path to the papertrade.csv file.
    - target_percentage (float): Percentage target for profit (default 2%).
    - interval (str): Time interval for historical price data (default 'minute').
    """

    # Read the paper trades
    try:
        paper_trades = pd.read_csv(file_path)
        if paper_trades.empty:
            print("No active trades found.")
            return
    except FileNotFoundError as e:
        print(f"File {file_path} not found: {e}")
        return
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Set timezone
    local_tz = pytz.timezone('Asia/Kolkata')

    # Create threads for each ticker to run their own monitoring window
    threads = []

    # Loop through each trade and start monitoring in a separate thread
    for index, row in paper_trades.iterrows():
        ticker = row['Ticker']
        buy_price = row['Buy Price']
        quantity = row['Quantity']
        total_value_bought = row['Total Value Bought']
        trade_time = pd.to_datetime(row['Time'])

        # Convert trade_time to local timezone if needed
        if trade_time.tzinfo is None:
            trade_time = trade_time.tz_localize(local_tz)
        else:
            trade_time = trade_time.tz_convert(local_tz)

        # Create a thread to run the monitor function for each ticker
        thread = threading.Thread(
            target=monitor_ticker_in_window,
            args=(ticker, buy_price, quantity, total_value_bought, trade_time, kite, instrument_df, target_percentage, interval)
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()













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
    monitor_paper_trades_backtest(kite, instrument_df)

if __name__ == "__main__":
    main()
    logging.shutdown()

