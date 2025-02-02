import yfinance as yf

def get_stock_price(symbol="AAPL"):
    stock = yf.Ticker(symbol)
    return stock.history(period="1d")['Close'].iloc[-1]

print("AAPL Price:", get_stock_price("AAPL"))
