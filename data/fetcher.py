import ccxt
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataFetcher:
    def __init__(self, exchange_id='binance'):
        self.exchange_id = exchange_id
        exchange_class = getattr(ccxt, exchange_id)
        
        # Check for API keys in environment
        api_key = os.getenv(f'{exchange_id.upper()}_API_KEY')
        secret = os.getenv(f'{exchange_id.upper()}_SECRET')
        
        config = {}
        if api_key and secret:
            config = {
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True
            }
            
        self.exchange = exchange_class(config)
        self.exchange.load_markets()

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=1000):
        """
        Fetch OHLCV data from the exchange.
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return None

    def fetch_order_book(self, symbol, limit=20):
        """
        Fetch Order Book data.
        """
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            return order_book
        except Exception as e:
            print(f"Error fetching Order Book for {symbol}: {e}")
            return None

if __name__ == "__main__":
    fetcher = DataFetcher()
    # Test fetch
    try:
        df = fetcher.fetch_ohlcv('BTC/USDT', '1h', 10)
        if df is not None:
            print(df.head())
    except Exception as e:
        print(f"Test failed: {e}")
