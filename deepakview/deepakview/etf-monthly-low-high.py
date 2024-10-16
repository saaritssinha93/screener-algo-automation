import yfinance as yf
import pandas as pd

# Step 1: Fetch NiftyBees data from Jan 1, 2024 to Oct 15, 2024
def fetch_niftybees_data():
    # Fetch historical data for NiftyBees ETF (ticker: NIFTYBEES.NS)
    niftybees = yf.Ticker("NIFTYBEES.NS")
    
    # Define the date range (from Jan 1, 2024 to Oct 15, 2024)
    df = niftybees.history(start="2024-01-01", end="2024-12-15", interval="1d")
    
    # Reset the index to make the date a column in the DataFrame
    df.reset_index(inplace=True)
    
    return df

# Step 2: Calculate monthly highs and lows, including the dates
def calculate_monthly_high_low(df):
    # Ensure 'Date' column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Add a 'Month' column for grouping by month
    df['Month'] = df['Date'].dt.to_period('M')
    
    # Initialize an empty list to store results
    monthly_data = []

    # Group by 'Month'
    for month, group in df.groupby('Month'):
        # Find the row with the minimum 'Low' value in the group
        min_row = group.loc[group['Low'].idxmin()]
        # Find the row with the maximum 'High' value in the group
        max_row = group.loc[group['High'].idxmax()]
        
        # Append the month, min and max values, and their corresponding dates
        monthly_data.append({
            'Month': month,
            'Low': min_row['Low'],
            'Low Date': min_row['Date'].strftime('%Y-%m-%d'),
            'High': max_row['High'],
            'High Date': max_row['Date'].strftime('%Y-%m-%d'),
            'Difference': max_row['High'] - min_row['Low']
        })
    
    # Convert to DataFrame
    result_df = pd.DataFrame(monthly_data)

    # Display the result
    print(result_df)

    # Optionally, save to CSV
    result_df.to_csv('niftybees_jan_to_oct_high_low_with_dates.csv', index=False)

# Step 3: Run the functions
df = fetch_niftybees_data()
calculate_monthly_high_low(df)
