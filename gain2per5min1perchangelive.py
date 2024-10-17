# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 17:41:53 2024

@author: Saarit
"""

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

# Stocks
shares = [
    'AARTIDRUGS', 'AARTISURF-BE', 'ABFRL', 'ADANIPOWER', 'ADVENZYMES', 
    'AFFLE', 'AGARIND', 'AJMERA', 'ALEMBICLTD', 'ARE&M', 
    'ANANTRAJ', 'APCOTEXIND', 'APLAPOLLO', 'ARCHIDPLY', 'ASHOKA',
    'ASIANHOTNR', 'ASTERDM', 'AUROPHARMA', 'AXISBANK', 'BALAMINES',
    'BALRAMCHIN', 'BANCOINDIA', 'BASF', 'BATAINDIA',
    'BAYERCROP', 'BDL', 'BEL', 'BEML',
    'BERGEPAINT', 'BFUTILITIE', 'BGRENERGY-BE', 'BHAGERIA-BE', 'BHARATGEAR',
    'BIRLAMONEY-BE', 'BLUESTARCO', 'BOROLTD', 'BRIGADE', 'BSOFT',
    'CAPLIPOINT', 'CARYSIL', 'CEATLTD', 'CENTUM', 'CHALET',
    'CHEMCON', 'CHEMFAB', 'CHEMPLASTS', 'CHOLAHLDNG', 'TITAGARH' ,
    'COCHINSHIP-BE', 'COFORGE', 'COSMOFIRST', 'CROMPTON', 'CSBBANK',
    'CYIENT', 'LTFOODS', 'DCAL', 'DEEPAKFERT', 'DELTACORP',
    'DENORA', 'DISHTV', 'DOLLAR', 'DPSCLTD', 'DREDGECORP',
    'DYNPRO-BE', 'ECLERX', 'EDELWEISS', 'EIDPARRY', 'EIHOTEL',
    'ELGIEQUIP', 'EMAMILTD', 'EMIL', 'ENDURANCE', 'ENGINERSIN',
    'ERIS', 'ESABINDIA' , 'FEDERALBNK', 'FIEMIND',
    'FINPIPE', 'FLUOROCHEM', 'GABRIEL', 'GAIL', 'GALAXYSURF',
    'GARFIBRES', 'GATEWAY', 'GEPIL', 'GHCL', 'GICHSGFIN',
    'GILLETTE', 'GIPCL', 'GLS', 'GNA', 'GNFC',
    'GODFRYPHLP', 'GOODYEAR', 'GRAUWEIL', 'GRINDWELL', 'GLAXO',
    'GTPL', 'GUFICBIO', 'GULFOILLUB', 'HAPPSTMNDS', 'HARRMALAYA-BE',
    'HATSUN', 'HERITGFOOD', 'HFCL', 'HIKAL',
    'HINDCOPPER', 'HINDZINC', 'HMVL', 'HINDOILEXP', 'HONAUT',
    'HSIL', 'ICIL', 'ICRA', 'IDBI', 'IDFCFIRSTB',
    'IFBIND', 'IIFL', 'IL&FSENGG-BZ', 'IMFA', 'INDIANB',
    'INDIANCARD', 'INDIGO', 'INDORAMA', 'INDOSTAR', 'STYRENIX',
    'INFIBEAM', 'INTELLECT', 'IRB', 'IRCON', 'ISEC',
    'ITI', 'J&KBANK', 'JAICORPLTD', 'JAMNAAUTO', 'JASH',
    'JBCHEPHARM', 'JETAIRWAYS-BZ', 'JINDALPHOT', 'JISLJALEQS', 'JKCEMENT',
    'JKLAKSHMI', 'JKPAPER', 'JMFINANCIL', 'JSL', 'JTEKTINDIA',
    'JUBLFOOD', 'JUBLINDS', 'KABRAEXTRU', 'KAJARIACER', 'KPIL',
    'KANSAINER', 'KEI', 'KIRLOSENG', 'KITEX',
    'KNRCON', 'KOKUYOCMLN', 'KOLTEPATIL', 'KOPRAN', 'KRBL',
    'KSB', 'LTF', 'LAOPALA', 'LEMONTREE', 'LINDEINDIA',
    'LUXIND', 'M&MFIN', 'MAHABANK', 'CIEINDIA', 'MAHSCOOTER',
    'MAITHANALL', 'MANAKSIA', 'MARKSANS', 'MASTEK', 'MAYURUNIQ',
    'MAZDOCK', 'MBAPL', 'UNITDSPR', 'MINDACORP',
    'MOLDTECH', 'MONTECARLO', 'MOREPENLAB', 'MOTILALOFS', 'MPHASIS',
    'MRPL', 'MSTCLTD', 'MTARTECH', 'MUKANDLTD', 'MUNJALSHOW',
    'NATCOPHARM', 'NATIONALUM', 'NBCC', 'NCC', 'NDL',
    'NELCO', 'NESCO', 'NESTLEIND', 'NLCINDIA', 'NMDC',
    'NOCIL', 'NRAIL', 'NTPC', 'NUCLEUS', 'OBEROIRLTY',
    'OIL', 'OLECTRA', 'OMAXE', 'ONGC', 'ORIENTCEM',
    'ORIENTELEC', 'ORTINGLOBE' , 'PAGEIND', 'PANAMAPET', 'PARAGMILK',
   'PCJEWELLER-BE', 'PDSL', 'PEL', 'PERSISTENT', 'PETRONET',
   'PFIZER', 'GODFRYPHLP', 'PILANIINVS', 'PNBHOUSING', 'POLYCAB',
   'POWERINDIA', 'PRAJIND', 'PRSMJOHNSN', 'PTC',
   'RAILTEL', 'RAIN', 'RALLIS', 'RANEHOLDIN', 'RATNAMANI',
   'RAYMOND', 'RECLTD', 'RELAXO', 'RELINFRA-BE', 'RENUKA',
   'RITES', 'ROSSARI', 'RTNPOWER' , 'RUCHINFRA-BE',
   'RVNL', 'SAGCEM', 'SANOFI', 'SARDAEN', 'SBICARD',
   'SCI', 'SEQUENT-BE', 'SHILPAMED', 'SHOPERSTOP', 'SHREDIGCEM',
   'SEPC', 'SHYAMMETL', 'SIEMENS', 'SIS', 'SJS',
   'SKFINDIA', 'SOBHA', 'SOLARA', 'SONACOMS', 'SOUTHBANK',
   'SPAL', 'SPARC', 'SRHHYPOLTD', 'SHRIRAMFIN', 'STAR',
   'STCINDIA', 'STLTECH', 'SUBEXLTD', 'SUDARSCHEM', 'SUNDRMFAST',
   'SUNPHARMA', 'SPLPETRO', 'SUPRAJIT', 'SUVEN', 'SWARAJENG',
   'SYMPHONY', 'TANLA', 'TATAINVEST', 'TCPLPACK',
   'TATAPOWER', 'TATASTEEL', 'TCS', 'TECHM', 'TEGA',
   'THEINVEST', 'THERMAX', 'TIMKEN', 'TITAN', 'TORNTPOWER',
   'TRENT', 'TRITURBINE', 'TTKPRESTIG', 'TV18BRDCST', 'TVSMOTOR',
   'UCOBANK', 'ULTRACEMCO', 'UNIONBANK', 'UNOMINDA', 'UPL',
   'UJJIVANSFB', 'VAKRANGEE', 'VARROC', 'VEDL', 'VENKEYS',
   'VGUARD', 'VIPIND', 'VOLTAMP', 'VSTIND',
   'ZFCVINDIA', 'WALCHANNAG', 'WELCORP', 'WELSPUNLIV', 'WHIRLPOOL',
   'WOCKPHARMA', 'YESBANK', 'ZEEL', 'ZENITHSTL-BE', 'ZENTEC',
   # Nifty 50 stocks list
   'ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 
   'BAJAJFINSV', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 
   'COALINDIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GRASIM', 
   'HCLTECH', 'HDFCBANK', 'HEROMOTOCO', 'HINDALCO', 
   'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY', 
   'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 
   'NESTLEIND', 'NTPC', 'ONGC', 'POWERGRID', 'RELIANCE', 
   'SBILIFE', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 
   'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'ULTRACEMCO', 
   'UPL', 'WIPRO', 'NEULANDLAB', 'YATHARTH',
   # Top 100 midcap stocks
   'ADANIGREEN', 'ADANIPORTS', 'AJANTPHARM', 'ALKEM', 'AMBUJACEM', 
   'APOLLOHOSP', 'ASHOKLEY', 'ASTRAL', 'ATUL', 'AVANTIFEED',
   'BAJFINANCE', 'BAJAJHFL', 'BANKBARODA', 'BEL', 'BHARATFORG',
   'BHARTIARTL', 'BIRLACORPN', 'ZYDUSLIFE', 'CANFINHOME', 'CEATLTD',
   'CENTRALBK', 'CIPLA', 'COFORGE', 'COLPAL', 'CONCOR',
   'CROMPTON', 'DABUR', 'DCMSHRIRAM', 'DEEPAKNTR', 'DIVISLAB',
   'DIXON', 'DLF', 'EICHERMOT', 'ESCORTS', 'EXIDEIND',
   'GAIL', 'GLAND', 'GLAXO', 'GMRINFRA', 'GRANULES',
   'HAVELLS', 'HDFCLIFE', 'HINDCOPPER', 'HINDPETRO', 'HINDUNILVR',
   'ICICIBANK', 'IGL', 'INDIGO', 'INDUSINDBK', 'INDUSTOWER',
   'IRCTC', 'JINDALSTEL', 'JSL', 'KEC', 'KIRLOSENG',
   'LTF', 'LT', 'LTIM', 'MOTHERSON', 'MUTHOOTFIN',
   'NIITLTD', 'NOCIL', 'OIL', 'PERSISTENT', 'PIDILITIND',
   'POLYCAB', 'PVRINOX', 'RAMCOCEM', 'RELIANCE', 'SAIL',
   'SBIN', 'SBICARD', 'SHREECEM', 'SRF', 'SUDARSCHEM',
   'SUNPHARMA', 'TATAELXSI', 'TECHM', 'TITAN', 'TORNTPHARM',
   'TRIDENT', 'ULTRACEMCO', 'UNIONBANK', 'UPL', 'VOLTAS',
   'WIPRO', 'ZENSARTECH'
      
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

# Dictionary to store stocks with their percentage and volume change
high_growth_stocks = {}

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

def print_price_comparison(symbol):
    """Prints last market day closing price, current price, and percentage change."""    
    # Find the last trading day
    last_trading_day = get_last_trading_day()
    
    # Set date range for the last trading day and last 15 minutes
    start_date = last_trading_day
    end_date = last_trading_day
    
    # Fetch OHLC data for last trading day and today's live price
    ohlc_data = fetch_ohlc(symbol, "day", start_date, end_date)
    volume_data_15m = fetch_ohlc(symbol, "15minute", last_trading_day, last_trading_day)  # Fetch last 15-minute volume

    if ohlc_data is not None and not ohlc_data.empty:
        if 'close' in ohlc_data.columns:
            last_close = ohlc_data['close'].iloc[-1]
            live_price = fetch_live_price(symbol)
            
            if live_price is not None:
                percent_change = ((live_price - last_close) / last_close) * 100
                
                # Only output if price change is >= 2%
                if percent_change >= 2:
                    # Calculate volume change if volume data is available
                    if volume_data_15m is not None and not volume_data_15m.empty:
                        last_volume = volume_data_15m['volume'].iloc[-1]
                        last_day_volume = ohlc_data['volume'].iloc[-1]

                        if last_day_volume > 0:
                            volume_change = ((last_volume - last_day_volume) / last_day_volume) * 100
                        else:
                            volume_change = float('inf')  # Handle zero volume edge case
                        
                        # Output result in concise format
                        print(f"{symbol}: Price +{percent_change:.2f}%, Volume Change: {volume_change:.2f}%")
                        high_growth_stocks[symbol] = (percent_change, volume_change)
                    else:
                        print(f"{symbol}: Price +{percent_change:.2f}%, Volume Change: N/A")
                # If price change < 2%, minimal output
                else:
                    print(f"{symbol}: Price Change: {percent_change:.2f}%")
            else:
                print(f"Error: Live price not available for {symbol}")
        else:
            print(f"Error: Missing 'close' data for {symbol}")
    else:
        print(f"Error: Historical data not available for {symbol}")


# Modified function to print high growth stocks and save to CSV
def print_high_growth_stocks():
    """Prints the stocks with a growth of 2% or more along with volume change, 
    sorted by percent growth in descending order, and saves to a CSV file."""
    logging.info("Stocks with 2% or more increase:")

    if high_growth_stocks:
        # Sort the high_growth_stocks dictionary by the percent change in descending order
        sorted_stocks = sorted(high_growth_stocks.items(), key=lambda x: x[1][0], reverse=True)
        
        # Prepare data for CSV
        ranked_data = []
        for stock, (percent, volume_change) in sorted_stocks:
            ranked_data.append({"Stock": stock, "Percent Change": f"{percent:.2f}%", "Volume Change": f"{volume_change:.2f}%"})
            print(f"{stock}: {percent:.2f}%   Volume Change: {volume_change:.2f}%")
        
        # Create a DataFrame and save it to CSV
        ranked_df = pd.DataFrame(ranked_data)
        ranked_df.to_csv("high_growth_stocks.csv", index=False)

    else:
        logging.info("No stocks have increased by 2% or more.")
        print("No stocks have increased by 2% or more.")

def run_every_30mins(shares):
    """Run the price comparison and high-growth stock functions every 30 minutes."""
    
    while True:
        # Perform actions for each share
        for share in shares:
            print_price_comparison(share)

        # Print high-growth stocks
        print_high_growth_stocks()

        # Log or print the time of execution
        print(f"Data fetched and printed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Wait for 30 minutes (1800 seconds) before the next run
        time.sleep(1800)  # 1800 seconds = 30 minutes



# Function to select the top 3 high growth stocks based on percentage change
def select_top_growth_stocks(growth_stocks, n=3):
    """Selects top N high growth stocks based on percentage change."""
    sorted_stocks = sorted(growth_stocks.items(), key=lambda x: x[1][0], reverse=True)
    top_stocks = sorted_stocks[:n]
    return {symbol: (percent, volume) for symbol, (percent, volume) in top_stocks}

# Function to simulate paper trading
def paper_trade(stocks, investment_per_stock=50000, target=0.02, stop_loss=0.015):
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

import tkinter as tk
from tkinter import scrolledtext
import threading
import time

from datetime import datetime, timedelta

def show_significant_changes_popup(changes):
    """Creates a popup window to display significant price changes."""
    window = tk.Tk()
    window.title("Significant Price Changes")

    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=100, height=40)
    text_area.pack(padx=10, pady=10)

    if changes:
        for change in changes:
            text_area.insert(tk.END, f"Symbol: {change['Symbol']}, Time: {change['Time']}, "
                                       f"Close: {change['Close']}, Price Change: {change['Price Change']:.2f}%\n")
    else:
        text_area.insert(tk.END, "No significant price changes found.\n")

    # Automatically close the window after 120 seconds
    window.after(120000, window.destroy)  # 120000 milliseconds = 120 seconds

    window.mainloop()

# Updated fetch function to call the popup window
def fetch_3min_intervals_for_high_growth_stocks(growth_stocks, threshold=2, verbose=True):
    """Fetch 3-minute interval data for high-growth stocks for today's date, 
    handle errors, and check data availability."""
    
    # Get today's date
    today = datetime.now()
    
    # Set the market start and end time for today
    start_date = today.replace(hour=9, minute=15, second=0, microsecond=0)
    end_date = today.replace(hour=15, minute=30, second=0, microsecond=0)

    logging.info(f"Scanning 3-minute data for high-growth stocks on {today.date()}.")

    # Prepare to collect significant changes for CSV
    all_significant_changes = []

    for symbol in growth_stocks:
        try:
            # Fetch OHLC data for 3-minute intervals
            ohlc_data_3min = fetch_ohlc(symbol, '3minute', start_date, end_date)

            if ohlc_data_3min is None or ohlc_data_3min.empty:
                logging.warning(f"No 3-minute data available for {symbol}. Skipping.")
                continue

            # Calculate the percentage price changes between consecutive intervals
            ohlc_data_3min = get_price_changes(ohlc_data_3min)

            # Filter for intervals with a positive price change greater than the threshold
            significant_changes = ohlc_data_3min[ohlc_data_3min['price_change'] > threshold]

            if not significant_changes.empty:
                if verbose:
                    print(f"\nSignificant positive price changes (> {threshold}% change) for {symbol} on {today.date()}:")
                    print(significant_changes[['close', 'price_change']])

                # Append significant changes to the list for CSV output
                for index, row in significant_changes.iterrows():
                    all_significant_changes.append({
                        "Symbol": symbol,
                        "Time": index,
                        "Close": row['close'],
                        "Price Change": row['price_change']
                    })

        except KeyError as e:
            logging.error(f"Symbol error for {symbol}: {e}")
            print(f"Error with symbol {symbol}: {e}")
        except Exception as e:
            logging.error(f"Error fetching 3-minute data for {symbol}: {e}")
            print(f"Error fetching data for {symbol}: {e}")

    # Save all significant changes to a CSV file if there are any
    if all_significant_changes:
        changes_df = pd.DataFrame(all_significant_changes)
        changes_df.to_csv("significant_price_changes.csv", index=False)
        print(f"Significant price changes saved to significant_price_changes.csv")
        
        # Show significant changes in a popup window
        show_significant_changes_popup(all_significant_changes)
    else:
        print("No significant price changes found for any stocks.")

# Function to calculate percentage change between consecutive intervals
def get_price_changes(df):
    """Calculates the percentage change in 'close' price between consecutive rows."""
    df['price_change'] = df['close'].pct_change() * 100
    return df



import time
import datetime as dt

def fetch_3min_intervals_for_high_growth_stocks_periodically(growth_stocks, threshold=1):
    """Fetch updated 3-minute interval data for high-growth stocks every 3 minutes."""
    
    while True:
        # Get the current time and set the start and end times for the latest 3-minute window
        end_time = dt.datetime.now()
        start_time = end_time - dt.timedelta(minutes=3)

        # Fetch the updated 3-minute interval data
        fetch_3min_intervals_for_high_growth_stocks(growth_stocks, threshold=1)

        # Log or print the time of execution
        print(f"Fetched data for the 3-minute interval from {start_time} to {end_time}.")

        # Wait for 3 minutes before running the next scan
        time.sleep(180)  # 180 seconds = 3 minutes



# Function to print high-growth stocks in a new window
def print_high_growth_stocks_in_window():
    """Creates a new window to display high-growth stocks."""
    window = tk.Tk()
    window.title("High-Growth Stocks")

    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=100, height=40)
    text_area.pack(padx=10, pady=10)

    # Display high-growth stocks
    if high_growth_stocks:
        sorted_stocks = sorted(high_growth_stocks.items(), key=lambda x: x[1][0], reverse=True)
        for stock, (percent, volume_change) in sorted_stocks:
            text_area.insert(tk.END, f"{stock}: {percent:.2f}%   Volume Change: {volume_change:.2f}%\n")
    else:
        text_area.insert(tk.END, "No stocks have increased by 2% or more.\n")

    # Function to close the window
    def close_window():
        window.destroy()

    # Schedule the close_window function to run after 120 seconds
    window.after(120000, close_window)  # 120000 milliseconds = 120 seconds

    window.mainloop()

# Function to simulate stock selection and paper trading
def run_trading_tasks():
    """Simulates the stock selection and trading tasks."""
    time.sleep(2)  # Simulate delay
    
    # Get top 3 high growth stocks
    print("Selecting top 3 high growth stocks...")
    top_stocks = select_top_growth_stocks(high_growth_stocks)
    
    # Perform paper trading on top stocks
    print("Performing paper trading on top stocks...")
    trade_results = paper_trade(top_stocks)
    
    # Print trade results
    print(trade_results)
  
    # Example usage: Get all high-growth stocks
    all_high_growth_stocks = high_growth_stocks

    # Scan 3-minute intervals for all high-growth stocks
    print("Fetching 3-minute intervals for all high-growth stocks...")
    fetch_3min_intervals_for_high_growth_stocks(all_high_growth_stocks, threshold=1)

# Function to run tasks in the background
def run_background_tasks():
    """Run background tasks like stock analysis and paper trading."""
    run_trading_tasks()

# Start the tkinter window in the main thread
def start_ui():
    """Start the tkinter window in the main thread."""
    print_high_growth_stocks_in_window()

# Run Tkinter window and background task concurrently
def run_program():
    # Start the output window in a separate thread
    output_thread = threading.Thread(target=start_ui)
    output_thread.start()

    # Background task to run simultaneously
    """Start background tasks in a separate thread."""
    background_thread = threading.Thread(target=run_background_tasks)
    background_thread.daemon = True  # Daemon so it doesn't block exiting
    background_thread.start()



if __name__ == "__main__":
    for _ in range(22000):  # Run twice
        for share in shares:
            print_price_comparison(share)

        print_high_growth_stocks()
        # Run tkinter window and background tasks
        run_program()
    
