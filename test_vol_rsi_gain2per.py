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
import datetime as dt
import datetime

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


def get_last_closing_price(ticker, start_date, end_date):
    """
    Function to get the last closing price of a stock.
    
    Args:
        ticker (str): The stock symbol to fetch the last closing price.
        start_date (datetime): The start date for fetching historical data.
        end_date (datetime): The end date for fetching historical data.
        
    Returns:
        float: The last closing price or None if not available.
    """
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
def fetch_live_price(symbol):
    """Fetches the current live price of the given stock."""
    try:
        instrument = instrument_lookup(instrument_df, symbol)
        live_price_data = kite.ltp(f"NSE:{symbol}")
        return live_price_data[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        logging.error(f"Error fetching live price for {symbol}: {e}")
        return None
  
# Function to get live price using the Kite API
def get_live_price(ticker):
    try:
        live_price_data = kite.ltp(f"NSE:{ticker}")
        live_price = live_price_data[f'NSE:{ticker}']['last_price']
        return live_price
    except Exception as e:
        logging.error(f"Error fetching live price for {ticker}: {e}")
        return None  
    
def get_token_for_share(share):
    """
    Function to get the instrument token for a given stock symbol (share).
    Assumes 'instrument_df' is a DataFrame containing instrument data with columns 'tradingsymbol' and 'instrument_token'.
    """
    try:
        # Assuming 'instrument_df' is already loaded and contains 'tradingsymbol' and 'instrument_token' columns
        token = instrument_df[instrument_df['tradingsymbol'] == share]['instrument_token'].values[0]
        return token
    except IndexError:
        print(f"Token not found for {share}")
        return None
    
    
# Function to fetch historical data from Zerodha
def fetch_historical_data(ticker, token, interval="day", duration="6month"):
    """Fetch historical data using Zerodha Kite API."""
    end_date = datetime.date.today()
    start_date = end_date - pd.DateOffset(months=6)
    data = kite.historical_data(token, start_date, end_date, interval)
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    return df  



# Dictionary to store OHLCV data
ohlcv_data = {}


# Loop through each share and get the token
for share in shares:
    token = get_token_for_share(share)
    if token:
        print(f"Token for {share}: {token}")
    else:
        print(f"No token found for {share}")
  
def calculate_30_day_sma_volume(ticker, start_date, end_date):
    """
    Function to calculate 30-day simple moving average of volume for a given stock.
    
    Args:
        ticker (str): The stock symbol for which the SMA of volume is to be calculated.
        start_date (datetime): The start date for fetching historical data.
        end_date (datetime): The end date for fetching historical data.

    Returns:
        pd.DataFrame: A DataFrame with the 30-day SMA of the volume for the given stock.
    """
    try:
        # Fetch OHLC data for the stock
        data = fetch_ohlc(ticker, "day", start_date, end_date)
        
        if data is not None and not data.empty:
            # Calculate the 30-day SMA of the volume
            data['30_day_sma_volume'] = data['volume'].rolling(window=30).mean()

            # Return only relevant columns: volume and 30-day SMA of volume
            return data[['volume', '30_day_sma_volume']].tail(30)
        else:
            logging.error(f"No data available for {ticker}")
            return pd.DataFrame()

    except Exception as e:
        logging.error(f"Error calculating 30day SMA for {ticker}: {e}")
        return pd.DataFrame()



def filter_and_store_growth_stocks(input_file='high_volume_stocks.csv', output_file='volume_price_growth_stocks.csv'):
    """
    Function to compare last close price with current price from high_volume_stocks.csv
    and store stocks with more than 2% price growth in a new CSV file.
    
    Args:
        input_file (str): The CSV file containing high volume stock data.
        output_file (str): The CSV file to store the selected growth stocks.
        
    Returns:
        None
    """
    try:
        # Read the high volume stocks data
        df = pd.read_csv(input_file)

        # Ensure the required columns are present
        required_columns = ['ticker', 'current_volume', 'sma_volume', 'last_close_price', 'current_price']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"CSV file does not contain required column: {col}")

        # Calculate percentage growth
        df['percentage_growth'] = ((df['current_price'] - df['last_close_price']) / df['last_close_price']) * 100

        # Filter stocks with more than 2% growth
        growth_stocks = df[df['percentage_growth'] > 2]

        # If there are stocks meeting the criteria, sort and save to new CSV file
        if not growth_stocks.empty:
            # Sort by percentage growth in descending order
            growth_stocks_sorted = growth_stocks.sort_values(by='percentage_growth', ascending=False)

            # Save to CSV
            growth_stocks_sorted.to_csv(output_file, index=False)
            print(f"Stocks with more than 2% growth saved to {output_file}:")
            print(growth_stocks_sorted[['ticker', 'last_close_price', 'current_price', 'percentage_growth']])
        else:
            print("No stocks with more than 2% growth found.")

    except Exception as e:
        print(f"Error processing the stocks data: {e}")

# Example usage
filter_and_store_growth_stocks()


# Function to filter and store the selected stocks
def store_high_volume_stocks(start_date, end_date, volume_multiplier=1.3, output_file='high_volume_stocks.csv'):
    """
    Function to filter and store stocks where the current volume is 1.5 times the 30-day SMA of volume.
    
    Args:
        start_date (datetime): The start date for fetching historical data.
        end_date (datetime): The end date for fetching historical data.
        volume_multiplier (float): Multiplier to compare the current volume with the 30-day SMA.
        output_file (str): The file path to store the selected stocks.
        
    Returns:
        None
    """
    selected_stocks = []

    for stock in shares:
        result = select_high_volume_stocks(stock, start_date, end_date, volume_multiplier)

        if result is not None:
            selected_stocks.append(result)

    # Convert the selected stocks list to a DataFrame and store it as a CSV
    if selected_stocks:
        df = pd.DataFrame(selected_stocks)
        df.to_csv(output_file, index=False)
        print(f"Selected high-volume stocks saved to {output_file}")
    else:
        print("No stocks met the criteria.")



