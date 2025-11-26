import pandas as pd
import numpy as np
from risk.guardrails import RiskGuardrails

class BacktestEngine:
    def __init__(self, initial_capital=10000.0, fee=0.001, max_drawdown=0.20):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.fee = fee
        self.positions = [] 
        self.current_position = {'quantity': 0.0, 'entry_price': 0.0} 
        self.equity_curve = []
        self.peak_equity = initial_capital
        self.guardrails = RiskGuardrails(max_drawdown)

    def run(self, data, strategy_logic):
        """
        Event-driven backtest loop with Position Management and Circuit Breaker.
        """
        for index, row in data.iterrows():
            current_price = row['close']
            
            # 1. Mark to Market Equity
            unrealized_pnl = self.current_position['quantity'] * (current_price - self.current_position['entry_price'])
            portfolio_value = self.capital + unrealized_pnl
            
            # Update Peak Equity
            if portfolio_value > self.peak_equity:
                self.peak_equity = portfolio_value
            
            self.equity_curve.append({'timestamp': row['timestamp'], 'equity': portfolio_value})
            
            # 2. Check Circuit Breaker
            if self.guardrails.check_circuit_breaker(portfolio_value, self.peak_equity):
                # Close all positions if not already closed
                if self.current_position['quantity'] != 0:
                    self._close_position(current_price)
                continue # Skip strategy logic (Halt Trading)

            # 3. Get Strategy Signal
            signal, size = strategy_logic(row, portfolio_value, self.current_position)
            
            # 4. Execute Signal
            if signal == 0:
                continue

            # Buy / Open Long
            if signal == 1:
                if self.current_position['quantity'] < 0:
                    self._close_position(current_price)
                qty = size / current_price
                self._open_position(qty, current_price)

            # Sell / Open Short
            elif signal == -1:
                if self.current_position['quantity'] > 0:
                    self._close_position(current_price)
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
        cost = abs(quantity * price)
        fee_amt = cost * self.fee
        self.capital -= fee_amt
        
        self.current_position['quantity'] += quantity
        if self.current_position['entry_price'] == 0:
             self.current_position['entry_price'] = price
        else:
            total_val = (self.current_position['quantity'] - quantity) * self.current_position['entry_price'] + quantity * price
            self.current_position['entry_price'] = total_val / self.current_position['quantity']

    def _close_position(self, price):
        qty = self.current_position['quantity']
        entry = self.current_position['entry_price']
        pnl = qty * (price - entry)
        cost = abs(qty * price)
        fee_amt = cost * self.fee
        
        self.capital += (pnl - fee_amt)
        self.positions.append({
            'entry_price': entry,
            'exit_price': price,
            'quantity': qty,
            'pnl': pnl - fee_amt,
            'fee': fee_amt
        })
        self.current_position = {'quantity': 0.0, 'entry_price': 0.0}

    def calculate_metrics(self):
        """
        Calculate trading metrics: Profit Factor, Win Rate, Max Drawdown.
        """
        if not self.positions:
            return {
                'profit_factor': 0.0,
                'win_rate': 0.0,
                'total_trades': 0,
                'max_drawdown': 0.0
            }

        gross_profit = sum(p['pnl'] for p in self.positions if p['pnl'] > 0)
        gross_loss = sum(p['pnl'] for p in self.positions if p['pnl'] <= 0)
        
        profit_factor = gross_profit / abs(gross_loss) if gross_loss != 0 else float('inf')
        
        wins = len([p for p in self.positions if p['pnl'] > 0])
        total_trades = len(self.positions)
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0.0

        # Max Drawdown from equity curve
        df = pd.DataFrame(self.equity_curve)
        if not df.empty:
            running_max = df['equity'].cummax()
            drawdown = (df['equity'] - running_max) / running_max
            max_drawdown = abs(drawdown.min()) * 100
        else:
            max_drawdown = 0.0

        return {
            'profit_factor': profit_factor,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'max_drawdown': max_drawdown
        }
