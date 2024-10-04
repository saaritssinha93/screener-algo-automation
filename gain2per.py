# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication with a task running every 5 minutes
"""

import schedule
import time
from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd
import csv

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

# Stocks
shares = [
    'AARTIDRUGS', 'AARTISURF', 'ABFRL', 'ADANIPOWER', 'ADVENZYMES', 
    'AFFLE', 'AGARIND', 'AJMERA', 'ALEMBICLTD', 'ARE&M', 
    'ANANTRAJ', 'APCOTEXIND', 'APLAPOLLO', 'ARCHIDPLY', 'ASHOKA',
    'ASIANHOTNR', 'ASTERDM', 'AUROPHARMA', 'AXISBANK', 'BALAJIAMINES', 
    'BALAMINES', 'BALRAMCHIN', 'BANCOINDIA', 'BASF', 'BATAINDIA',
    'BAYERCROP', 'BCG', 'BDL', 'BEL', 'BEML',
    'BERGEPAINT', 'BFUTILITIE', 'BGRENERGY', 'BHAGERIA', 'BHARATGEAR',
    'BIRLAMONEY', 'BLUESTARCO', 'BOROSIL', 'BRIGADE', 'BSOFT',
    'CAPLIPOINT', 'CARYSIL', 'CEATLTD', 'CENTUM', 'CHALET',
    'CHEMCON', 'CHEMFAB', 'CHEMPLASTS', 'CHOLAHLDNG', 'CIMMCO',
    'COCHINSHIP', 'COFORGE', 'COSMOFILMS', 'CROMPTON', 'CSBBANK',
    'CYIENT', 'DAAWAT', 'DCAL', 'DEEPAKFERT', 'DELTACORP',
    'DENORA', 'DISHTV', 'DOLLAR', 'DPSCLTD', 'DREDGECORP',
    'DYNPRO', 'ECLERX', 'EDELWEISS', 'EIDPARRY', 'EIHOTEL',
    'ELGIEQUIP', 'EMAMILTD', 'EMIL', 'ENDURANCE', 'ENGINERSIN',
    'ERIS', 'ESABINDIA', 'FCONSUMER', 'FEDERALBNK', 'FIEMIND',
    'FINPIPE', 'FLUOROCHEM', 'GABRIEL', 'GAIL', 'GALAXYSURF',
    'GARFIBRES', 'GDL', 'GEPOWER', 'GHCL', 'GICHSGFIN',
    'GILLETTE', 'GIPCL', 'GLS', 'GNA', 'GNFC',
    'GODFRYPHLP', 'GOODYEAR', 'GRAUWEIL', 'GRINDWELL', 'GSKCONS',
    'GTPL', 'GUFICBIO', 'GULFOILLUB', 'HAPPSTMNDS', 'HARRMALAYA',
    'HATSUN', 'HERCULES', 'HERITGFOOD', 'HFCL', 'HIKAL',
    'HINDCOPPER', 'HINDZINC', 'HMVL', 'HOEC', 'HONAUT',
    'HSIL', 'ICIL', 'ICRA', 'IDBI', 'IDFC',
    'IFBIND', 'IIFL', 'IL&FSENGG', 'IMFA', 'INDIANB',
    'INDIANCARD', 'INDIGO', 'INDORAMA', 'INDOSTAR', 'INEOSSTYRO',
    'INFIBEAM', 'INTELLECT', 'IRB', 'IRCON', 'ISEC',
    'ITI', 'J&KBANK', 'JAICORPLTD', 'JAMNAAUTO', 'JASH',
    'JBCHEPHARM', 'JETAIRWAYS', 'JINDALPHOT', 'JISLJALEQS', 'JKCEMENT',
    'JKLAKSHMI', 'JKPAPER', 'JMFINANCIL', 'JSL', 'JTEKTINDIA',
    'JUBLFOOD', 'JUBLINDS', 'KABRAEXTRU', 'KAJARIACER', 'KALPATPOWR',
    'KANSAINER', 'KARDA', 'KEI', 'KIRLOSENG', 'KITEX',
    'KNRCON', 'KOKUYOCMLN', 'KOLTEPATIL', 'KOPRAN', 'KRBL',
    'KSB', 'L&TFH', 'LAOPALA', 'LEMONTREE', 'LINDEINDIA',
    'LUXIND', 'M&MFIN', 'MAHABANK', 'MAHINDCIE', 'MAHSCOOTER',
    'MAITHANALL', 'MANAKSIA', 'MARKSANS', 'MASTEK', 'MAYURUNIQ',
    'MAZDOCK', 'MBAPL', 'MCDOWELL-N', 'MINDACORP', 'MINDAIND',
    'MOLDTEK', 'MONTECARLO', 'MOREPENLAB', 'MOTILALOFS', 'MPHASIS',
    'MRPL', 'MSTC', 'MTARTECH', 'MUKANDLTD', 'MUNJALSHOW',
    'NATCOPHARM', 'NATIONALUM', 'NBCC', 'NCC', 'NDL',
    'NELCO', 'NESCO', 'NESTLEIND', 'NLCINDIA', 'NMDC',
    'NOCIL', 'NRAIL', 'NTPC', 'NUCLEUS', 'OBEROIRLTY',
    'OIL', 'OLECTRA', 'OMAXE', 'ONGC', 'ORIENTCEM',
    'ORIENTELEC', 'ORTINLAB', 'PAGEIND', 'PANAMAPET', 'PARAGMILK',
    'PCJEWELLER', 'PDSL', 'PEL', 'PERSISTENT', 'PETRONET',
    'PFIZER', 'PHILIPCARB', 'PILANIINVS', 'PNBHOUSING', 'POLYCAB',
    'POWERINDIA', 'PRAJIND', 'PRECOT', 'PRSMJOHNSN', 'PTC',
    'RAILTEL', 'RAIN', 'RALLIS', 'RANEHOLDIN', 'RATNAMANI',
    'RAYMOND', 'RECLTD', 'RELAXO', 'RELINFRA', 'RENUKA',
    'RHFL', 'RITES', 'ROSSARI', 'RTNPOWER', 'RUCHI',
    'RVNL', 'SAGCEM', 'SANOFI', 'SARDAEN', 'SBICARD',
    'SCI', 'SEQUENT', 'SHILPAMED', 'SHOPERSTOP', 'SHREDIGCEM',
    'SHRIRAMEPC', 'SHYAMMETL', 'SIEMENS', 'SIS', 'SJS',
    'SKFINDIA', 'SOBHA', 'SOLARA', 'SONACOMS', 'SOUTHBANK',
    'SPAL', 'SPARC', 'SRHHYPOLTD', 'SRTRANSFIN', 'STAR',
    'STCINDIA', 'STLTECH', 'SUBEXLTD', 'SUDARSCHEM', 'SUNDRMFAST',
    'SUNPHARMA', 'SUPPETRO', 'SUPRAJIT', 'SUVEN', 'SWARAJENG',
    'SYMPHONY', 'TANLA', 'TATAINVEST', 'TATACOFFEE', 'TATAMETALI',
    'TATAPOWER', 'TATASTEEL', 'TCS', 'TECHM', 'TEGA',
    'THEINVEST', 'THERMAX', 'TIMKEN', 'TITAN', 'TORNTPOWER',
    'TRENT', 'TRITURBINE', 'TTKPRESTIG', 'TV18BRDCST', 'TVSMOTOR',
    'UCOBANK', 'ULTRACEMCO', 'UNIONBANK', 'UNOMINDA', 'UPL',
    'UJJIVAN', 'VAKRANGEE', 'VARROC', 'VEDL', 'VENKEYS',
    'VGUARD', 'VIKASMCORP', 'VIPIND', 'VOLTAMP', 'VSTIND',
    'WABCOINDIA', 'WALCHANNAG', 'WELCORP', 'WELSPUNIND', 'WHIRLPOOL',
    'WOCKPHARMA', 'YESBANK', 'ZEEL', 'ZENITHSTL', 'ZENTEC',
    # Nifty 50 stocks list
    'ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 
    'BAJAJFINSV', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 
    'COALINDIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GRASIM', 
    'HCLTECH', 'HDFCBANK', 'HDFC', 'HEROMOTOCO', 'HINDALCO', 
    'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY', 
    'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 
    'NESTLEIND', 'NTPC', 'ONGC', 'POWERGRID', 'RELIANCE', 
    'SBILIFE', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 
    'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'ULTRACEMCO', 
    'UPL', 'WIPRO',
    # Top 100 midcap stocks
    'ADANIGREEN', 'ADANIPORTS', 'AJANTPHARM', 'ALKEM', 'AMBUJACEM', 
    'APOLLOHOSP', 'ASHOKLEY', 'ASTRAL', 'ATUL', 'AVANTIFEED',
    'BAJFINANCE', 'BAJFAHFL', 'BANKBARODA', 'BEL', 'BHARATFORG',
    'BHARTIARTL', 'BIRLACORPN', 'ZYDUSLIFE', 'CANFINHOME', 'CEATLTD',
    'CENTRALBK', 'CIPLA', 'COFORGE', 'COLPAL', 'CONCOR',
    'CROMPTON', 'DABUR', 'DCMSHRIRAM', 'DEEPAKNTR', 'DIVISLAB',
    'DIXON', 'DLF', 'EICHERMOT', 'ESCORTS', 'EXIDEIND',
    'GAIL', 'GLAND', 'GLAXO', 'GMRINFRA', 'GRANULES',
    'HAVELLS', 'HDFCLIFE', 'HINDCOPPER', 'HINDPETRO', 'HINDUNILVR',
    'ICICIBANK', 'IGL', 'INDIGO', 'INDUSINDBK', 'INDUSTOWER',
    'IRCTC', 'JINDALSTEL', 'JSLHISAR', 'KEC', 'KIRLOSENG',
    'LTF', 'LT', 'MINDTREE', 'MOTHERSON', 'MUTHOOTFIN',
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
        logging.info(f"Instrument token for {symbol}: {instrument_token}")
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

        if not data.empty:
            logging.info(f"Fetched data columns for {ticker}: {data.columns}")
            data.set_index("date", inplace=True)
            return data
        else:
            logging.error(f"No data returned for {ticker}")
            return pd.DataFrame()

    except Exception as e:
        logging.error(f"Error fetching OHLC data for {ticker}: {e}")
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

# Modify the print_price_comparison function to include volume change
def print_price_comparison(symbol):
    """Prints last market day closing price, current price, and percentage change."""    
    # Find the last trading day
    last_trading_day = get_last_trading_day()
    
    # Set date range for the last trading day and last 15 minutes
    start_date = last_trading_day
    end_date = last_trading_day

    logging.info(f"Fetching data for {symbol} on last trading day: {last_trading_day}")
    
    # Fetch OHLC data for last trading day and today's live price
    ohlc_data = fetch_ohlc(symbol, "day", start_date, end_date)
    volume_data_15m = fetch_ohlc(symbol, "15minute", last_trading_day, last_trading_day)  # Fetch last 15-minute volume

    if ohlc_data is not None and not ohlc_data.empty:
        if 'close' in ohlc_data.columns:
            last_close = ohlc_data['close'].iloc[-1]
            live_price = fetch_live_price(symbol)
            
            if live_price is not None:
                percent_change = ((live_price - last_close) / last_close) * 100
                
                logging.info(f"{symbol}: Last Trading Day Close: {last_close}, Current Price: {live_price}, Percentage Change: {percent_change:.2f}%")
                
                # Check if the percentage change is 2% or more
                if percent_change >= 2:
                    logging.info(f"{symbol} has increased by {percent_change:.2f}%, which is above 2%.")
                    # Volume change logic
                    if volume_data_15m is not None and not volume_data_15m.empty:
                        last_volume = volume_data_15m['volume'].iloc[-1]  # Volume for last 15 minutes
                        last_day_volume = ohlc_data['volume'].iloc[-1]  # Volume for last trading day

                        volume_change = ((last_volume - last_day_volume) / last_day_volume) * 100 if last_day_volume > 0 else float('inf')
                        logging.info(f"Volume Change for {symbol}: {volume_change:.2f}%")
                        
                        # Print the output in a formatted way
                        print(f"{symbol}: Last Close: {last_close}, Current Price: {live_price}, "
                              f"Percentage Change: {percent_change:.2f}%, Volume Change: {volume_change:.2f}%")
                        high_growth_stocks[symbol] = (percent_change, volume_change)  # Store as a tuple
                    else:
                        print(f"{symbol}: Last Close: {last_close}, Current Price: {live_price}, "
                              f"Percentage Change: {percent_change:.2f}%, Volume Change: Data not available")
                else:
                    print(f"{symbol}: Last Close: {last_close}, Current Price: {live_price}, "
                          f"Percentage Change: {percent_change:.2f}%, Volume Change: Data not available")
            else:
                logging.error(f"Could not fetch live price for {symbol}")
        else:
            logging.error(f"'close' column missing in OHLC data for {symbol}")
    else:
        logging.error(f"Could not fetch historical data for {symbol}")

# Modified function to print the high growth stocks
def print_high_growth_stocks():
    """Prints the stocks with a growth of 2% or more along with volume change."""
    logging.info("Stocks with 2% or more increase:")
    if high_growth_stocks:
        for stock, (percent, volume_change) in high_growth_stocks.items():
            print(f"{stock}: {percent:.2f}%   Volume Change: {volume_change:.2f}%")
    else:
        logging.info("No stocks have increased by 2% or more.")
        print("No stocks have increased by 2% or more.")

# Modified function to save stocks with 2% or more change to a CSV file
def save_high_growth_stocks_to_csv():
    """Saves stocks with a percentage change of 2% or more to a CSV file."""
    if high_growth_stocks:
        # Sort stocks by percentage change in descending order
        sorted_stocks = sorted(high_growth_stocks.items(), key=lambda x: x[1][0], reverse=True)
        with open("high_growth_stocks.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Stock', 'Percentage Change (%)', 'Volume Change (%)'])
            for stock, (percent_change, volume_change) in sorted_stocks:
                writer.writerow([stock, percent_change, volume_change])
        logging.info("High growth stocks saved to high_growth_stocks.csv.")
    else:
        logging.info("No stocks to save.")

# Main function to run every 5 minutes
def job():
    """Job to run every 5 minutes."""
    logging.info("Job started.")
    for share in shares:
        print_price_comparison(share)
    print_high_growth_stocks()
    save_high_growth_stocks_to_csv()

# Schedule the job to run every 5 minutes
schedule.every(5).minutes.do(job)

# Start the scheduler
if __name__ == "__main__":
    logging.info("Scheduler started.")
    while True:
        schedule.run_pending()
        time.sleep(1)