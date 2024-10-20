# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 09:27:18 2024

@author: Saarit
"""

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

# Global DataFrame to store high-growth stocks
high_growth_stocks = pd.DataFrame(columns=['Symbol', 'Percent Change', 'Status'])

def compare_price_change(symbol, start_date, specified_date):
    """Compares the closing price at start_date and specified_date for a given stock.
    If the price change exceeds 2%, it stores the stock as a high-growth stock in the high_growth_stocks DataFrame.
    """
    global high_growth_stocks  # Declare the DataFrame as global to modify it inside the function

    try:
        # Fetch OHLC data for start_date (daily) and specified_date (5-minute intervals)
        ohlc_start = fetch_ohlc(symbol, "day", start_date, start_date)
        ohlc_specified = fetch_ohlc(symbol, "5minute", specified_date.replace(hour=9, minute=15), specified_date)

        if ohlc_start is not None and not ohlc_start.empty and ohlc_specified is not None and not ohlc_specified.empty:
            # Extract closing prices
            start_close = ohlc_start['close'].iloc[0]

            # Get the last available close price for the specified date and time
            specified_close = ohlc_specified['close'].iloc[-1]  # Use the last close in the 5-min data

            # Calculate price change percentage
            percent_change = ((specified_close - start_close) / start_close) * 100

            # Check if the percent change is equal to or greater than 2%
            if percent_change >= 2:
                # Create a dictionary for the current stock
                current_stock_data = {
                    'Symbol': symbol,
                    'Percent Change': percent_change,
                    'Status': 'High Growth'
                }
                # Append the current stock data to the high_growth_stocks DataFrame
                high_growth_stocks.loc[len(high_growth_stocks)] = current_stock_data  # Append row

                print(f"{symbol}: Price percentage Change : {percent_change:.2f}%")
            else:
                print(f"{symbol}: Price percentage Change : {percent_change:.2f}%")

        else:
            print(f"No data available for {symbol} on {start_date} or {specified_date}")

    except Exception as e:
        print(f"Error comparing price change for {symbol}: {e}")


def print_high_growth_stocks(shares, start_date, specified_date):
    """Prints high-growth stocks in descending order of percentage change,
    only those with a change of 2% or more."""
    global high_growth_stocks  # Ensure we're using the global DataFrame

    # Clear the high_growth_stocks DataFrame before new data
    high_growth_stocks = pd.DataFrame(columns=['Symbol', 'Percent Change', 'Status'])

    # Iterate through each stock symbol in the list
    for symbol in shares:
        compare_price_change(symbol, start_date, specified_date)

    if not high_growth_stocks.empty:
        # Sort stocks by percentage change in descending order
        sorted_stocks = high_growth_stocks.sort_values(by='Percent Change', ascending=False)

        # Print sorted high-growth stocks
        print("High Growth Stocks (>= 2% change) in Descending Order:")
        for _, row in sorted_stocks.iterrows():
            print(f"{row['Symbol']}: {row['Percent Change']:.2f}% - {row['Status']}")
    else:
        print("No high growth stocks found.")




def print_5min_interval_data_for_high_growth_stocks(high_growth_stocks, specified_date):
    """Fetch and print 5-minute interval data for all high-growth stocks on a specified date
    where the price change is greater than or equal to 1%."""
    
    start_time = specified_date.replace(hour=9, minute=15)  # Market opens at 9:15 AM
    end_time = specified_date.replace(hour=15, minute=30)    # Market closes at 3:30 PM

    # Iterate over the rows of the high_growth_stocks DataFrame
    for _, row in high_growth_stocks.iterrows():
        symbol = row['Symbol']  # Get the stock symbol
        try:
            # Fetch OHLC data for 5-minute intervals
            ohlc_data_5min = fetch_ohlc(symbol, '5minute', start_time, end_time)

            if ohlc_data_5min is None or ohlc_data_5min.empty:
                print(f"No 5-minute data available for {symbol}.")
                continue
            
            # Calculate percentage changes for price and volume
            ohlc_data_5min['price_change'] = ohlc_data_5min['close'].pct_change() * 100
            ohlc_data_5min['volume_change'] = ohlc_data_5min['volume'].pct_change() * 100
            
            # Filter for positive price changes >= 1%
            positive_changes = ohlc_data_5min[ohlc_data_5min['price_change'] >= 1]

            if positive_changes.empty:
                print(f"No positive changes found for {symbol}.")
                continue

            print(f"\n5-Minute Interval Data with >= 1% Positive Change for {symbol} on {specified_date.date()}:")
            for index, change_row in positive_changes.iterrows():
                print(f"Time: {index}, Price Change: {change_row['price_change']:.2f}%, Volume Change: {change_row['volume_change']:.2f}%")

        except Exception as e:
            logging.error(f"Error fetching 5-minute data for {symbol}: {e}")
            print(f"Error fetching data for {symbol}: {e}")

def print_5min_v_interval_data_for_high_growth_stocks(high_growth_stocks, specified_date):
    """Fetch and print 5-minute interval data for all high-growth stocks on a specified date
    where the price change is greater than or equal to 1%."""
    
    start_time = specified_date.replace(hour=9, minute=15)  # Market opens at 9:15 AM
    end_time = specified_date.replace(hour=15, minute=30)    # Market closes at 3:30 PM

    # Iterate over the rows of the high_growth_stocks DataFrame
    for _, row in high_growth_stocks.iterrows():
        symbol = row['Symbol']  # Get the stock symbol
        try:
            # Fetch OHLC data for 5-minute intervals
            ohlc_data_5min = fetch_ohlc(symbol, '5minute', start_time, end_time)

            if ohlc_data_5min is None or ohlc_data_5min.empty:
                print(f"No 5-minute data available for {symbol}.")
                continue
            
            # Calculate percentage changes for price and volume
            ohlc_data_5min['price_change'] = ohlc_data_5min['close'].pct_change() * 100
            ohlc_data_5min['volume_change'] = ohlc_data_5min['volume'].pct_change() * 100
            
            # Filter for positive volume change >= 10%
            positive_changes = ohlc_data_5min[ohlc_data_5min['volume_change'] >= 1000]

            if positive_changes.empty:
                print(f"No positive changes found for {symbol}.")
                continue

            print(f"\n5-Minute Interval Data with >= 1% Positive Change for {symbol} on {specified_date.date()}:")
            for index, change_row in positive_changes.iterrows():
                print(f"Time: {index}, Price Change: {change_row['price_change']:.2f}%, Volume Change: {change_row['volume_change']:.2f}%")

        except Exception as e:
            logging.error(f"Error fetching 5-minute data for {symbol}: {e}")
            print(f"Error fetching data for {symbol}: {e}")



def print_5min_pv_interval_data_for_high_growth_stocks(high_growth_stocks, specified_date):
    """Fetch and print 5-minute interval data for all high-growth stocks on a specified date
    where the price change is greater than or equal to 1%."""
    
    start_time = specified_date.replace(hour=9, minute=15)  # Market opens at 9:15 AM
    end_time = specified_date.replace(hour=15, minute=30)    # Market closes at 3:30 PM

    # Iterate over the rows of the high_growth_stocks DataFrame
    for _, row in high_growth_stocks.iterrows():
        symbol = row['Symbol']  # Get the stock symbol
        try:
            # Fetch OHLC data for 5-minute intervals
            ohlc_data_5min = fetch_ohlc(symbol, '5minute', start_time, end_time)

            if ohlc_data_5min is None or ohlc_data_5min.empty:
                print(f"No 5-minute data available for {symbol}.")
                continue
            
            # Calculate percentage changes for price and volume
            ohlc_data_5min['price_change'] = ohlc_data_5min['close'].pct_change() * 100
            ohlc_data_5min['volume_change'] = ohlc_data_5min['volume'].pct_change() * 100
            
            # Filter for positive volume change >= 10%
            positive_changes = ohlc_data_5min[(ohlc_data_5min['volume_change'] >= 1000) & (ohlc_data_5min['price_change'] >= 1)]

            if positive_changes.empty:
                print(f"No positive changes found for {symbol}.")
                continue

            print(f"\n5-Minute Interval Data with >= 1% Positive Change for {symbol} on {specified_date.date()}:")
            for index, change_row in positive_changes.iterrows():
                print(f"Time: {index}, Price Change: {change_row['price_change']:.2f}%, Volume Change: {change_row['volume_change']:.2f}%")

        except Exception as e:
            logging.error(f"Error fetching 5-minute data for {symbol}: {e}")
            print(f"Error fetching data for {symbol}: {e}")

    # Example usage 
start_date = dt.datetime(2024, 10, 17)  # Example start date
specified_date = dt.datetime(2024, 10, 18, 15, 30)  # Example specified date with time
             

print_high_growth_stocks(shares, start_date, specified_date)
all_high_growth_stocks = high_growth_stocks  # Assuming high_growth_stocks is your full list

print_5min_interval_data_for_high_growth_stocks(all_high_growth_stocks, specified_date)

#print_5min_v_interval_data_for_high_growth_stocks(all_high_growth_stocks, specified_date)

#print_5min_pv_interval_data_for_high_growth_stocks(all_high_growth_stocks, specified_date)



def calculate_vwap(data):
    """Calculate the Volume Weighted Average Price (VWAP)."""
    data['cum_volume'] = data['volume'].cumsum()
    data['cum_value'] = (data['close'] * data['volume']).cumsum()
    data['vwap'] = data['cum_value'] / data['cum_volume']
    return data

def fetch_historical_data(ticker, interval, start_date, end_date):
    """Fetch historical data and calculate VWAP."""
    instrument = kite.ltp(f"NSE:{ticker}")['NSE:' + ticker]['instrument_token']  # Get the instrument token
    data = kite.historical_data(instrument, start_date, end_date, interval)
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)

    # Calculate VWAP
    df = calculate_vwap(df)

    return df[['close', 'volume', 'vwap']]


def check_valid_ticker(ticker):
    try:
        ltp = kite.ltp(f"NSE:{ticker}")
        return f"NSE:{ticker}" in ltp
    except Exception as e:
        print(f"Error checking LTP for {ticker}: {e}")
        return False


if __name__ == "__main__":
    interval = "5minute"
    start_date = dt.datetime(2024, 10, 10)  # Example start date
    specified_date = dt.datetime(2024, 10, 11)  # Example specified date with time

    # Loop through each stock and fetch VWAP data
    for index, row in high_growth_stocks.iterrows():
        ticker = row['Symbol']
        if check_valid_ticker(ticker):  # Validate the ticker
            try:
                vwap_data = fetch_historical_data(ticker, interval, start_date, specified_date)
                if vwap_data is not None:
                    high_growth_stocks.at[index, 'VWAP Data'] = vwap_data  # Store VWAP data
                    print(f"VWAP data for {ticker}:")
                    print(vwap_data.head())  # Display the first few rows with VWAP
                else:
                    print(f"No VWAP data available for {ticker}.")
            except Exception as e:
                print(f"Error fetching data for {ticker}: {str(e)}")
        else:
            print(f"Invalid ticker: {ticker}")
