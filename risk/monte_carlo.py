import numpy as np
import pandas as pd

class MonteCarloSimulation:
    def __init__(self, num_simulations=1000, num_trades=100):
        self.num_simulations = num_simulations
        self.num_trades = num_trades

    def simulate(self, win_rate, avg_win, avg_loss, starting_capital=10000):
        """
        Run Monte Carlo simulation for a trading strategy.
        
        Args:
            win_rate (float): Probability of winning (0.0 to 1.0).
            avg_win (float): Average profit per winning trade (%).
            avg_loss (float): Average loss per losing trade (%).
            starting_capital (float): Initial capital.
            
        Returns:
            dict: Statistics of the simulation (Max DD, Final Equity, Ruin Prob).
        """
        results = []
        max_drawdowns = []
        ruin_count = 0

        for _ in range(self.num_simulations):
            equity = [starting_capital]
            peak = starting_capital
            max_dd = 0.0
            
            # Generate trade outcomes
            # 1 = Win, 0 = Loss
            outcomes = np.random.choice([1, 0], size=self.num_trades, p=[win_rate, 1-win_rate])
            
            for outcome in outcomes:
                current_cap = equity[-1]
                if outcome == 1:
                    pnl = current_cap * avg_win
                else:
                    pnl = -current_cap * avg_loss
                
                new_cap = current_cap + pnl
                if new_cap <= 0:
                    new_cap = 0
                
                equity.append(new_cap)
                
                # Track DD
                if new_cap > peak:
                    peak = new_cap
                dd = (peak - new_cap) / peak if peak > 0 else 0
                if dd > max_dd:
                    max_dd = dd
            
            results.append(equity[-1])
            max_drawdowns.append(max_dd)
            if equity[-1] <= starting_capital * 0.5: # Definition of "ruin" can vary
                ruin_count += 1

        stats = {
            'mean_final_equity': np.mean(results),
            'median_final_equity': np.median(results),
            'max_drawdown_95th': np.percentile(max_drawdowns, 95),
            'ruin_probability': ruin_count / self.num_simulations
        }
        return stats
