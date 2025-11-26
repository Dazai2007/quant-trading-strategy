import random

class SmartOrderRouter:
    def __init__(self, exchanges=['binance', 'coinbase', 'kraken']):
        self.exchanges = exchanges

    def get_best_price(self, symbol, side='buy', quantity=1.0):
        """
        Simulate finding the best price across multiple exchanges.
        In a real system, this would query live order books.
        """
        prices = {}
        # Simulate slight price variations
        base_price = 100000.0 # Placeholder BTC price
        
        for exchange in self.exchanges:
            # Random deviation +/- 0.05%
            deviation = base_price * random.uniform(-0.0005, 0.0005)
            prices[exchange] = base_price + deviation

        if side == 'buy':
            best_exchange = min(prices, key=prices.get)
            best_price = prices[best_exchange]
        else:
            best_exchange = max(prices, key=prices.get)
            best_price = prices[best_exchange]

        return {
            'exchange': best_exchange,
            'price': best_price,
            'quantity': quantity,
            'side': side
        }

    def route_order(self, order):
        """
        Route the order to the best exchange.
        """
        best_execution = self.get_best_price(order['symbol'], order['side'], order['quantity'])
        print(f"Routing order to {best_execution['exchange']} @ {best_execution['price']:.2f}")
        return best_execution
