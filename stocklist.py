# -*- coding: utf-8 -*-
"""
Fetch list of all stocks from NSE and BSE using Zerodha Kite Connect API.
"""

import logging
import os
import pandas as pd
from kiteconnect import KiteConnect
import re  # Import the regular expression module

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

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

# Fetch instruments from NSE and BSE
try:
    nse_instruments = kite.instruments("NSE")
    bse_instruments = kite.instruments("BSE")
    
    # Convert to DataFrame for better handling
    nse_df = pd.DataFrame(nse_instruments)
    bse_df = pd.DataFrame(bse_instruments)

    # Filter out ETFs, SG (Securities with Special Tax Treatment), mutual funds, indices, commodities, currencies, and INAV stocks
    nse_df = nse_df[~nse_df['segment'].isin(['ETF', 'SG', 'MF', 'INDEX', 'COMMODITY', 'CURRENCY'])]
    bse_df = bse_df[~bse_df['segment'].isin(['ETF', 'SG', 'MF', 'INDEX', 'COMMODITY', 'CURRENCY'])]
    
    nse_df = nse_df[~nse_df['tradingsymbol'].str.contains('INAV', regex=False)]
    bse_df = bse_df[~bse_df['tradingsymbol'].str.contains('INAV', regex=False)]

    # Remove stocks with numerals in their symbols
    nse_df = nse_df[~nse_df['tradingsymbol'].str.contains(r'\d', regex=True)]
    bse_df = bse_df[~bse_df['tradingsymbol'].str.contains(r'\d', regex=True)]

    # Extract trading symbols
    nse_shares = set(nse_df['tradingsymbol'].tolist())
    bse_shares = set(bse_df['tradingsymbol'].tolist())

    # Remove common stocks
    unique_bse_shares = bse_shares - nse_shares

    # Print the shares in the desired format
    print(f"NSE shares: {nse_shares}")
    print(f"Total count of NSE stocks: {len(nse_shares)}")
    
    print(f"Unique BSE shares (not in NSE): {list(unique_bse_shares)}")
    print(f"Total count of unique BSE stocks: {len(unique_bse_shares)}")

    # Optionally, save to CSV
    nse_df.to_csv('nse_instruments.csv', index=False)
    bse_df[bse_df['tradingsymbol'].isin(unique_bse_shares)].to_csv('unique_bse_instruments.csv', index=False)
    
    logging.info("Instruments fetched successfully and saved to nse_instruments.csv and unique_bse_instruments.csv.")

except Exception as e:
    logging.error(f"Error fetching instruments: {e}")
