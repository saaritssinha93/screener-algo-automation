# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 16:48:37 2024

@author: Saarit
"""

# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication for fetching 5-minute interval historical data for today.
"""

import time
from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

# Stocks
shares = [
    'ECLERX', 'EDELWEISS', 'EIDPARRY', 'EIHOTEL',
    'ELGIEQUIP', 'EMAMILTD', 'EMIL', 'ENDURANCE', 'ENGINERSIN',
    'ERIS', 'ESABINDIA', 'FCONSUMER', 'FEDERALBNK', 'FIEMIND',
    'FINPIPE', 'NATCOPHARM', 'NATIONALUM', 'NBCC', 'ZENSARTECH'   
]

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
        logging.info(f"Instrument token for {symbol}: {instrument_token}")
        return instrument_token
    except IndexError:
        logging.error(f"Symbol {symbol} not found in instrument dump.")
        return -1
    except Exception as e:
        logging.error(f"Error in instrument lookup: {e}")
        return -1

# Function to fetch OHLC data for a specific date range
def fetch_ohlc(ticker, interval, start_date, end_date):
    """Extracts historical OHLC data for a specific date range and returns it as a DataFrame."""
    try:
        # Perform instrument lookup
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
            logging.info(f"Fetched data columns for {ticker}: {data.columns}")
            
            # Ensure 'date' column is available for further processing
            data['date'] = pd.to_datetime(data['date'])  # Ensure 'date' is in datetime format

            # Extract 'time' from 'date' for additional clarity
            data['time'] = data['date'].dt.time
            data['date_only'] = data['date'].dt.date

            # Set 'date' as the index for OHLC-style handling, but retain the date and time columns in the DataFrame
            data.set_index('date', inplace=False)  # Optional: you can choose to keep date or reset index
            return data
        else:
            logging.error(f"No data returned for {ticker}")
            return pd.DataFrame()

    except Exception as e:
        logging.error(f"Error fetching OHLC data for {ticker}: {e}")
        return None


# Initialize an empty DataFrame to store all fetched data
df_all_shares = pd.DataFrame()

# Initialize an empty dictionary to store high growth stocks
high_growth_stocks = {}

# Function to fetch today's data in 5-minute intervals and store in DataFrame
def fetch_today_data(ticker):
    """Fetches 5-minute interval data for today and stores it in a DataFrame."""
    try:
        # Get the start and end date for today
        today = dt.datetime.now()
        start_date = dt.datetime(today.year, today.month, today.day, 9, 15)  # Market opens at 9:15 AM
        end_date = today  # Up to the current time

        # Fetch 5-minute interval data for today
        logging.info(f"Fetching 5-minute interval data for {ticker} for today.")
        ohlc_data = fetch_ohlc(ticker, "5minute", start_date, end_date)
        
        if ohlc_data is not None and not ohlc_data.empty:
            logging.info(f"Data for {ticker} fetched successfully.")
            ohlc_data['ticker'] = ticker  # Add a 'ticker' column to identify the stock
            
            # Print column names for debugging
            logging.info(f"Fetched data columns for {ticker}: {ohlc_data.columns}")
            
            # Normalize column names by stripping any leading/trailing spaces and converting to lowercase
            ohlc_data.columns = ohlc_data.columns.str.strip().str.lower()
            
            # Check if 'date' column exists after normalization
            if 'date' in ohlc_data.columns:
                # Convert the 'date' column to datetime
                ohlc_data['date'] = pd.to_datetime(ohlc_data['date'])
                
                # Extract both 'date' and 'time' from the 'date' column
                ohlc_data['date_only'] = ohlc_data['date'].dt.date
                ohlc_data['time'] = ohlc_data['date'].dt.time
            else:
                logging.error(f"'date' column not found in the data for {ticker}. Columns: {ohlc_data.columns}")

            # Append the data to the global DataFrame
            global df_all_shares
            df_all_shares = pd.concat([df_all_shares, ohlc_data], ignore_index=True)
        else:
            logging.error(f"No data fetched for {ticker} today.")
    except Exception as e:
        logging.error(f"Error fetching today's data for {ticker}: {e}")

