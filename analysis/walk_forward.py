import pandas as pd
import numpy as np
import optuna
import yaml
from data.fetcher import DataFetcher
from strategy.indicators import Indicators
from strategy.regime import RegimeDetection
from strategy.logic import StrategyLogic
from analysis.backtest import BacktestEngine

def load_config(path='config.yaml'):
    with open(path, 'r', encoding='utf-8-sig') as file:
        return yaml.safe_load(file)

def optimize_on_data(df_train, base_config):
    def objective(trial):
        config = base_config.copy()
        config['strategy']['indicators']['ma_short'] = trial.suggest_int('ma_short', 10, 100)
        config['strategy']['indicators']['ma_long'] = trial.suggest_int('ma_long', 100, 300)
        config['strategy']['risk']['stop_loss_atr'] = trial.suggest_float('stop_loss_atr', 2.0, 5.0)
        
        # Recalculate indicators for this trial (Simplified: assuming indicators depend on params)
        # In reality, we need to re-run indicators.
        # For speed, we just re-run indicators on df_train inside objective
        
        inds = config['strategy']['indicators']
        temp_df = df_train.copy()
        temp_df = Indicators.ma_crossover(temp_df, short_window=inds['ma_short'], long_window=inds['ma_long'])
        temp_df = Indicators.rsi(temp_df, window=inds['rsi_period'])
        temp_df = Indicators.bollinger_bands(temp_df, window=inds['bb_window'], num_std=inds['bb_std'])
        temp_df = Indicators.atr(temp_df, window=inds['atr_window'])
        try:
            temp_df = Indicators.garch_volatility(temp_df)
        except:
            temp_df['garch_vol'] = 2.0
            
        regime = RegimeDetection(temp_df)
        temp_df = regime.detect_regime()
        
        engine = BacktestEngine(initial_capital=config['backtest']['initial_capital'], fee=0.001)
        logic = StrategyLogic(config)
        
        def strategy_wrapper(row, capital, current_position):
            return logic.get_signal(row, capital, current_position)

        results = engine.run(temp_df, strategy_wrapper)
        
        final_equity = results['equity'].iloc[-1]
        ret = (final_equity - config['backtest']['initial_capital'])
        return ret

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=10) # Fast optimization
    return study.best_params

def run_walk_forward():
    print("--- Starting Walk-Forward Analysis ---")
    config = load_config()
    
    # 1. Fetch Data
    fetcher = DataFetcher()
    df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=2000)
    
    if df is None or df.empty:
        print("Using mock data.")
        dates = pd.date_range(start='2023-01-01', periods=2000, freq='1h')
        df = pd.DataFrame({
            'timestamp': dates,
            'open': 100, 'high': 105, 'low': 95, 'close': 100, 'volume': 1000
        })
        import numpy as np
        returns = np.random.normal(0, 0.01, 2000)
        price_path = 100 * np.cumprod(1 + returns)
        df['close'] = price_path
        df['open'] = price_path
        df['high'] = price_path * 1.01
        df['low'] = price_path * 0.99

    # 2. Split Data (50% Train, 50% Test)
    split_idx = int(len(df) * 0.5)
    df_train = df.iloc[:split_idx].copy()
    df_test = df.iloc[split_idx:].copy()
    
    print(f"Train Set: {len(df_train)} candles")
    print(f"Test Set: {len(df_test)} candles")
    
    # 3. Optimize on Train
    print("Optimizing on Train Set...")
    best_params = optimize_on_data(df_train, config)
    print(f"Best Params: {best_params}")
    
    # 4. Test on Out-of-Sample (Test Set)
    print("Testing on Out-of-Sample Data...")
    
    # Update config with best params
    config['strategy']['indicators']['ma_short'] = best_params['ma_short']
    config['strategy']['indicators']['ma_long'] = best_params['ma_long']
    config['strategy']['risk']['stop_loss_atr'] = best_params['stop_loss_atr']
    
    # Prepare Test Data
    inds = config['strategy']['indicators']
    df_test = Indicators.ma_crossover(df_test, short_window=inds['ma_short'], long_window=inds['ma_long'])
    df_test = Indicators.rsi(df_test, window=inds['rsi_period'])
    df_test = Indicators.bollinger_bands(df_test, window=inds['bb_window'], num_std=inds['bb_std'])
    df_test = Indicators.atr(df_test, window=inds['atr_window'])
    try:
        df_test = Indicators.garch_volatility(df_test)
    except:
        df_test['garch_vol'] = 2.0
        
    regime = RegimeDetection(df_test)
    df_test = regime.detect_regime()
    
    engine = BacktestEngine(initial_capital=config['backtest']['initial_capital'], fee=0.001)
    logic = StrategyLogic(config)
    
    def strategy_wrapper(row, capital, current_position):
        return logic.get_signal(row, capital, current_position)

    results = engine.run(df_test, strategy_wrapper)
    
    final_equity = results['equity'].iloc[-1]
    initial_cap = config['backtest']['initial_capital']
    ret = ((final_equity - initial_cap) / initial_cap) * 100
    
    print(f"Out-of-Sample Return: {ret:.2f}%")
    print(f"Final Equity: ")

if __name__ == "__main__":
    run_walk_forward()
