import pandas as pd
import numpy as np
import time

class OrderBookReplay:
    def __init__(self, fetcher=None):
        self.fetcher = fetcher

    def generate_dummy_book(self, mid_price, depth=10, spread_bps=5):
        """
        Generate a dummy order book around a mid price.
        """
        spread = mid_price * (spread_bps / 10000.0)
        best_bid = mid_price - (spread / 2)
        best_ask = mid_price + (spread / 2)

        bids = []
        asks = []

        for i in range(depth):
            # Price steps
            bid_price = best_bid - (i * mid_price * 0.0001)
            ask_price = best_ask + (i * mid_price * 0.0001)
            
            # Random quantity
            bid_qty = np.random.uniform(0.1, 2.0)
            ask_qty = np.random.uniform(0.1, 2.0)
            
            bids.append([bid_price, bid_qty])
            asks.append([ask_price, ask_qty])

        return {'bids': bids, 'asks': asks, 'timestamp': int(time.time()*1000)}

    def replay_stream(self, price_series):
        """
        Yield order books based on a price series (e.g., from OHLCV close).
        """
        for price in price_series:
            yield self.generate_dummy_book(price)
