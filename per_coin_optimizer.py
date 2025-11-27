import optuna
import pandas as pd
import numpy as np
import yaml
from data.fetcher import DataFetcher
from strategy.indicators import Indicators
from strategy.regime import RegimeDetection
from strategy.logic import StrategyLogic
from analysis.backtest import BacktestEngine

def load_config(path='config.yaml'):
    with open(path, 'r', encoding='utf-8-sig') as file:
        return yaml.safe_load(file)

def objective(trial):
    global current_symbol, cached_df
    
    # 1. Load Base Config
    config = load_config()
    
    # 2. Suggest Parameters
    config['strategy']['indicators']['ma_short'] = trial.suggest_int('ma_short', 10, 100)
    config['strategy']['indicators']['ma_long'] = trial.suggest_int('ma_long', 100, 300)
    config['strategy']['indicators']['rsi_period'] = trial.suggest_int('rsi_period', 10, 30)
    config['strategy']['indicators']['adx_threshold'] = trial.suggest_int('adx_threshold', 15, 35)
    config['strategy']['risk']['stop_loss_atr'] = trial.suggest_float('stop_loss_atr', 2.0, 5.0)
    config['strategy']['risk']['take_profit_atr'] = trial.suggest_float('take_profit_atr', 2.0, 8.0)
    
    # 3. Prepare Data
    if cached_df is None or cached_df.empty:
        return 0.0
        
    df = cached_df.copy()

    # 4. Recalculate Indicators
    inds = config['strategy']['indicators']
    df = Indicators.ma_crossover(df, short_window=inds['ma_short'], long_window=inds['ma_long'])
    df = Indicators.rsi(df, window=inds['rsi_period'])
    df = Indicators.bollinger_bands(df, window=inds['bb_window'], num_std=inds['bb_std'])
    df = Indicators.atr(df, window=inds['atr_window'])
    df = Indicators.adx(df, window=14)
    try:
        df = Indicators.garch_volatility(df)
    except:
        df['garch_vol'] = 2.0
        
    regime = RegimeDetection(df)
    df = regime.detect_regime()

    # 5. Run Backtest
    engine = BacktestEngine(
        initial_capital=config['backtest']['initial_capital'], 
        fee=config['backtest'].get('fee', 0.001),
        max_drawdown=0.15 
    )
    logic = StrategyLogic(config)
    
    def strategy_wrapper(row, capital, current_position):
        return logic.get_signal(row, capital, current_position)

    results = engine.run(df, strategy_wrapper)
    
    # 6. Calculate Metric
    metrics = engine.calculate_metrics()
    profit_factor = metrics['profit_factor']
    win_rate = metrics['win_rate']
    
    # Constraints (Relaxed for per-coin)
    if metrics['total_trades'] < 20: 
        return 0.0
    if win_rate < 45.0: 
        return 0.0
        
    # Multi-objective: PF + WR bonus
    score = profit_factor + (win_rate / 100.0)
    
    print(f"  Trial {trial.number}: PF={profit_factor:.2f}, WR={win_rate:.2f}%, Trades={metrics['total_trades']}, Score={score:.2f}")
    return score

def optimize_coin(symbol, config):
    global current_symbol, cached_df
    current_symbol = symbol
    
    print(f"\n--- Optimizing {symbol} ---")
    
    # Fetch data
    source = config['backtest'].get('source', 'yahoo')
    fetcher = DataFetcher(source=source)
    timeframe = config['backtest']['timeframe']
    limit = 18000
    
    print(f"Fetching data...")
    cached_df = fetcher.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    if cached_df is None or cached_df.empty:
        print(f"!!! ERROR: No data for {symbol}. Skipping. !!!")
        return None
    
    print(f"Running optimization (20 trials)...")
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=20, show_progress_bar=False) 

    print(f"Best trial for {symbol}:")
    trial = study.best_trial
    print(f"  Score: {trial.value:.2f}")
    print(f"  Params: {trial.params}")
    
    return trial.params

if __name__ == "__main__":
    print("--- Per-Coin Optimization ---")
    
    config = load_config()
    symbols = config['backtest']['symbols']
    
    results = {}
    
    for symbol in symbols:
        try:
            params = optimize_coin(symbol, config)
            if params:
                results[symbol] = params
        except Exception as e:
            print(f"Error optimizing {symbol}: {e}")
    
    print("\n" + "="*60)
    print("OPTIMIZATION RESULTS")
    print("="*60)
    for symbol, params in results.items():
        print(f"{symbol}: {params}")
    
    print("\nSave these to config manually or run a verification backtest.")
