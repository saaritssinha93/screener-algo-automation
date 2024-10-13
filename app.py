from flask import Flask, render_template
import yfinance as yf

app = Flask(__name__)

# List of known ETF symbols on NSE
etfs = [
    'ABGSEC', 'ABSLBANETF', 'ABSLNN50ET', 'ABSLPSE', 'BFSI'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/etf_list')
def etf_list():
    etf_data = []

    for etf in etfs:
        try:
            ticker = yf.Ticker(etf + '.NS')  # Adding '.NS' to get NSE data
            info = ticker.info
            data = ticker.history(period='1d')  # Fetch current day's data

            if not data.empty:
                current_price = data['Close'].iloc[-1]
                etf_name = info.get('longName', 'N/A')  # Get the long name of the ETF
                etf_data.append({'name': etf_name, 'price': f"₹{current_price:.2f}"})
            else:
                etf_data.append({'name': 'N/A', 'price': 'No data'})
        except Exception as e:
            etf_data.append({'name': 'Error fetching data', 'price': str(e)})

    return render_template('etf_list.html', etf_data=etf_data)

if __name__ == '__main__':
    app.run(debug=True)
