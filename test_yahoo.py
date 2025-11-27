import yfinance as yf
import pandas as pd

def test_yahoo():
    symbol = "BTC-USD"
    print(f"Testing connection for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        # Try fetching 1 month of data
        df = ticker.history(period="1mo", interval="1h")
        
        if df.empty:
            print("ERROR: DataFrame is empty.")
        else:
            print("SUCCESS: Data fetched successfully.")
            print(df.head())
            print(f"Rows: {len(df)}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_yahoo()
