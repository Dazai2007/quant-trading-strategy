import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class Visualizer:
    def __init__(self, results_df, data_df):
        """
        Args:
            results_df (pd.DataFrame): Backtest results (timestamp, equity).
            data_df (pd.DataFrame): Original OHLCV data with indicators and regimes.
        """
        self.results = results_df
        self.data = data_df
        # Merge to align timestamps
        self.merged = pd.merge(self.results, self.data, on='timestamp', how='inner')

    def plot_performance(self, filename='strategy_performance.png'):
        """
        Plot Equity Curve, Drawdown, and Regime overlay.
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # 1. Equity Curve
        ax1.plot(self.merged['timestamp'], self.merged['equity'], label='Equity', color='blue')
        ax1.set_title('Strategy Equity Curve')
        ax1.set_ylabel('Equity ($)')
        ax1.legend(loc='upper left')
        ax1.grid(True)

        # Overlay Regimes on Equity
        # We can shade the background based on regime
        if 'regime' in self.merged.columns:
            # Create spans for regimes
            # This is a bit complex to vectorize, simplified loop for demo
            # Or just plot regime as a separate line/scatter on ax1 twinx
            pass

        # 2. Drawdown
        equity_series = self.merged['equity']
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max
        
        ax2.fill_between(self.merged['timestamp'], drawdown, 0, color='red', alpha=0.3, label='Drawdown')
        ax2.set_title('Drawdown')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True)

        # 3. Regime / Volatility
        if 'regime' in self.merged.columns:
            # Map regime to numeric for plotting
            regime_map = {'TREND': 1, 'MEAN_REVERSION': 0}
            numeric_regime = self.merged['regime'].map(regime_map)
            ax3.step(self.merged['timestamp'], numeric_regime, where='post', label='Regime (1=Trend, 0=Range)', color='purple')
            ax3.set_yticks([0, 1])
            ax3.set_yticklabels(['Range', 'Trend'])
        
        if 'atr' in self.merged.columns:
            ax3_twin = ax3.twinx()
            ax3_twin.plot(self.merged['timestamp'], self.merged['atr'], color='orange', alpha=0.5, label='ATR', linestyle='--')
            ax3_twin.set_ylabel('ATR')
            # ax3_twin.legend(loc='upper right')

        ax3.set_title('Market Regime & Volatility')
        ax3.grid(True)
        
        plt.tight_layout()
        plt.savefig(filename)
        print(f"Performance plot saved to {filename}")

    def plot_trades(self, trades_list, filename='trades_analysis.png'):
        """
        Plot entry/exit points on price chart.
        """
        # Placeholder for trade visualization
        pass
