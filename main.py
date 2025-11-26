import pandas as pd
import numpy as np
from strategy.indicators import Indicators
from strategy.regime import RegimeDetection
from filters.imbalance import OrderBookImbalance
from filters.metalabeling import MetaLabeling
from risk.sizing import PositionSizing
from risk.guardrails import RiskGuardrails
from execution.router import SmartOrderRouter
from execution.algo import ExecutionAlgo
from analysis.permutation import PermutationTest

def run_pipeline():
    print("--- Starting Quant Strategy Pipeline ---")

    # 1. Data Layer (Mock Data)
    print("\n[1] Data Layer")
    dates = pd.date_range(start='2023-01-01', periods=100, freq='1h')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(100, 110, 100),
        'high': np.random.uniform(110, 120, 100),
        'low': np.random.uniform(90, 100, 100),
        'close': np.random.uniform(100, 110, 100),
        'volume': np.random.uniform(1000, 5000, 100)
    })
    print(f"Loaded {len(df)} data points.")

    # 2. Strategy Layer
    print("\n[2] Strategy Layer")
    df = Indicators.donchian_channel(df)
    df = Indicators.atr(df)
    
    regime_detector = RegimeDetection(df)
    df = regime_detector.detect_regime()
    print(f"Current Regime: {df['regime'].iloc[-1]}")

    # 3. Filter Layer
    print("\n[3] Filter Layer")
    # Mock Order Book
    order_book = {'bids': [[99, 1], [98, 2]], 'asks': [[101, 1], [102, 1]]}
    imbalance = OrderBookImbalance.calculate_imbalance(order_book)
    print(f"Order Book Imbalance: {imbalance:.2f}")

    # 4. Risk Layer
    print("\n[4] Risk Layer")
    sizer = PositionSizing(target_volatility=0.20)
    current_vol = 0.15 # Mock annualized vol
    capital = 10000
    size = sizer.calculate_volatility_target_size(capital, current_vol)
    print(f"Calculated Position Size: ")

    guard = RiskGuardrails()
    guard.update_equity(10000)
    guard.update_equity(9500)
    is_breach = guard.check_drawdown(9500)
    print(f"Drawdown Breach: {is_breach}")

    # 5. Execution Layer
    print("\n[5] Execution Layer")
    router = SmartOrderRouter()
    algo = ExecutionAlgo(router)
    # Simulate TWAP
    algo.twap('BTC/USDT', 'buy', 1.0, duration_minutes=1)

    # 6. Analysis Layer
    print("\n[6] Analysis Layer")
    perm = PermutationTest()
    mock_returns = np.random.normal(0.001, 0.02, 100)
    res = perm.run_test(mock_returns)
    print(f"Permutation Test p-value: {res['p_value']:.4f}")

    print("\n--- Pipeline Completed Successfully ---")

if __name__ == "__main__":
    run_pipeline()