def get_last_trading_day():
    """Returns the last trading day (excluding weekends and holidays)."""
    today = dt.datetime.now()
    last_day = today

    # Check if today is a weekend (Saturday or Sunday)
    if today.weekday() in [5, 6]:
        # If it's Saturday, go back to Friday
        last_day = today - dt.timedelta(days=today.weekday() - 4)  # Friday
    else:
        # Assuming the market is open Monday to Friday
        # You can add logic here to check for holidays
        pass

    # Return the date without time
    return last_day.date()


# Modify the print_price_comparison function to compare last day's close with today's 9:45 am 5-minute close
def print_price_comparison(symbol):
    """Prints last market day closing price, current day's 9:45 am price, and percentage change along with volume change."""
    global high_growth_stocks  # Declare it as global to modify the global variable

    # Find the last trading day
    last_trading_day = get_last_trading_day()

    # Get today's date
    today = dt.datetime.now()

    # Set date range for the last trading day (whole day)
    start_date_last_day = last_trading_day
    end_date_last_day = last_trading_day

    # Fetch last trading day's OHLC data
    logging.info(f"Fetching last trading day data for {symbol} on {last_trading_day}")
    ohlc_data_last_day = fetch_ohlc(symbol, "day", start_date_last_day, end_date_last_day)

    # Set date range for today's 9:45 AM to 9:50 AM (5-minute interval)
    start_date_today_5min = dt.datetime(today.year, today.month, today.day, 9, 45)
    end_date_today_5min = dt.datetime(today.year, today.month, today.day, 9, 50)

    # Fetch today's 5-minute OHLC data for 9:45 AM close
    logging.info(f"Fetching today's 5-minute interval data for {symbol} starting at 9:45 AM")
    ohlc_data_today_5min = fetch_ohlc(symbol, "5minute", start_date_today_5min, end_date_today_5min)

    # Check if both dataframes have data
    if ohlc_data_last_day is not None and not ohlc_data_last_day.empty and ohlc_data_today_5min is not None and not ohlc_data_today_5min.empty:
        if 'close' in ohlc_data_last_day.columns and 'close' in ohlc_data_today_5min.columns:
            # Get last day's close
            last_day_close = ohlc_data_last_day['close'].iloc[-1]

            # Get today's 9:45 AM close (from 5-minute data)
            today_945_close = ohlc_data_today_5min['close'].iloc[-1]

            # Calculate percentage change
            percent_change = ((today_945_close - last_day_close) / last_day_close) * 100

            logging.info(f"{symbol}: Last Trading Day Close: {last_day_close}, 9:45 AM Close Today: {today_945_close}, "
                         f"Percentage Change: {percent_change:.2f}%")

            # Check if the percentage change is 2% or more
            if percent_change >= 2:
                logging.info(f"{symbol} has increased by {percent_change:.2f}%, which is above 2%.")
                
                # Fetch volume data if needed (this section can be skipped if volume comparison is not required)
                volume_data_15m = fetch_ohlc(symbol, "15minute", last_trading_day, last_trading_day)  # Fetch last 15-minute volume
                if volume_data_15m is not None and not volume_data_15m.empty:
                    last_volume = volume_data_15m['volume'].iloc[-1]
                    last_day_volume = ohlc_data_last_day['volume'].iloc[-1]

                    logging.info(f"15-min volume: {last_volume}, Last day volume: {last_day_volume}")

                    if last_day_volume > 0:
                        volume_change = ((last_volume - last_day_volume) / last_day_volume) * 100
                    else:
                        volume_change = float('inf')  # Handle zero volume edge case

                    logging.info(f"Volume Change for {symbol}: {volume_change:.2f}%")
                    
                    print(f"{symbol}: Last Close: {last_day_close}, 9:45 AM Close: {today_945_close}, "
                          f"Percentage Change: {percent_change:.2f}%, Volume Change: {volume_change:.2f}%")
                    
                    # Store in the global dictionary
                    high_growth_stocks[symbol] = (percent_change, volume_change)  # Store as a tuple
                else:
                    print(f"{symbol}: Last Close: {last_day_close}, 9:45 AM Close: {today_945_close}, "
                          f"Percentage Change: {percent_change:.2f}%, Volume Change: Data not available")
            else:
                print(f"{symbol}: Last Close: {last_day_close}, 9:45 AM Close: {today_945_close}, "
                      f"Percentage Change: {percent_change:.2f}%")
        else:
            logging.error(f"'close' column missing in OHLC data for {symbol}")
    else:
        logging.error(f"Could not fetch historical data for {symbol}")



