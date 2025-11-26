# 4-Layer Quant Trading Strategy

## Overview
This project implements a comprehensive quantitative trading strategy for Bitcoin, structured in 4 layers:
1.  **Regime Detection**: Identifies market state (Trend vs Mean Reversion).
2.  **Signal Filtering**: Uses Order Book Imbalance and Meta-labeling to filter signals.
3.  **Risk Management**: Applies Volatility Targeting and Max Drawdown guardrails.
4.  **Execution**: Simulates Smart Order Routing and Algo Execution (TWAP/POV).

## Project Structure
-   data/: Data fetching and storage.
-   strategy/: Indicators and regime logic.
-   ilters/: Signal filtering logic.
-   isk/: Position sizing and risk controls.
-   execution/: Order routing and execution algorithms.
-   nalysis/: Statistical tests and backtesting.

## Installation
1.  Create a virtual environment:
    `ash
    python -m venv venv
    .\venv\Scripts\activate
    `
2.  Install dependencies:
    `ash
    pip install -r requirements.txt
    `

## Usage
Run the full system integration test:
`ash
python main.py
`

## Modules
-   **Indicators**: Donchian, MA, RSI, BB, ATR, GARCH.
-   **Filters**: Order Book Imbalance, Random Forest Meta-labeling.
-   **Risk**: Volatility Targeting, Monte Carlo Simulation.
-   **Analysis**: Permutation Tests, Trade Dependence.

## Disclaimer
This is a research project. Real trading involves significant risk. The execution layer is currently a simulation.
