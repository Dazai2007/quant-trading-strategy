from data.fetcher import DataFetcher

def test_binance():
    # Initialize with binance source
    fetcher = DataFetcher(source='binance')
    
    # 2 years of 15m data = approx 2 * 365 * 24 * 4 = 70,080 candles
    limit = 70000 
    symbol = 'BTC/USDT'
    
    print(f"Testing Binance fetch for {symbol} (Limit: {limit})...")
    df = fetcher.fetch_ohlcv(symbol, timeframe='15m', limit=limit)
    
    if df is not None and not df.empty:
        print("SUCCESS!")
        print(f"Rows: {len(df)}")
        print(f"Start: {df['timestamp'].iloc[0]}")
        print(f"End: {df['timestamp'].iloc[-1]}")
    else:
        print("FAILURE: No data returned.")

if __name__ == "__main__":
    test_binance()
