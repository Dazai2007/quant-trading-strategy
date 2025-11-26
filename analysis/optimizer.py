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
    # 1. Load Base Config
    config = load_config()
    
    # 2. Suggest Parameters
    config['strategy']['indicators']['ma_short'] = trial.suggest_int('ma_short', 10, 100)
    config['strategy']['indicators']['ma_long'] = trial.suggest_int('ma_long', 100, 300)
    config['strategy']['indicators']['rsi_period'] = trial.suggest_int('rsi_period', 10, 30)
    # config['strategy']['indicators']['adx_threshold'] = trial.suggest_int('adx_threshold', 15, 40)
    config['strategy']['risk']['stop_loss_atr'] = trial.suggest_float('stop_loss_atr', 1.0, 5.0)
    config['strategy']['risk']['take_profit_atr'] = trial.suggest_float('take_profit_atr', 2.0, 10.0)
    
    # 3. Prepare Data (Load once ideally, but here we load inside for simplicity or pass it in)
    # For speed, we should load data outside.
    # But to keep it self-contained in objective, we'll fetch mock or real.
    # BETTER: Use global data variable or class.
    
    global cached_df
    df = cached_df.copy()

    # 4. Recalculate Indicators (Dynamic based on params)
    inds = config['strategy']['indicators']
    df = Indicators.ma_crossover(df, short_window=inds['ma_short'], long_window=inds['ma_long'])
    df = Indicators.rsi(df, window=inds['rsi_period'])
    df = Indicators.bollinger_bands(df, window=inds['bb_window'], num_std=inds['bb_std'])
    df = Indicators.atr(df, window=inds['atr_window'])
    # df = Indicators.adx(df, window=14)
    try:
        df = Indicators.garch_volatility(df)
    except:
        df['garch_vol'] = 2.0
        
    regime = RegimeDetection(df)
    df = regime.detect_regime()

    # 5. Run Backtest
    engine = BacktestEngine(initial_capital=config['backtest']['initial_capital'], fee=config['backtest'].get('fee', 0.001))
    logic = StrategyLogic(config)
    
    def strategy_wrapper(row, capital, current_position):
        return logic.get_signal(row, capital, current_position)

    results = engine.run(df, strategy_wrapper)
    
    # 6. Calculate Metric: Profit Factor
    metrics = engine.calculate_metrics()
    profit_factor = metrics['profit_factor']
    
    # Penalize low number of trades to avoid overfitting to 1 lucky trade
    if metrics['total_trades'] < 5:
        return 0.0
        
    return profit_factor

if __name__ == "__main__":
    print("--- Starting Optimization ---")
    
    # Load Data Once
    fetcher = DataFetcher()
    # Use a longer period for optimization if possible
    cached_df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=1000)
    
    if cached_df is None or cached_df.empty:
        print("Using mock data for optimization.")
        dates = pd.date_range(start='2023-01-01', periods=1000, freq='1h')
        cached_df = pd.DataFrame({
            'timestamp': dates,
            'open': 100, 'high': 105, 'low': 95, 'close': 100, 'volume': 1000
        })
        import numpy as np
        returns = np.random.normal(0, 0.01, 1000)
        price_path = 100 * np.cumprod(1 + returns)
        cached_df['close'] = price_path
        cached_df['open'] = price_path
        cached_df['high'] = price_path * 1.01
        cached_df['low'] = price_path * 0.99

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=20) # 20 trials for demo speed

    print("Number of finished trials: ", len(study.trials))
    print("Best trial:")
    trial = study.best_trial

    print("  Value: ", trial.value)
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")
        
    # Save best params to a new config file?
    # For now just print.
