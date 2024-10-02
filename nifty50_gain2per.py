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
        data.set_index("date", inplace=True)
        logging.info(f"OHLC data fetched for {ticker}")
        return data
    except Exception as e:
        logging.error(f"Error fetching OHLC data for {ticker}: {e}")
        return None

# New Function to find Nifty 50 stocks with 2% or more gain since 30th September
def fetch_nifty50_gainers(percent=2, target_date=None):
    """Fetches Nifty 50 stocks where today's price is 2% or more than 30th September."""
    if target_date is None:
        target_date = dt.date(2024, 9, 30)  # Set 30th September as the default target date
    
    gainers = []
    
    # Iterate over Nifty 50 stocks only
    for symbol in nifty50_stocks:
        try:
            # Fetch OHLC data from 30th September to today
            start_date = target_date
            end_date = dt.date.today()
            ohlc_data = fetch_ohlc(symbol, "day", start_date, end_date)  # Fetch data from 30th September
            
            if ohlc_data is None or len(ohlc_data) < 2:
                continue  # Skip if there's insufficient data
            
            # Get today's and 30th September's closing prices
            today_close = ohlc_data['close'].iloc[-1]
            if str(target_date) in ohlc_data.index:
                sep30_close = ohlc_data.loc[str(target_date), 'close']
            else:
                logging.warning(f"No data for 30th September for {symbol}")
                continue
            
            # Calculate percentage gain
            percent_change = ((today_close - sep30_close) / sep30_close) * 100
            
            # Check if gain is 2% or more
            if percent_change >= percent:
                gainers.append((symbol, percent_change))
                logging.info(f"{symbol} gained {percent_change:.2f}% since 30th September")
        
        except Exception as e:
            logging.error(f"Error processing {symbol}: {e}")
            continue
    
    return pd.DataFrame(gainers, columns=['Stock', 'Percent Change'])

# Example usage: Fetch Nifty 50 gainers with 2% or more increase since 30th September
gainers_df = fetch_nifty50_gainers(2)
if not gainers_df.empty:
    print(gainers_df)
else:
    logging.info("No Nifty 50 gainers found with 2% or more increase since 30th September.")




















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
        data.set_index("date", inplace=True)
        logging.info(f"OHLC data fetched for {ticker}")
        return data
    except Exception as e:
        logging.error(f"Error fetching OHLC data for {ticker}: {e}")
        return None

# New Function to find Nifty 50 stocks with 2% or more gain since yesterday
def fetch_nifty50_gainers(percent=2):
    """Fetches Nifty 50 stocks where today's price is 2% or more than yesterday's closing price."""
    
    # Set yesterday's date
    yesterday = dt.date.today() - dt.timedelta(days=1)
    
    gainers = []
    
    # Iterate over Nifty 50 stocks only
    for symbol in nifty50_stocks:
        try:
            # Fetch OHLC data from yesterday to today
            start_date = yesterday
            end_date = dt.date.today()
            ohlc_data = fetch_ohlc(symbol, "day", start_date, end_date)  # Fetch data from yesterday
            
            if ohlc_data is None or len(ohlc_data) < 2:
                continue  # Skip if there's insufficient data
            
            # Get today's and yesterday's closing prices
            today_close = ohlc_data['close'].iloc[-1]
            if str(yesterday) in ohlc_data.index:
                yesterday_close = ohlc_data.loc[str(yesterday), 'close']
            else:
                logging.warning(f"No data for yesterday ({yesterday}) for {symbol}")
                continue
            
            # Calculate percentage gain
            percent_change = ((today_close - yesterday_close) / yesterday_close) * 100
            
            # Check if gain is 2% or more
            if percent_change >= percent:
                gainers.append((symbol, percent_change))
                logging.info(f"{symbol} gained {percent_change:.2f}% since yesterday")
        
        except Exception as e:
            logging.error(f"Error processing {symbol}: {e}")
            continue
    
    return pd.DataFrame(gainers, columns=['Stock', 'Percent Change'])

# Example usage: Fetch Nifty 50 gainers with 2% or more increase since yesterday
gainers_df = fetch_nifty50_gainers(2)
if not gainers_df.empty:
    print(gainers_df)
else:
    logging.info("No Nifty 50 gainers found with 2% or more increase since yesterday.")