# Modified function to print the high growth stocks
def print_high_growth_stocks():
    """Prints the stocks with a growth of 2% or more along with volume change."""
    logging.info("Stocks with 2% or more increase:")
    if high_growth_stocks:
        # Sort the high_growth_stocks dictionary by percentage change in descending order
        sorted_stocks = sorted(high_growth_stocks.items(), key=lambda item: item[1][0], reverse=True)
        
        for stock, (percent, volume_change) in sorted_stocks:
            print(f"{stock}: {percent:.2f}%   Volume Change: {volume_change:.2f}%")
    else:
        logging.info("No stocks have increased by 2% or more.")
        print("No stocks have increased by 2% or more.")


# Function to select the top 3 high growth stocks based on percentage change
def select_top_growth_stocks(growth_stocks, n=3):
    """Selects top N high growth stocks based on percentage change."""
    sorted_stocks = sorted(growth_stocks.items(), key=lambda x: x[1][0], reverse=True)
    top_stocks = sorted_stocks[:n]
    return {symbol: (percent, volume) for symbol, (percent, volume) in top_stocks}

# Function to fetch the live price of a stock
def fetch_live_price(symbol):
    """Fetches the live price of the given stock symbol."""
    try:
        # Assume we have a method in the KiteConnect instance to fetch live price
        live_price_data = kite.ltp(f"NSE:{symbol}")
        return live_price_data[f"NSE:{symbol}"]['last_price']
    except Exception as e:
        logging.error(f"Error fetching live price for {symbol}: {e}")
        return None

# Function to simulate paper trading
def paper_trade(stocks, investment_per_stock=50000, target=0.005, stop_loss=0.01):
    """Simulates paper trading on selected stocks."""
    results = []
    
    for symbol in stocks:
        live_price = fetch_live_price(symbol)
        
        if live_price is None:
            logging.error(f"Could not fetch live price for {symbol}, skipping paper trade.")
            continue
        
        # Calculate the number of shares to buy
        shares_to_buy = investment_per_stock // live_price
        investment = shares_to_buy * live_price
        target_price = live_price * (1 + target)
        stop_loss_price = live_price * (1 - stop_loss)

        # Initialize variables for trailing stop loss
        highest_price = live_price
        trailing_stop_loss_price = stop_loss_price

        # Simulate the price movements (for example, over a trading session)
        price_movements = np.random.normal(0, 0.5, 100)  # Simulate some price movements
        
        for movement in price_movements:
            current_price = live_price + movement
            
            # Update trailing stop loss if current price exceeds highest price
            if current_price > highest_price:
                highest_price = current_price
                trailing_stop_loss_price = highest_price * (1 - stop_loss)
            
            # Check for target hit or stop loss hit
            if current_price >= target_price:
                results.append((symbol, investment, live_price, shares_to_buy, target_price, stop_loss_price, "Target Hit"))
                break
            elif current_price <= trailing_stop_loss_price:
                results.append((symbol, investment, live_price, shares_to_buy, target_price, stop_loss_price, "Stop Loss Hit"))
                break
        else:
            results.append((symbol, investment, live_price, shares_to_buy, target_price, stop_loss_price, "No Action"))

    return pd.DataFrame(results, columns=["Stock", "Investment", "Buy Price", "Shares Bought", "Target", "Stop Loss", "Status"])

