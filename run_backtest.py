import pandas as pd
import matplotlib.pyplot as plt
import yaml
from data.fetcher import DataFetcher
from strategy.indicators import Indicators
from strategy.regime import RegimeDetection
from strategy.logic import StrategyLogic
from analysis.backtest import BacktestEngine

def load_config(path='config.yaml'):
    # Use utf-8-sig to handle BOM if present
    with open(path, 'r', encoding='utf-8-sig') as file:
        return yaml.safe_load(file)

def main():
    print("--- Starting Backtest (Config Driven) ---")
    try:
        config = load_config()
        print(f"DEBUG: Loaded config keys: {[repr(k) for k in config.keys()]}")
        print(f"DEBUG: Config content: {config}")
    except Exception as e:
        print(f"CRITICAL ERROR loading config: {e}")
        return

    # 1. Fetch Data
    print("Fetching data...")
    fetcher = DataFetcher()
    symbol = config['backtest']['symbol']
    timeframe = config['backtest']['timeframe']
    limit = config['backtest']['limit']
    
    df = fetcher.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    if df is None or df.empty:
        print("Failed to fetch data. Using mock data.")
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

    print(f"Data points: {len(df)}")

    # 2. Calculate Indicators
    print("Calculating indicators...")
    inds = config['strategy']['indicators']
    df = Indicators.ma_crossover(df, short_window=inds['ma_short'], long_window=inds['ma_long'])
    df = Indicators.rsi(df, window=inds['rsi_period'])
    df = Indicators.bollinger_bands(df, window=inds['bb_window'], num_std=inds['bb_std'])
    df = Indicators.atr(df, window=inds['atr_window'])
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
    engine = BacktestEngine(initial_capital=config['backtest']['initial_capital'], fee=config['backtest'].get('fee', 0.0))
    logic = StrategyLogic(config)
    
    def strategy_wrapper(row, capital, current_position):
        return logic.get_signal(row, capital, current_position)

    results = engine.run(df, strategy_wrapper)
    
    # 5. Analyze Results
    final_equity = results['equity'].iloc[-1]
    initial_cap = config['backtest']['initial_capital']
    print(f"Final Equity: ")
    print(f"Return: {((final_equity - initial_cap)/initial_cap)*100:.2f}%")

    # 6. Visualize
    print("Generating plot...")
    plt.figure(figsize=(12, 6))
    plt.plot(results['timestamp'], results['equity'], label='Strategy Equity')
    plt.title(f'Backtest Results: {symbol} {timeframe}')
    plt.xlabel('Date')
    plt.ylabel('Equity ($)')
    plt.legend()
    plt.grid(True)
    plt.savefig('backtest_result_config.png')
    print("Plot saved to backtest_result_config.png")

if __name__ == "__main__":
    main()
