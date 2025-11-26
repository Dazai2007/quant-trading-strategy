import pandas as pd
import numpy as np

class BacktestEngine:
    def __init__(self, initial_capital=10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []

    def run(self, data, strategy_logic):
        """
        Simple event-driven backtest loop.
        
        Args:
            data (pd.DataFrame): OHLCV data with indicators.
            strategy_logic (function): Function that returns signal (1, -1, 0) and size.
        """
        for index, row in data.iterrows():
            # 1. Update Portfolio Value
            current_price = row['close']
            portfolio_value = self.capital
            
            # Mark to Market
            for pos in self.positions:
                portfolio_value += pos['quantity'] * (current_price - pos['entry_price'])
            
            self.equity_curve.append({'timestamp': row['timestamp'], 'equity': portfolio_value})
            
            # 2. Get Strategy Signal
            signal, size = strategy_logic(row, portfolio_value)
            
            # 3. Execute Signal (Simplified)
            if signal != 0 and size > 0:
                # Close existing if opposite
                # Open new
                self.positions.append({
                    'symbol': 'BTC/USDT',
                    'entry_price': current_price,
                    'quantity': size if signal == 1 else -size,
                    'timestamp': row['timestamp']
                })
                # Deduct cost (simplified)
                # self.capital -= ... 
                
        return pd.DataFrame(self.equity_curve)
