import pandas as pd
import numpy as np

class OrderBookImbalance:
    @staticmethod
    def calculate_imbalance(order_book, depth=10):
        """
        Calculate Order Book Imbalance (OBI).
        OBI = (Bid_Qty - Ask_Qty) / (Bid_Qty + Ask_Qty)
        
        Args:
            order_book (dict): CCXT order book structure {'bids': [], 'asks': []}
            depth (int): Number of levels to consider.
            
        Returns:
            float: Imbalance ratio between -1 (Sell pressure) and 1 (Buy pressure).
        """
        if not order_book or 'bids' not in order_book or 'asks' not in order_book:
            return 0.0

        bids = np.array(order_book['bids'])[:depth]
        asks = np.array(order_book['asks'])[:depth]

        if len(bids) == 0 or len(asks) == 0:
            return 0.0

        bid_qty = np.sum(bids[:, 1])
        ask_qty = np.sum(asks[:, 1])

        if bid_qty + ask_qty == 0:
            return 0.0

        imbalance = (bid_qty - ask_qty) / (bid_qty + ask_qty)
        return imbalance

    @staticmethod
    def weighted_imbalance(order_book, depth=10, decay=0.5):
        """
        Calculate Weighted Order Book Imbalance.
        Closer levels have higher weight.
        """
        # Placeholder for more complex logic
        pass
