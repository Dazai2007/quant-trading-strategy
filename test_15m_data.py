import yfinance as yf

def test_15m():
    symbol = "BTC-USD"
    print(f"Testing 15m fetch for {symbol}...")
    
    # Try fetching 2 years
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2y", interval="15m")
        if df.empty:
            print("2y fetch failed (Empty).")
        else:
            print(f"2y fetch success: {len(df)} rows. Range: {df.index[0]} to {df.index[-1]}")
            return
    except Exception as e:
        print(f"2y fetch error: {e}")

    # Try fetching 60 days (max usually)
    try:
        print("Testing 60d fetch...")
        df = ticker.history(period="60d", interval="15m")
        if df.empty:
            print("60d fetch failed (Empty).")
        else:
            print(f"60d fetch success: {len(df)} rows. Range: {df.index[0]} to {df.index[-1]}")
    except Exception as e:
        print(f"60d fetch error: {e}")

if __name__ == "__main__":
    test_15m()
