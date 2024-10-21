# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 16:02:49 2024

@author: Saarit
"""

import logging
import os
import pandas as pd

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

# Set up logging to a file
logging.basicConfig(filename='trading_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

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

def main():
    
    logging.info("Starting the trading algorithm...")
    filter_and_store_growth_stocks()  # Call the function to filter and store growth stocks

if __name__ == "__main__":
    main()
    logging.shutdown()
