import yaml
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from data.fetcher import DataFetcher
from strategy.indicators import Indicators
from strategy.regime import RegimeDetection
from strategy.logic import StrategyLogic
from analysis.backtest import BacktestEngine
from analysis.visualizer import Visualizer
from utils.telegram_notifier import TelegramNotifier
import time

def load_config(path='config.yaml'):
    with open(path, 'r', encoding='utf-8-sig') as file:
        return yaml.safe_load(file)

def run_strategy_for_symbol(symbol, config):
    print(f"\n--- Processing {symbol} ---")
    
    # 1. Data Layer
    source = config['backtest'].get('source', 'yahoo')
    fetcher = DataFetcher(source=source)
    timeframe = config['backtest']['timeframe']
    limit = config['backtest']['limit']
    
    print(f"Fetching {limit} candles for {symbol} ({timeframe})...")
    df = fetcher.fetch_ohlcv(symbol, timeframe, limit)
    
    if df is None or df.empty:
        print(f"!!! WARNING: No data for {symbol}. Skipping. !!!")
        return None

    # 2. Strategy Layer
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
        
    regime_detector = RegimeDetection(df)
    df = regime_detector.detect_regime()

    # 3. Backtest
    engine = BacktestEngine(
        initial_capital=config['backtest']['initial_capital'], 
        fee=config['backtest'].get('fee', 0.001),
        max_drawdown=config['strategy']['risk'].get('max_drawdown', 0.15)
    )
    
    logic = StrategyLogic(config)
    def strategy_wrapper(row, capital, current_position):
        return logic.get_signal(row, capital, current_position)

    results = engine.run(df, strategy_wrapper)
    metrics = engine.calculate_metrics()
    
    # Return summary
    return {
        'symbol': symbol,
        'profit_factor': metrics['profit_factor'],
        'win_rate': metrics['win_rate'],
        'total_trades': metrics['total_trades'],
        'max_drawdown': metrics['max_drawdown'],
        'total_return': ((results['equity'].iloc[-1] - config['backtest']['initial_capital']) / config['backtest']['initial_capital']) * 100,
        'final_equity': results['equity'].iloc[-1]
    }

def main():
    print("--- Starting Multi-Asset Quant Strategy Pipeline ---")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Telegram notifier
    telegram = None
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if bot_token and chat_id:
            telegram = TelegramNotifier(bot_token, chat_id)
            print(" Telegram notifications enabled")
        else:
            print(" Telegram credentials not found in .env")
    except Exception as e:
        print(f" Telegram initialization failed: {e}")
    
    config = load_config()
    if not config:
        print("Failed to load config. Exiting.")
        return

    # Handle single symbol vs list of symbols
    if 'symbols' in config['backtest']:
        symbols = config['backtest']['symbols']
    else:
        symbols = [config['backtest']['symbol']]
        
    print(f"Targeting {len(symbols)} assets: {symbols}")
    
    # Send start notification
    if telegram:
        try:
            telegram.send_start_notification(symbols)
        except Exception as e:
            print(f" Failed to send start notification: {e}")
    
    portfolio_results = []
    start_time = time.time()
    
    for symbol in symbols:
        try:
            res = run_strategy_for_symbol(symbol, config)
            if res:
                portfolio_results.append(res)
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            if telegram:
                try:
                    telegram.send_alert("Backtest Hatası", f"{symbol}: {str(e)}")
                except:
                    pass
            
    # Portfolio Summary
    print("\n" + "="*60)
    print(f"{'SYMBOL':<10} | {'PF':<6} | {'WR%':<6} | {'TRADES':<6} | {'MDD%':<6} | {'RETURN%':<8}")
    print("-" * 60)
    
    total_return_sum = 0
    total_pf_sum = 0
    valid_count = 0
    
    for res in portfolio_results:
        print(f"{res['symbol']:<10} | {res['profit_factor']:<6.2f} | {res['win_rate']:<6.2f} | {res['total_trades']:<6} | {res['max_drawdown']:<6.2f} | {res['total_return']:<8.2f}")
        total_return_sum += res['total_return']
        total_pf_sum += res['profit_factor']
        valid_count += 1
        
    print("-" * 60)
    
    if valid_count > 0:
        avg_return = total_return_sum / valid_count
        avg_pf = total_pf_sum / valid_count
        print(f"{'AVERAGE':<10} | {avg_pf:<6.2f} | {'-':<6} | {'-':<6} | {'-':<6} | {avg_return:<8.2f}")
    
    print("="*60)
    print("Check individual logs for details.")
    
    # Send portfolio summary to Telegram
    if telegram and portfolio_results:
        try:
            telegram.send_portfolio_summary(portfolio_results)
            duration = time.time() - start_time
            telegram.send_completion(duration)
            print(" Portfolio summary sent to Telegram")
        except Exception as e:
            print(f" Failed to send Telegram summary: {e}")

if __name__ == "__main__":
    main()
