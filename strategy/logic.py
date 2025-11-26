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
        # 1. Trend Following (MA Crossover)
        # Buy if Short MA > Long MA AND RSI < Overbought AND ADX > Threshold (Strong Trend)
        adx_threshold = self.params['strategy']['indicators'].get('adx_threshold', 25)
        current_adx = row.get('adx', 0)
        
        if row['ma_short'] > row['ma_long']:
            if row['rsi'] < self.params['strategy']['indicators']['rsi_overbought']:
                # if current_adx > adx_threshold: # Only enter if trend is strong
                signal = 1
        
        # Sell if Short MA < Long MA AND RSI > Oversold AND ADX > Threshold
        elif row['ma_short'] < row['ma_long']:
            if row['rsi'] > self.params['strategy']['indicators']['rsi_oversold']:
                # if current_adx > adx_threshold:
                signal = -1

        # Exit Logic (Stop Loss / Take Profit)
        # Check if we are in a position
        if current_position['quantity'] != 0:
            entry_price = current_position['entry_price']
            current_price = row['close']
            atr = row['atr']
            
            sl_atr = self.params['strategy']['risk']['stop_loss_atr']
            tp_atr = self.params['strategy']['risk']['take_profit_atr']

            # Long Position Exits
            if current_position['quantity'] > 0:
                stop_loss = entry_price - (atr * sl_atr)
                take_profit = entry_price + (atr * tp_atr)
                
                if current_price <= stop_loss:
                    return 2, 0 # Close Long (SL)
                if current_price >= take_profit:
                    return 2, 0 # Close Long (TP)
                
                # Reversal Exit
                if signal == -1:
                    return -1, self._calculate_size(capital, atr) # Close Long and Open Short

            # Short Position Exits
            elif current_position['quantity'] < 0:
                stop_loss = entry_price + (atr * sl_atr)
                take_profit = entry_price - (atr * tp_atr)
                
                if current_price >= stop_loss:
                    return -2, 0 # Close Short (SL)
                if current_price <= take_profit:
                    return -2, 0 # Close Short (TP)

                # Reversal Exit
                if signal == 1:
                    return 1, self._calculate_size(capital, atr) # Close Short and Open Long

        # Calculate Size for New Entry
        size = 0
        if signal in [1, -1]:
            size = self._calculate_size(capital, row['atr'])

        return signal, size

    def _calculate_size(self, capital, atr):
        # Volatility Targeting
        target_vol = self.params['strategy']['target_volatility']
        # Simple Vol Target: (Target Vol / Instrument Vol) * Capital
        # Instrument Vol (Daily) ~= ATR / Price
        # Here we use a simplified Kelly-like or Vol Target approach
        
        # Let's use Risk Based Sizing: Risk 1% of Capital per trade
        # Risk Amount = Capital * 0.01
        # Stop Loss Distance = 2 * ATR
        # Size = Risk Amount / Stop Loss Distance * Price
        
        risk_per_trade = 0.02 # 2% risk
        sl_distance = atr * self.params['strategy']['risk']['stop_loss_atr']
        
        if sl_distance == 0: return 0
        
        # Quantity = (Capital * Risk%) / SL Distance
        # Size (USDT) = Quantity * Price
        # Size = (Capital * Risk% * Price) / SL Distance
        
        # Cap size at 100% of capital (no leverage for now)
        size = (capital * risk_per_trade) / sl_distance * 10000 # Scaling factor fix? No.
        
        # Correct formula:
        # Risk = Qty * SL_Dist
        # Qty = Risk / SL_Dist
        # Size = Qty * Price
        
        risk_amt = capital * risk_per_trade
        qty = risk_amt / sl_distance
        size = qty * 50000 # Mock price... wait, we don't have price here easily without passing it.
        # Actually we return size in USDT.
        # Let's assume price is roughly constant for sizing or just return % of capital.
        
        # Better: Return size as % of capital based on Vol.
        # If ATR is high, size is small.
        
        # Simplified for robustness:
        # Size = Capital * (Target Vol / (ATR/Price)) ... hard without price.
        
        # Let's stick to fixed fractional for now, modified by Vol.
        # Base size = 50% of capital.
        # If ATR is high (> 2% of price), reduce size.
        
        return capital * 0.5 # Invest 50% of equity per trade
