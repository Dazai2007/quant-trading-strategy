import pandas as pd
import matplotlib.pyplot as plt
from data.fetcher import DataFetcher
from strategy.indicators import Indicators
from strategy.regime import RegimeDetection
from strategy.logic import StrategyLogic
from analysis.backtest import BacktestEngine

def main():
    print("--- Starting Backtest with Exit Logic ---")
    
    # 1. Fetch Data
    print("Fetching data...")
    fetcher = DataFetcher()
    df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=1000)
    
    if df is None or df.empty:
        print("Failed to fetch data. Using mock data.")
        dates = pd.date_range(start='2023-01-01', periods=1000, freq='1h')
        df = pd.DataFrame({
            'timestamp': dates,
            'open': 100, 'high': 105, 'low': 95, 'close': 100, 'volume': 1000
        })
        import numpy as np
        returns = np.random.normal(0, 0.01, 1000)
        price_path = 100 * np.cumprod(1 + returns)
        df['close'] = price_path
        df['open'] = price_path
        df['high'] = price_path * 1.01
        df['low'] = price_path * 0.99

    print(f"Data points: {len(df)}")

    # 2. Calculate Indicators
    print("Calculating indicators...")
    df = Indicators.ma_crossover(df)
    df = Indicators.rsi(df)
    df = Indicators.bollinger_bands(df)
    df = Indicators.atr(df)
    try:
        df = Indicators.garch_volatility(df)
    except Exception as e:
        print(f"GARCH failed: {e}. Using fallback.")
        df['garch_vol'] = 2.0

    # 3. Detect Regime
    print("Detecting regimes...")
    regime = RegimeDetection(df)
    df = regime.detect_regime()

    # 4. Run Backtest
    print("Running backtest engine...")
    engine = BacktestEngine(initial_capital=10000)
    logic = StrategyLogic(target_volatility=0.20)
    
    # Update wrapper to pass current_position
    def strategy_wrapper(row, capital, current_position):
        return logic.get_signal(row, capital, current_position)

    results = engine.run(df, strategy_wrapper)
    
    # 5. Analyze Results
    final_equity = results['equity'].iloc[-1]
    print(f"Final Equity: ")
    print(f"Return: {((final_equity - 10000)/10000)*100:.2f}%")

    # 6. Visualize
    print("Generating plot...")
    plt.figure(figsize=(12, 6))
    plt.plot(results['timestamp'], results['equity'], label='Strategy Equity')
    plt.title('Backtest Results (with Exits): BTC/USDT 1h')
    plt.xlabel('Date')
    plt.ylabel('Equity ($)')
    plt.legend()
    plt.grid(True)
    plt.savefig('backtest_result_exits.png')
    print("Plot saved to backtest_result_exits.png")

if __name__ == "__main__":
    main()
