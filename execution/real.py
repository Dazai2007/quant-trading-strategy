import ccxt
import time

class RealExecution:
    def __init__(self, exchange_id='binance', api_key=None, secret=None, sandbox=False):
        exchange_class = getattr(ccxt, exchange_id)
        config = {
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        }
        self.exchange = exchange_class(config)
        if sandbox:
            self.exchange.set_sandbox_mode(True)
        self.exchange.load_markets()

    def place_order(self, symbol, side, type, amount, price=None):
        """
        Place a real order.
        """
        try:
            if type == 'limit':
                order = self.exchange.create_order(symbol, type, side, amount, price)
            else:
                order = self.exchange.create_order(symbol, type, side, amount)
            
            print(f"Order placed: {order['id']} - {side} {amount} {symbol}")
            return order
        except Exception as e:
            print(f"Order failed: {e}")
            return None

    def get_balance(self, currency='USDT'):
        try:
            balance = self.exchange.fetch_balance()
            return balance['total'].get(currency, 0.0)
        except Exception as e:
            print(f"Failed to fetch balance: {e}")
            return 0.0
