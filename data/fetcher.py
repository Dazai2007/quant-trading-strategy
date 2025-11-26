import ccxt
import pandas as pd
import os
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

class DataFetcher:
    def __init__(self, exchange_id='binance', source='binance'):
        self.source = source
        if self.source == 'binance':
            self.exchange = getattr(ccxt, exchange_id)({
                'apiKey': os.getenv('BINANCE_API_KEY'),
                'secret': os.getenv('BINANCE_SECRET'),
                'enableRateLimit': True,
            })
        else:
            self.exchange = None

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=100):
        if self.source == 'yahoo':
            return self._fetch_yahoo(symbol, timeframe, limit)
        else:
            return self._fetch_ccxt(symbol, timeframe, limit)

    def _fetch_ccxt(self, symbol, timeframe, limit):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching data from CCXT: {e}")
            return None

    def _fetch_yahoo(self, symbol, timeframe, limit):
        try:
            # Map timeframe: 1h -> 1h, 1d -> 1d
            # Yahoo symbols: BTC/USDT -> BTC-USD
            yf_symbol = symbol.replace('/', '-') if '/' in symbol else symbol
            if yf_symbol == 'BTC-USDT': yf_symbol = 'BTC-USD' # Common mapping
            
            # Calculate period based on limit and timeframe (Approx)
            # yfinance uses period='1y', '1mo' etc or start/end
            # For simplicity, let's fetch a fixed period that covers the limit
            period = '1y' 
            if timeframe == '1d': period = '5y'
            if timeframe == '1m': period = '7d'
            
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=timeframe)
            
            if df.empty:
                print(f"No data found for {yf_symbol} on Yahoo.")
                return None
                
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'timestamp', 'Datetime': 'timestamp',
                'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
            })
            
            # Ensure timestamp is datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter to limit
            df = df.tail(limit).reset_index(drop=True)
            
            # Keep only required columns
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
        except Exception as e:
            print(f"Error fetching data from Yahoo: {e}")
            return None

    def fetch_order_book(self, symbol, limit=5):
        if self.source == 'yahoo':
            print("Order book not supported for Yahoo Finance.")
            return None
        try:
            return self.exchange.fetch_order_book(symbol, limit)
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None
