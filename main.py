import pandas as pd
import yaml
import sys

# Import modules
from data.fetcher import DataFetcher
from strategy.indicators import Indicators
from strategy.regime import RegimeDetection
from strategy.logic import StrategyLogic
from analysis.backtest import BacktestEngine
from analysis.visualizer import Visualizer

def load_config(path='config.yaml'):
    try:
        with open(path, 'r', encoding='utf-8-sig') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def main():
    print("--- Starting Quant Strategy Pipeline (Full Integration) ---")
    
    # 0. Load Config
    config = load_config()
    if not config:
        print("Failed to load config. Exiting.")
        return

    # 1. Data Layer
    print("\n[1] Data Layer")
    fetcher = DataFetcher()
    symbol = config['backtest']['symbol']
    timeframe = config['backtest']['timeframe']
    limit = config['backtest']['limit']
    
    print(f"Fetching {limit} candles for {symbol} ({timeframe})...")
    df = fetcher.fetch_ohlcv(symbol, timeframe, limit)
    
    if df is None or df.empty:
        print("Warning: Failed to fetch real data. Using mock data for demonstration.")
        dates = pd.date_range(start='2023-01-01', periods=limit, freq=timeframe)
        df = pd.DataFrame({
            'timestamp': dates,
            'open': 100, 'high': 105, 'low': 95, 'close': 100, 'volume': 1000
        })
        import numpy as np
        returns = np.random.normal(0, 0.01, limit)
        price_path = 100 * np.cumprod(1 + returns)
        df['close'] = price_path
        df['open'] = price_path
        df['high'] = price_path * 1.01
        df['low'] = price_path * 0.99
    
    print(f"Loaded {len(df)} data points.")

    # 2. Strategy Layer (Indicators & Regime)
    print("\n[2] Strategy Layer")
    print("Calculating indicators...")
    inds = config['strategy']['indicators']
    df = Indicators.ma_crossover(df, short_window=inds['ma_short'], long_window=inds['ma_long'])
    df = Indicators.rsi(df, window=inds['rsi_period'])
    df = Indicators.bollinger_bands(df, window=inds['bb_window'], num_std=inds['bb_std'])
    df = Indicators.atr(df, window=inds['atr_window'])
    try:
        df = Indicators.garch_volatility(df)
    except:
        df['garch_vol'] = 2.0

    print("Detecting Regimes...")
    regime_detector = RegimeDetection(df)
    df = regime_detector.detect_regime()
    print(f"Current Regime: {df['regime'].iloc[-1]}")

    # 3. Backtest / Execution Simulation
    print("\n[3] Backtest & Execution Simulation")
    engine = BacktestEngine(
        initial_capital=config['backtest']['initial_capital'], 
        fee=config['backtest'].get('fee', 0.001),
        max_drawdown=config['strategy']['risk'].get('max_drawdown', 0.20)
    )
    logic = StrategyLogic(config)

    def strategy_wrapper(row, capital, current_position):
        return logic.get_signal(row, capital, current_position)

    print("Running Backtest Engine...")
    results = engine.run(df, strategy_wrapper)
    
    final_equity = results['equity'].iloc[-1]
    initial_cap = config['backtest']['initial_capital']
    ret = ((final_equity - initial_cap) / initial_cap) * 100
    print(f"Final Equity: ")
    print(f"Total Return: {ret:.2f}%")
    
    # Check if circuit breaker triggered
    if engine.guardrails.circuit_breaker_triggered:
        print("!!! CIRCUIT BREAKER TRIGGERED: Trading Halted due to Max Drawdown !!!")

    # 4. Visualization
    print("\n[4] Visualization")
    print("Generating performance plots...")
    viz = Visualizer(results, df)
    viz.plot_performance(filename='pipeline_performance.png')
    
    print("\n--- Pipeline Completed Successfully ---")
    print("Check 'pipeline_performance.png' for results.")

if __name__ == "__main__":
    main()
