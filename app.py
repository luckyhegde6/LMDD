from flask import Flask, render_template, jsonify, request
import yfinance as yf
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
import requests

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Stock model
class StockPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# List of Nifty 50 stocks
NIFTY50_STOCKS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "HINDUNILVR", "KOTAKBANK", "LT", "SBIN", "AXISBANK",
    "BAJFINANCE", "BHARTIARTL", "MARUTI", "TITAN", "SUNPHARMA",
    "ULTRACEMCO", "ITC", "WIPRO", "NTPC", "POWERGRID"
]

# Fetch and store stock prices in the database
def fetch_stock_prices():
    prices = {}
    for stock in NIFTY50_STOCKS:
        symbol = stock.replace("", "")  # Remove "" for TradingView API
        url = f"https://www.tradingview.com/symbols/NSE-{symbol}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Extract price data (requires additional parsing)
                prices[stock] = "Fetched successfully"  # Placeholder
            else:
                prices[stock] = "Error fetching data"
        except Exception as e:
            prices[stock] = f"Error: {e}"
    return prices

@app.route('/')
def index():
    return render_template("index.html", stocks=NIFTY50_STOCKS)

@app.route('/api/prices')
def api_prices():
    latest_prices = {}
    for stock in NIFTY50_STOCKS:
        latest_entry = StockPrice.query.filter_by(symbol=stock).order_by(StockPrice.timestamp.desc()).first()
        latest_prices[stock] = latest_entry.price if latest_entry else "N/A"
    return jsonify(latest_prices)

@app.route('/api/price_history')
def price_history():
    stock = request.args.get("stock")
    history = StockPrice.query.filter_by(symbol=stock).order_by(StockPrice.timestamp.asc()).all()
    data = {"timestamps": [entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") for entry in history],
            "prices": [entry.price for entry in history]}
    return jsonify(data)

if __name__ == "__main__":
    fetch_stock_prices()  # Fetch initial data
    app.run(host="0.0.0.0", port=5000, debug=True)
