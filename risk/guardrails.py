class RiskGuardrails:
    def __init__(self, max_drawdown=0.20):
        self.max_drawdown = max_drawdown
        self.circuit_breaker_triggered = False

    def check_drawdown(self, current_equity, peak_equity):
        """
        Check if drawdown exceeds limit.
        """
        if peak_equity <= 0: return False
        drawdown = (peak_equity - current_equity) / peak_equity
        if drawdown > self.max_drawdown:
            return True
        return False

    def check_circuit_breaker(self, current_equity, peak_equity):
        """
        Check if circuit breaker should trigger (halt trading).
        """
        if self.check_drawdown(current_equity, peak_equity):
            self.circuit_breaker_triggered = True
            return True
        return False

    def can_trade(self):
        return not self.circuit_breaker_triggered
