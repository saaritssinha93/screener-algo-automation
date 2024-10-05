# -*- coding: utf-8 -*-
# =============================================================================
# Import OHLCV data and perform basic visualizations
# Author : Saarit

# =============================================================================

import datetime as dt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt  # Importing matplotlib to show plots

tickers = ["AMZN", "MSFT", "META", "GOOG"]
start = dt.datetime.today() - dt.timedelta(3650)
end = dt.datetime.today()
cl_price = pd.DataFrame()  # empty dataframe which will be filled with closing prices of each stock

# Looping over tickers and creating a dataframe with close prices
for ticker in tickers:
    cl_price[ticker] = yf.download(ticker, start, end)["Adj Close"]

# Dropping NaN values
cl_price.dropna(axis=0, how='any', inplace=True)

# Return calculation
daily_return = cl_price.pct_change()  # Creates dataframe with daily return for each stock

# Plotting close prices
cl_price.plot()
plt.title("Closing Prices of Stocks")
plt.xlabel("Date")
plt.ylabel("Adjusted Close Price")
plt.show()  # Show the plot

# Plotting close prices with subplots
cl_price.plot(
    subplots=True,       # Separate plots for each stock
    layout=(2, 2),       # 2x2 grid layout
    title="Stock Price Evolution",  # Title for the plot
    grid=True            # Enable grid
)

plt.tight_layout()  # Adjust layout to prevent overlap
plt.show()  # Display the plots

  
#plotting daily returns and cumulative returns    
# Plotting daily returns
daily_return.plot(
    title="Daily Stock Returns",  # Adding a title for clarity
    grid=True                     # Enabling grid for better readability
)

plt.show()  # Display the plot

# Plotting daily returns with subplots for each stock
daily_return.plot(
    subplots=True,                # Create individual subplots for each stock
    layout=(2, 2),                # Arrange subplots in a 2x2 grid
    title="Daily Stock Returns",   # Title for each subplot
    grid=True,                    # Enable grid for better readability
    figsize=(10, 8)               # Adjust figure size for better spacing
)

plt.tight_layout()  # Automatically adjust subplot parameters to fit the figure area
plt.show()  # Display the plot

# Plotting cumulative returns (Stock Price Evolution) without subplots
(1 + daily_return).cumprod().plot(
    title="Stock Price Evolution", # Title for the plot
    grid=True,                     # Enable grid for better readability
    figsize=(10, 6)                # Adjust figure size for better visualization
)

plt.show()  # Display the plot


# Plotting cumulative returns (Stock Price Evolution) with subplots
(1 + daily_return).cumprod().plot(
    subplots=True,                 # Create individual subplots for each stock
    layout=(2, 2),                 # Arrange subplots in a 2x2 grid
    title="Stock Price Evolution", # Title for each subplot
    grid=True,                     # Enable grid for better readability
    figsize=(10, 8)                # Adjust figure size for better spacing
)

plt.tight_layout()  # Automatically adjust subplot parameters to fit the figure area
plt.show()  # Display the plot