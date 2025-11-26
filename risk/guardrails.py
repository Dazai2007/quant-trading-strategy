class RiskGuardrails:
    def __init__(self, max_drawdown_limit=0.20):
        """
        Args:
            max_drawdown_limit (float): Maximum allowed drawdown (e.g., 0.20 for 20%).
        """
        self.max_drawdown_limit = max_drawdown_limit
        self.peak_equity = 0.0

    def update_equity(self, current_equity):
        """
        Update peak equity and check for drawdown violation.
        """
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
            
    def check_drawdown(self, current_equity):
        """
        Check if current drawdown exceeds the limit.
        
        Returns:
            bool: True if drawdown limit is breached (STOP TRADING), False otherwise.
        """
        if self.peak_equity == 0:
            return False
            
        drawdown = (self.peak_equity - current_equity) / self.peak_equity
        
        if drawdown > self.max_drawdown_limit:
            return True # BREACH
        return False

    def check_risk_per_trade(self, entry_price, stop_loss, capital, max_risk_per_trade=0.02):
        """
        Calculate max position size based on risk per trade.
        """
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share == 0:
            return 0.0
            
        max_risk_amount = capital * max_risk_per_trade
        max_position_size = max_risk_amount / risk_per_share
        return max_position_size