# Function to monitor stocks and execute sell as per target or stop-loss
# Function to monitor stocks and execute sell as per target or stop-loss
def monitor_stocks(stocks, investment_per_stock=50000, target=0.001, stop_loss=0.001):
    """Monitors stocks and executes sell based on target or stop-loss."""
    trade_info = {}
    
    # Initialize trades
    for symbol in stocks:
        live_price = fetch_live_price(symbol)
        shares_to_buy = investment_per_stock // live_price
        target_price = live_price * (1 + target)
        stop_loss_price = live_price * (1 - stop_loss)
        
        trade_info[symbol] = {
            'investment': investment_per_stock,
            'buy_price': live_price,
            'shares_bought': shares_to_buy,
            'target_price': target_price,
            'stop_loss_price': stop_loss_price,
            'status': 'Holding'
        }

    total_invested = sum(info['investment'] for info in trade_info.values())
    net_total = total_invested  # Initialize net total with total invested

    while trade_info:  # Continue while there are stocks being monitored
        for symbol in list(trade_info.keys()):  # Use list to avoid modifying dict during iteration
            current_price = fetch_live_price(symbol)
            
            # Print live price and trade status
            print(f"Monitoring {symbol}: Live Price = {current_price:.2f}, Status = {trade_info[symbol]['status']}")
            
            # Check for target hit or stop loss hit
            if current_price >= trade_info[symbol]['target_price']:
                profit = trade_info[symbol]['shares_bought'] * (current_price - trade_info[symbol]['buy_price'])
                net_total += profit
                print(f"Target hit! Sold {trade_info[symbol]['shares_bought']} shares of {symbol} at {current_price:.2f}.")
                print(f"Target hit! Investment: {trade_info[symbol]['investment']}, Buy Price: {trade_info[symbol]['buy_price']:.2f}, "
                      f"Target: {trade_info[symbol]['target_price']:.2f}, Stop Loss: {trade_info[symbol]['stop_loss_price']:.2f}")
                print(f"Total Invested: {total_invested}, Net Total: {net_total:.2f}")
                del trade_info[symbol]  # Remove the stock from monitoring
            
            elif current_price <= trade_info[symbol]['stop_loss_price']:
                loss = trade_info[symbol]['shares_bought'] * (trade_info[symbol]['buy_price'] - current_price)
                net_total -= loss
                print(f"Stop Loss hit! Sold {trade_info[symbol]['shares_bought']} shares of {symbol} at {current_price:.2f}.")
                print(f"Stop Loss hit! Investment: {trade_info[symbol]['investment']}, Buy Price: {trade_info[symbol]['buy_price']:.2f}, "
                      f"Target: {trade_info[symbol]['target_price']:.2f}, Stop Loss: {trade_info[symbol]['stop_loss_price']:.2f}")
                print(f"Total Invested: {total_invested}, Net Total: {net_total:.2f}")
                del trade_info[symbol]  # Remove the stock from monitoring
        
        time.sleep(1)  # Sleep for a second before checking again

# Fetch data for all shares
for share in shares:
    fetch_today_data(share)
    print_price_comparison(share)  # Only the symbol is passed
  # Compare at 9:45 AM

# Get top 3 high growth stocks based on 9:45 AM data
top_stocks = select_top_growth_stocks(high_growth_stocks)

# Perform paper trading on top stocks
trade_results = paper_trade(top_stocks)

# Print the results
print(trade_results)

# Monitor the stocks and execute sell based on target or stop-loss
monitor_stocks(top_stocks)
