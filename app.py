from flask import Flask, render_template, redirect, url_for
import yfinance as yf

app = Flask(__name__)

# List of known ETF symbols on NSE
etfs = [
    'ABGSEC', 'ABSLBANETF', 'ABSLNN50ET', 'ABSLPSE', 'BFSI'
]

# List of bank stocks
stocks = ['HDFCBANK', 'BANKBARODA', 'ICICIBANK', 'YESBANK']

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/etf_list')
def etf_list():
    return render_template('etf_list.html')  # Assuming this template exists

@app.route('/etfdata')
def etf_data():
    etf_data = []

    for etf in etfs:
        try:
            ticker = yf.Ticker(etf + '.NS')  # Adding '.NS' to get NSE data
            info = ticker.info
            
            if not info:
                raise ValueError("No info returned for ticker.")

            data = ticker.history(period='1mo')  # Fetch data for the last month

            if not data.empty:
                historical_prices = data['Close'].tolist()

                # Calculate percentage changes for each day
                percentage_changes = []
                for i in range(1, len(historical_prices)):
                    price_today = historical_prices[i]
                    price_yesterday = historical_prices[i - 1]
                    
                    if price_yesterday > 0:
                        percentage_change = ((price_today - price_yesterday) / price_yesterday) * 100
                        percentage_changes.append(f"{percentage_change:.2f}%")
                    else:
                        percentage_changes.append("N/A")
                
                # Calculate the 1-day percentage change if enough data is available
                if len(historical_prices) >= 2:
                    price_now = historical_prices[-1]  # Current price
                    price_yesterday = historical_prices[-2]  # Price from the previous day

                    if price_yesterday > 0:
                        one_day_change = ((price_now - price_yesterday) / price_yesterday) * 100
                        one_day_change_formatted = f"{one_day_change:.2f}%"
                    else:
                        one_day_change_formatted = "N/A"
                else:
                    one_day_change_formatted = "N/A"  # Not enough data to calculate

                # Calculate the 5-day percentage change if enough data is available
                if len(historical_prices) >= 6:
                    price_5_days_ago = historical_prices[-6]  # Price 5 days ago

                    if price_5_days_ago > 0:
                        five_day_change = ((price_now - price_5_days_ago) / price_5_days_ago) * 100
                        five_day_change_formatted = f"{five_day_change:.2f}%"
                    else:
                        five_day_change_formatted = "N/A"
                else:
                    five_day_change_formatted = "N/A"  # Not enough data to calculate

                # Calculate the 1-month percentage change
                if len(historical_prices) >= 22:  # Approx 22 trading days in a month
                    price_one_month_ago = historical_prices[-22]  # Price 1 month ago

                    if price_one_month_ago > 0:
                        one_month_change = ((price_now - price_one_month_ago) / price_one_month_ago) * 100
                        one_month_change_formatted = f"{one_month_change:.2f}%"
                    else:
                        one_month_change_formatted = "N/A"
                else:
                    one_month_change_formatted = "N/A"  # Not enough data to calculate

                # Format historical prices
                historical_prices_formatted = [f"₹{price:.2f}" for price in historical_prices]

                # Add to the ETF data
                etf_data.append({
                    'name': info.get('longName', 'N/A'),  # Get the long name of the ETF
                    'current_price': f"₹{historical_prices[-1]:.2f}",  # Current price is the last day's price
                    'historical_prices': historical_prices_formatted[::-1],  # Reverse for latest first
                    'percentage_changes': percentage_changes[::-1],  # Reverse for latest first
                    'one_day_change': one_day_change_formatted,  # Add the 1-day change
                    'five_day_change': five_day_change_formatted,  # Add the 5-day change
                    'one_month_change': one_month_change_formatted  # Add the 1-month change
                })
            else:
                etf_data.append({
                    'name': info.get('longName', 'N/A'),
                    'current_price': 'No data',
                    'historical_prices': [],
                    'percentage_changes': ['N/A'],  # No percentage change if no data
                    'one_day_change': 'N/A',  # No 1-day change if no data
                    'five_day_change': 'N/A',  # No 5-day change if no data
                    'one_month_change': 'N/A'  # No 1-month change if no data
                })
        except Exception as e:
            etf_data.append({
                'name': etf,
                'current_price': 'Error fetching data',
                'historical_prices': ['N/A'],
                'percentage_changes': ['N/A'],  # No percentage change if there was an error
                'one_day_change': 'N/A',  # No 1-day change if there was an error
                'five_day_change': 'N/A',  # No 5-day change if there was an error
                'one_month_change': 'N/A'  # No 1-month change if there was an error
            })

    return render_template('etf_data.html', etf_data=etf_data)

@app.route('/etfstatus')
def etf_status():
    etf_status_data = []

    for etf in etfs:
        try:
            ticker = yf.Ticker(etf + '.NS')  # Adding '.NS' to get NSE data
            info = ticker.info
            
            if not info:
                raise ValueError("No info returned for ticker.")

            data = ticker.history(period='2d')  # Fetch data for the last 2 days to calculate today's change

            if not data.empty and len(data) >= 2:
                # Get the closing prices for today and yesterday
                price_today = data['Close'].iloc[-1]
                price_yesterday = data['Close'].iloc[-2]

                # Calculate the 1-day percentage change
                if price_yesterday > 0:
                    one_day_change = ((price_today - price_yesterday) / price_yesterday) * 100
                else:
                    one_day_change = None  # No change if previous price is zero

                # Check if the ETF is down by 2% or more
                if one_day_change is not None and one_day_change <= -.1:
                    etf_status_data.append({
                        'name': info.get('longName', 'N/A'),  # Get the long name of the ETF
                        'current_price': f"₹{price_today:.2f}",  # Current price is today's closing price
                        'one_day_change': f"{one_day_change:.2f}%",  # Add the 1-day change
                    })

        except Exception as e:
            etf_status_data.append({
                'name': etf,
                'current_price': 'Error fetching data',
                'one_day_change': 'N/A'  # No change if there was an error
            })

    return render_template('etf_status.html', etf_status_data=etf_status_data)

@app.route('/current_prices')
def current_prices():
    stock_data = []

    for stock in stocks:
        try:
            ticker = yf.Ticker(stock + '.NS')  # Adding '.NS' to get NSE data
            data = ticker.history(period='1d')  # Fetch current day's data

            if not data.empty:
                current_price = data['Close'].iloc[-1]
                stock_data.append({'name': stock, 'price': f"₹{current_price:.2f}"})
            else:
                stock_data.append({'name': stock, 'price': 'No data'})
        except Exception as e:
            stock_data.append({'name': 'Error fetching data', 'price': str(e)})

    return render_template('current_prices.html', stock_data=stock_data)

if __name__ == '__main__':
    app.run(debug=True)
