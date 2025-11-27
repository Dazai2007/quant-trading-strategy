class StrategyLogic:
    def __init__(self, config):
        self.params = config

    def get_signal(self, row, capital, current_position):
        """
        Returns:
            signal (int): 1 (Buy), -1 (Sell), 2 (Close Long), -2 (Close Short), 0 (Hold)
            size (float): Position size in Quote Currency (e.g. USDT)
        """
        signal = 0
        
        # Entry Logic
        adx_threshold = self.params['strategy']['indicators'].get('adx_threshold', 25)
        current_adx = row.get('adx', 0)
        
        if row.get('regime') == 'TREND':
            if row['ma_short'] > row['ma_long']:
                if row['rsi'] < self.params['strategy']['indicators']['rsi_overbought']:
                    if current_adx > adx_threshold:
                        signal = 1
            
            elif row['ma_short'] < row['ma_long']:
                if row['rsi'] > self.params['strategy']['indicators']['rsi_oversold']:
                    if current_adx > adx_threshold:
                        signal = -1

        # Exit Logic (Trailing Stop & Fixed SL/TP)
        if current_position['quantity'] != 0:
            entry_price = current_position['entry_price']
            current_price = row['close']
            atr = row['atr']
            
            sl_atr = self.params['strategy']['risk']['stop_loss_atr']
            tp_atr = self.params['strategy']['risk']['take_profit_atr']
            
            # Trailing Stop Logic
            # We use a simplified chandelier exit or ATR trailing stop
            # For Long: Stop moves up to Highest High - (ATR * SL_ATR)
            # For Short: Stop moves down to Lowest Low + (ATR * SL_ATR)
            # Since we don't track Highest High since entry in this simple logic, 
            # we will use Close - (ATR * SL_ATR) as a dynamic stop if it's better than fixed SL.
            
            # Actually, to implement proper trailing stop without state, we can check if
            # current price reverted by X ATR from the extreme price since entry.
            # But we don't have "extreme price since entry" in the row.
            # So we will use a simpler "Breakeven" or "Dynamic" approach:
            # If profit > 2 ATR, move SL to Entry + 0.5 ATR (Lock profit)
            
            # Better: Use Moving Average as Trailing Stop?
            # Let's stick to the plan: Trailing Stop.
            # Since we lack state of "highest price since entry", we can't do a perfect trailing stop.
            # However, BacktestEngine tracks current_position.
            # Let's implement a "Ratchet" Stop:
            # If Price > Entry + 1 ATR, Move SL to Entry.
            # If Price > Entry + 2 ATR, Move SL to Entry + 1 ATR.
            
            # Long Position Exits
            if current_position['quantity'] > 0:
                # Fixed SL
                stop_loss = entry_price - (atr * sl_atr)
                
                # Trailing / Ratchet Logic
                profit_atr = (current_price - entry_price) / atr
                if profit_atr > 2.0:
                    stop_loss = max(stop_loss, entry_price + (atr * 0.5)) # Lock 0.5 ATR
                if profit_atr > 4.0:
                    stop_loss = max(stop_loss, entry_price + (atr * 2.0)) # Lock 2.0 ATR
                
                take_profit = entry_price + (atr * tp_atr)
                
                if current_price <= stop_loss:
                    return 2, 0 # Close Long (SL/Trailing)
                if current_price >= take_profit:
                    return 2, 0 # Close Long (TP)
                
                if signal == -1:
                    return -1, self._calculate_size(capital, atr)

            # Short Position Exits
            elif current_position['quantity'] < 0:
                # Fixed SL
                stop_loss = entry_price + (atr * sl_atr)
                
                # Trailing / Ratchet Logic
                profit_atr = (entry_price - current_price) / atr
                if profit_atr > 2.0:
                    stop_loss = min(stop_loss, entry_price - (atr * 0.5))
                if profit_atr > 4.0:
                    stop_loss = min(stop_loss, entry_price - (atr * 2.0))
                
                take_profit = entry_price - (atr * tp_atr)
                
                if current_price >= stop_loss:
                    return -2, 0 # Close Short (SL/Trailing)
                if current_price <= take_profit:
                    return -2, 0 # Close Short (TP)

                if signal == 1:
                    return 1, self._calculate_size(capital, atr)

        # Calculate Size for New Entry
        size = 0
        if signal in [1, -1]:
            size = self._calculate_size(capital, row['atr'])

        return signal, size

    def _calculate_size(self, capital, atr):
        return capital * 0.1 # Invest 10% of equity per trade
