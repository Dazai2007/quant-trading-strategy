import numpy as np
import pandas as pd
import scipy.stats as stats

class TradeDependence:
    def __init__(self):
        pass

    def runs_test(self, outcomes):
        """
        Wald-Wolfowitz Runs Test for randomness.
        Checks if the sequence of wins/losses is random.
        
        Args:
            outcomes (list or np.array): Binary sequence (1 for Win, 0 for Loss).
            
        Returns:
            dict: Z-score and p-value.
        """
        outcomes = np.array(outcomes)
        n = len(outcomes)
        n1 = np.sum(outcomes) # Number of wins
        n0 = n - n1 # Number of losses
        
        if n1 == 0 or n0 == 0:
            return {'z_score': 0, 'p_value': 1.0}

        # Calculate number of runs
        runs = 1 # Start with 1 run
        for i in range(1, n):
            if outcomes[i] != outcomes[i-1]:
                runs += 1
                
        # Expected runs and variance
        expected_runs = ((2 * n1 * n0) / n) + 1
        variance = (2 * n1 * n0 * (2 * n1 * n0 - n)) / ((n**2) * (n - 1))
        
        if variance == 0:
            z_score = 0
        else:
            z_score = (runs - expected_runs) / np.sqrt(variance)
            
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score))) # Two-tailed
        
        return {
            'runs': runs,
            'expected_runs': expected_runs,
            'z_score': z_score,
            'p_value': p_value,
            'is_random': p_value > 0.05
        }
