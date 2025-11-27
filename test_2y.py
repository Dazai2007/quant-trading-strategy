import yfinance as yf

def test_2y():
    symbol = "BTC-USD"
    print(f"Testing 2y fetch for {symbol}...")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="2y", interval="1h")
    
    if df.empty:
        print("ERROR: Empty DataFrame")
    else:
        print(f"SUCCESS: Fetched {len(df)} rows")
        print(df.head())
        print(df.tail())

if __name__ == "__main__":
    test_2y()
