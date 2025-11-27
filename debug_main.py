import yaml
from data.fetcher import DataFetcher
import pandas as pd

def load_config(path='config.yaml'):
    with open(path, 'r', encoding='utf-8-sig') as file:
        return yaml.safe_load(file)

def debug_main():
    print("--- Debug Main ---")
    config = load_config()
    print(f"Config Loaded: {config['backtest']}")
    
    source = config['backtest'].get('source', 'binance')
    print(f"Source: {source}")
    
    fetcher = DataFetcher(source=source)
    symbol = config['backtest']['symbol']
    timeframe = config['backtest']['timeframe']
    limit = config['backtest']['limit']
    
    print(f"Fetching {symbol}...")
    df = fetcher.fetch_ohlcv(symbol, timeframe, limit)
    
    if df is None:
        print("DF is None")
    elif df.empty:
        print("DF is Empty")
    else:
        print(f"Success! Loaded {len(df)} rows.")
        print(df.head())

if __name__ == "__main__":
    debug_main()
