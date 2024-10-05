# -*- coding: utf-8 -*-
"""
Handling NaN values
@author: Saarit
"""

import datetime as dt
import yfinance as yf
import pandas as pd

# Replace 'FB' with 'META'
stocks = ["AMZN", "MSFT", "META", "GOOG"]
start = dt.datetime.today() - dt.timedelta(4745)
end = dt.datetime.today()
cl_price = pd.DataFrame()  # Empty dataframe to hold closing prices

# Looping over tickers and creating a dataframe with close prices
for ticker in stocks:
    cl_price[ticker] = yf.download(ticker, start, end)["Adj Close"]

# Filling NaN values with backward fill
cl_price.bfill(axis=0, inplace=True)

# Check the resulting dataframe
print(cl_price.head())


# Dropping rows with NaN values
cl_price.dropna(axis=0, how='any', inplace=True)

# Check the resulting dataframe
print(cl_price.head())