# Example usage
start_date = dt.datetime(2024, 8, 15)  # Set appropriate start date
end_date = dt.datetime(2024, 10, 17)  # Set appropriate end date (today's date)

# Store stocks with current volume 1.5x of 30-day SMA
store_high_volume_stocks(start_date, end_date)




def filter_and_store_growth_stocks(input_file='high_volume_stocks.csv', output_file='volume_price_growth_stocks.csv'):
    """
    Function to compare last close price with current price from high_volume_stocks.csv
    and store stocks with more than 2% price growth in a new CSV file.
    
    Args:
        input_file (str): The CSV file containing high volume stock data.
        output_file (str): The CSV file to store the selected growth stocks.
        
    Returns:
        None
    """
    try:
        # Read the high volume stocks data
        df = pd.read_csv(input_file)

        # Ensure the required columns are present
        required_columns = ['ticker', 'current_volume', 'sma_volume', 'last_close_price', 'current_price']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"CSV file does not contain required column: {col}")

        # Calculate percentage growth
        df['percentage_growth'] = ((df['current_price'] - df['last_close_price']) / df['last_close_price']) * 100

        # Filter stocks with more than 2% growth
        growth_stocks = df[df['percentage_growth'] > 2]

        # If there are stocks meeting the criteria, sort and save to new CSV file
        if not growth_stocks.empty:
            # Sort by percentage growth in descending order
            growth_stocks_sorted = growth_stocks.sort_values(by='percentage_growth', ascending=False)

            # Save to CSV
            growth_stocks_sorted.to_csv(output_file, index=False)
            print(f"Stocks with more than 2% growth saved to {output_file}:")
            print(growth_stocks_sorted[['ticker', 'last_close_price', 'current_price', 'percentage_growth']])
        else:
            print("No stocks with more than 2% growth found.")

    except Exception as e:
        print(f"Error processing the stocks data: {e}")

# Example usage
filter_and_store_growth_stocks()


# Function to calculate RSI using Exponential Weighted Moving Average (EWM)
def RSI(DF, n=14):
    """Function to calculate RSI using Exponential Weighted Moving Average (EWM)"""
    df = DF.copy()
    
    # Calculating changes in 'close' prices
    df['change'] = df['close'].diff()
    
    # Calculating gains and losses
    df['gain'] = np.where(df['change'] > 0, df['change'], 0)
    df['loss'] = np.where(df['change'] < 0, -df['change'], 0)
    
    # Calculate Exponential Moving Averages of gains and losses using EWM
    df['avgGain'] = df['gain'].ewm(alpha=1/n, min_periods=n).mean()
    df['avgLoss'] = df['loss'].ewm(alpha=1/n, min_periods=n).mean()

    # Calculate Relative Strength (RS)
    df['rs'] = df['avgGain'] / df['avgLoss']
    
    # Calculate RSI based on RS
    df['rsi'] = 100 - (100 / (1 + df['rs']))
    
    return df['rsi']


# Apply RSI function to all tickers in the dictionary
for shares in ohlcv_data:
    ohlcv_data[shares]['RSI'] = RSI(ohlcv_data[shares])

# Load the shares from the CSV file
input_csv_file = 'volume_price_growth_stocks.csv'
stocks_data = pd.read_csv(input_csv_file)

# Initialize an empty DataFrame to store results
rsi_results = pd.DataFrame(columns=['ticker', 'current_volume', 'sma_volume', 'last_close_price', 'current_price', 'RSI'])

# Loop through each stock in the DataFrame
for index, row in stocks_data.iterrows():
    ticker = row['ticker']
    current_volume = row['current_volume']
    sma_volume = row['sma_volume']
    last_close_price = row['last_close_price']
    current_price = row['current_price']
    
    start_date = get_last_trading_day() - dt.timedelta(days=50)  # Last 50 days
    end_date = get_last_trading_day()

    # Fetch OHLC data for the current ticker
    ohlc_data = fetch_ohlc(ticker, 'day', start_date, end_date)
    
    if ohlc_data is not None and not ohlc_data.empty:
        rsi_data = RSI(ohlc_data)
        
        if 'close' in rsi_data.columns and 'RSI' in rsi_data.columns and 'RSI_SMA' in rsi_data.columns:
            current_rsi = rsi_data['RSI'].iloc[-1]  # Get the latest RSI value
            
            # Create a new DataFrame for the current stock's data
            current_data = pd.DataFrame({
                'ticker': [ticker],
                'current_volume': [current_volume],
                'sma_volume': [sma_volume],
                'last_close_price': [last_close_price],
                'current_price': [current_price],
                'RSI': [current_rsi]
            })
            
            # Concatenate the current data with the results DataFrame
            rsi_results = pd.concat([rsi_results, current_data], ignore_index=True)
        else:
            print(f"RSI calculation did not produce expected columns for {ticker}.")
    else:
        print(f"OHLC data is empty or None for {ticker}.")

# Store the RSI results in a new CSV file
output_csv_file = 'rsi_results.csv'
rsi_results.to_csv(output_csv_file, index=False)

print(f"RSI values stored in {output_csv_file}.")