import pandas as pd
import numpy as np
from risk.sizing import PositionSizing

class StrategyLogic:
    def __init__(self, config):
        self.config = config
        self.sizer = PositionSizing(config['strategy']['target_volatility'])
        self.sl_atr = config['strategy']['risk']['stop_loss_atr']
        self.tp_atr = config['strategy']['risk']['take_profit_atr']

    def get_signal(self, row, capital, current_position):
        """
        Determine signal and position size for a single timestep.
        """
        signal = 0
        size = 0.0
        
        current_qty = current_position['quantity']
        entry_price = current_position['entry_price']
        current_price = row['close']
        atr = row.get('atr', 0)
        if pd.isna(atr) or atr == 0:
            atr = current_price * 0.02 # Fallback
            
        # --- EXIT LOGIC ---
        if current_qty > 0: # Long Position
            stop_loss = entry_price - (self.sl_atr * atr)
            take_profit = entry_price + (self.tp_atr * atr)
            
            if current_price <= stop_loss:
                return 2, 0 # Close Long (SL)
            if current_price >= take_profit:
                return 2, 0 # Close Long (TP)
                
        elif current_qty < 0: # Short Position
            stop_loss = entry_price + (self.sl_atr * atr)
            take_profit = entry_price - (self.tp_atr * atr)
            
            if current_price >= stop_loss:
                return -2, 0 # Close Short (SL)
            if current_price <= take_profit:
                return -2, 0 # Close Short (TP)

        # --- ENTRY LOGIC ---
        if current_qty == 0:
            regime = row.get('regime', 'TREND') 
            
            if regime == 'TREND':
                if row['ma_short'] > row['ma_long']:
                    signal = 1
                elif row['ma_short'] < row['ma_long']:
                    signal = -1
                    
            elif regime == 'MEAN_REVERSION':
                if row['rsi'] < self.config['strategy']['indicators']['rsi_oversold'] and row['close'] < row['bb_lower']:
                    signal = 1
                elif row['rsi'] > self.config['strategy']['indicators']['rsi_overbought'] and row['close'] > row['bb_upper']:
                    signal = -1
            
            # Position Sizing
            if signal != 0:
                vol = row.get('garch_vol', 0)
                if pd.isna(vol) or vol == 0:
                    vol = 0.02
                else:
                    vol = vol / 100.0 
                annualized_vol = vol * np.sqrt(365)
                size = self.sizer.calculate_volatility_target_size(capital, annualized_vol)
                
        return signal, size
