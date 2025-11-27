from data.fetcher import DataFetcher
import pandas as pd

def test_fetcher():
    print("Testing DataFetcher with Yahoo...")
    fetcher = DataFetcher(source='yahoo')
    
    try:
        df = fetcher.fetch_ohlcv("BTC-USD", timeframe="1h", limit=100)
        
        if df is None:
            print("ERROR: fetch_ohlcv returned None.")
        elif df.empty:
            print("ERROR: Returned DataFrame is empty.")
        else:
            print("SUCCESS: Data fetched successfully.")
            print(df.head())
            print(df.dtypes)
            
    except Exception as e:
        print(f"EXCEPTION in test: {e}")

if __name__ == "__main__":
    test_fetcher()
