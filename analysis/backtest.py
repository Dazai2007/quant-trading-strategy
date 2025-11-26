import pandas as pd
import numpy as np

class BacktestEngine:
    def __init__(self, initial_capital=10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = [] # List of trade history
        self.current_position = {'quantity': 0.0, 'entry_price': 0.0} # Net position
        self.equity_curve = []

    def run(self, data, strategy_logic):
        """
        Event-driven backtest loop with Position Management.
        
        Args:
            data (pd.DataFrame): OHLCV data with indicators.
            strategy_logic (function): Function that returns (signal, size).
                                     signal: 1 (Buy), -1 (Sell), 2 (Close Long), -2 (Close Short)
        """
        for index, row in data.iterrows():
            current_price = row['close']
            
            # 1. Mark to Market Equity
            unrealized_pnl = self.current_position['quantity'] * (current_price - self.current_position['entry_price'])
            portfolio_value = self.capital + unrealized_pnl
            
            self.equity_curve.append({'timestamp': row['timestamp'], 'equity': portfolio_value})
            
            # 2. Get Strategy Signal
            # Pass current position info to strategy
            signal, size = strategy_logic(row, portfolio_value, self.current_position)
            
            # 3. Execute Signal
            if signal == 0:
                continue

            # Buy / Open Long
            if signal == 1:
                # If short, close first
                if self.current_position['quantity'] < 0:
                    self._close_position(current_price)
                
                # Open new long
                qty = size / current_price
                self._open_position(qty, current_price)

            # Sell / Open Short
            elif signal == -1:
                # If long, close first
                if self.current_position['quantity'] > 0:
                    self._close_position(current_price)
                
                # Open new short
                qty = size / current_price
                self._open_position(-qty, current_price)

            # Close Positions
            elif signal == 2: # Close Long
                if self.current_position['quantity'] > 0:
                    self._close_position(current_price)
            
            elif signal == -2: # Close Short
                if self.current_position['quantity'] < 0:
                    self._close_position(current_price)

        return pd.DataFrame(self.equity_curve)

    def _open_position(self, quantity, price):
        self.current_position['quantity'] += quantity
        # Weighted average entry price (simplified: just update if flat, else average)
        # For simplicity in this demo, we assume full re-entry or adding
        if self.current_position['entry_price'] == 0:
             self.current_position['entry_price'] = price
        else:
            # Update avg price
            total_val = (self.current_position['quantity'] - quantity) * self.current_position['entry_price'] + quantity * price
            self.current_position['entry_price'] = total_val / self.current_position['quantity']

    def _close_position(self, price):
        qty = self.current_position['quantity']
        entry = self.current_position['entry_price']
        pnl = qty * (price - entry)
        
        self.capital += pnl
        self.positions.append({
            'entry_price': entry,
            'exit_price': price,
            'quantity': qty,
            'pnl': pnl
        })
        
        # Reset
        self.current_position = {'quantity': 0.0, 'entry_price': 0.0}
