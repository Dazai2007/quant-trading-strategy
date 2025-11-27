import ccxt
import pandas as pd
import os
import time
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class DataFetcher:
    def __init__(self, exchange_id='binance', source='binance'):
        self.source = source
        if self.source == 'binance':
            # Initialize without keys for public data if needed, or with keys if available
            # For fetching historical OHLCV, keys are not strictly required on Binance
            config = {'enableRateLimit': True}
            api_key = os.getenv('BINANCE_API_KEY')
            secret = os.getenv('BINANCE_SECRET')
            if api_key and secret:
                config['apiKey'] = api_key
                config['secret'] = secret
            
            self.exchange = getattr(ccxt, exchange_id)(config)
        else:
            self.exchange = None

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=100):
        if self.source == 'yahoo':
            return self._fetch_yahoo(symbol, timeframe, limit)
        else:
            # If limit is large, use pagination
            if limit > 1000:
                return self._fetch_ccxt_history(symbol, timeframe, limit)
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

    def _fetch_ccxt_history(self, symbol, timeframe, limit):
        """
        Fetch historical data using pagination.
        """
        print(f"Fetching historical data from Binance for {symbol} ({timeframe}, limit={limit})...")
        all_ohlcv = []
        
        # Calculate start time based on limit and timeframe (approx)
        # This is a rough estimate to set a 'since' timestamp
        duration_map = {
            '1m': 60, '3m': 180, '5m': 300, '15m': 900, '30m': 1800,
            '1h': 3600, '2h': 7200, '4h': 14400, '6h': 21600, '12h': 43200,
            '1d': 86400
        }
        seconds_per_candle = duration_map.get(timeframe, 3600)
        total_seconds = limit * seconds_per_candle
        start_time = datetime.now() - timedelta(seconds=total_seconds)
        since = int(start_time.timestamp() * 1000)
        
        fetched_count = 0
        while fetched_count < limit:
            try:
                # Fetch batch
                batch = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
                if not batch:
                    break
                
                all_ohlcv.extend(batch)
                fetched_count += len(batch)
                
                # Update since to the timestamp of the last candle + 1ms
                last_timestamp = batch[-1][0]
                since = last_timestamp + 1
                
                print(f"Fetched {fetched_count}/{limit} candles...", end='\r')
                
                # Rate limit sleep (handled by enableRateLimit but good to be safe)
                # time.sleep(self.exchange.rateLimit / 1000)
                
                if len(batch) < 1000: # End of data
                    break
                    
            except Exception as e:
                print(f"Error fetching batch: {e}")
                break
        
        print(f"\nTotal fetched: {len(all_ohlcv)}")
        
        if not all_ohlcv:
            return None

        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Trim to exact limit if we fetched too much
        if len(df) > limit:
            df = df.iloc[-limit:].reset_index(drop=True)
            
        return df

    def _fetch_yahoo(self, symbol, timeframe, limit):
        try:
            # Map timeframe: 1h -> 1h, 1d -> 1d
            # Yahoo symbols: BTC/USDT -> BTC-USD
            yf_symbol = symbol.replace('/', '-') if '/' in symbol else symbol
            if yf_symbol == 'BTC-USDT': yf_symbol = 'BTC-USD' # Common mapping
            
            # Calculate period based on limit and timeframe (Approx)
            period = '2y' 
            if timeframe == '1d': period = '5y'
            if timeframe == '1m': period = '7d'
            if timeframe == '15m': period = '60d' # Yahoo limit
            
            ticker = yf.Ticker(yf_symbol)
            print(f"Fetching {yf_symbol} from Yahoo (Period: {period}, Interval: {timeframe})...")
            df = ticker.history(period=period, interval=timeframe)
            
            if df.empty:
                print(f"No data found for {yf_symbol} on Yahoo.")
                return None
            
            print(f"Fetched {len(df)} rows from Yahoo.")
                
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'timestamp', 'Datetime': 'timestamp',
                'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
            })
            
            # Ensure timestamp is datetime and remove timezone
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
            
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
