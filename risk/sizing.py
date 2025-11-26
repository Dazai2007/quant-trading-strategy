import numpy as np

class PositionSizing:
    def __init__(self, target_volatility=0.20):
        """
        Args:
            target_volatility (float): Annualized target volatility (e.g., 0.20 for 20%).
        """
        self.target_volatility = target_volatility

    def calculate_volatility_target_size(self, capital, current_volatility):
        """
        Calculate position size based on volatility targeting.
        Size = (Target Vol / Current Vol) * Capital
        
        Args:
            capital (float): Current portfolio capital.
            current_volatility (float): Annualized volatility of the asset.
            
        Returns:
            float: Position size in currency units.
        """
        if current_volatility <= 0:
            return 0.0
            
        # Cap leverage if necessary (e.g., max 2x)
        leverage_cap = 2.0
        
        raw_weight = self.target_volatility / current_volatility
        weight = min(raw_weight, leverage_cap)
        
        position_size = capital * weight
        return position_size

    def kelly_criterion(self, win_rate, win_loss_ratio):
        """
        Calculate Kelly fraction.
        f = p - q/b
        """
        if win_loss_ratio <= 0:
            return 0.0
        return win_rate - (1 - win_rate) / win_loss_ratio
