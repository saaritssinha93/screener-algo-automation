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

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

# Stocks to analyze
shares = ['AARTIDRUGS', 'AARTISURF-BE', 'ABFRL', 'ADANIPOWER', 'ADVENZYMES', 
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
'WIPRO', 'ZENSARTECH']

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

# Function to fetch OHLC data
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

# Initialize a list to store results
results = []

# Loop through each stock in the shares list
for ticker in shares:
    end_date = dt.datetime.today()  # Use the current date as the end date
    start_date = end_date - dt.timedelta(days=180)  # 6 months ago (approximately 180 days)
    
    # Fetch OHLC data for the current ticker
    ohlc_data = fetch_ohlc(ticker, 'day', start_date, end_date)
    
    if ohlc_data is not None and not ohlc_data.empty:
        # Calculate RSI
        ohlc_data['RSI'] = RSI(ohlc_data)
        
        if 'RSI' in ohlc_data.columns:
            current_rsi = ohlc_data['RSI'].iloc[-1]  # Get the latest RSI value
            
            # Append the results to the list
            results.append({
                'Ticker': ticker,
                'Last Close Price': ohlc_data['close'].iloc[-1],
                'Current Price': ohlc_data['close'].iloc[-1],
                'RSI': current_rsi
            })
        else:
            print(f"RSI calculation did not produce expected results for {ticker}.")
    else:
        print(f"OHLC data is empty or None for {ticker}.")

# Create a DataFrame from the results list
results_df = pd.DataFrame(results)

# Store the results in an output CSV file
output_csv_file = 'output.csv'
results_df.to_csv(output_csv_file, index=False)

print(f"RSI values stored in {output_csv_file}.")

import pandas as pd
import numpy as np

def find_divergence(price_data, rsi_data):
    """
    Function to detect RSI divergence.
    Looks for price making higher highs or lower lows while RSI makes lower highs or higher lows.
    
    Args:
        price_data (pd.Series): Series of closing prices.
        rsi_data (pd.Series): Series of RSI values.
    
    Returns:
        str: 'bullish_divergence', 'bearish_divergence', or 'no_divergence'.
    """
    if len(price_data) < 3 or len(rsi_data) < 3:
        return 'no_divergence'

    # Find local peaks and troughs in price
    price_highs = (price_data.shift(1) < price_data) & (price_data.shift(-1) < price_data)
    price_lows = (price_data.shift(1) > price_data) & (price_data.shift(-1) > price_data)

    # Find local peaks and troughs in RSI
    rsi_highs = (rsi_data.shift(1) < rsi_data) & (rsi_data.shift(-1) < rsi_data)
    rsi_lows = (rsi_data.shift(1) > rsi_data) & (rsi_data.shift(-1) > rsi_data)

    # Check for bearish divergence (price higher highs, RSI lower highs)
    if price_highs.iloc[-3:].sum() > 0 and rsi_highs.iloc[-3:].sum() > 0:
        recent_price_high = price_data[price_highs].iloc[-1]
        previous_price_high = price_data[price_highs].iloc[-2]
        recent_rsi_high = rsi_data[rsi_highs].iloc[-1]
        previous_rsi_high = rsi_data[rsi_highs].iloc[-2]

        if recent_price_high > previous_price_high and recent_rsi_high < previous_rsi_high:
            return 'bearish_divergence'

    # Check for bullish divergence (price lower lows, RSI higher lows)
    if price_lows.iloc[-3:].sum() > 0 and rsi_lows.iloc[-3:].sum() > 0:
        recent_price_low = price_data[price_lows].iloc[-1]
        previous_price_low = price_data[price_lows].iloc[-2]
        recent_rsi_low = rsi_data[rsi_lows].iloc[-1]
        previous_rsi_low = rsi_data[rsi_lows].iloc[-2]

        if recent_price_low < previous_price_low and recent_rsi_low > previous_rsi_low:
            return 'bullish_divergence'

    return 'no_divergence'


# Initialize a list to store results
results = []

# Loop through each stock in the shares list
for ticker in shares:
    end_date = dt.datetime.today()  # Use the current date as the end date
    start_date = end_date - dt.timedelta(days=180)  # 6 months ago (approximately 180 days)
    
    # Fetch OHLC data for the current ticker
    ohlc_data = fetch_ohlc(ticker, 'day', start_date, end_date)
    
    if ohlc_data is not None and not ohlc_data.empty:
        # Calculate RSI
        ohlc_data['RSI'] = RSI(ohlc_data)
        
        if 'RSI' in ohlc_data.columns:
            current_rsi = ohlc_data['RSI'].iloc[-1]  # Get the latest RSI value
            
            # Check for RSI divergence
            divergence_status = find_divergence(ohlc_data['close'], ohlc_data['RSI'])
            
            # Store only if divergence is not 'no_divergence'
            if divergence_status != 'no_divergence':
                results.append({
                    'Ticker': ticker,
                    'Last Close Price': ohlc_data['close'].iloc[-1],
                    'Current Price': ohlc_data['close'].iloc[-1],
                    'RSI': current_rsi,
                    'Divergence': divergence_status
                })
        else:
            print(f"RSI calculation did not produce expected results for {ticker}.")
    else:
        print(f"OHLC data is empty or None for {ticker}.")

# Create a DataFrame from the results list
results_df = pd.DataFrame(results)

# Store the results in an output CSV file
output_csv_file = 'output.csv'
results_df.to_csv(output_csv_file, index=False)

print(f"RSI values stored in {output_csv_file}.")
