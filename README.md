# Market Dashboard

A tool for macro market judgment based on the "Five-Step Method" (Funding, Sentiment, Trend, Timing, Style).

## Overview

This dashboard visualizes key market indicators to assist in decision making:
1.  **Funding**: Market liquidity and margin balance.
2.  **Sentiment**: Market temperature and panic levels.
3.  **Trend**: Major index trends (EMA200).
4.  **Timing**: Volatility contraction and breakout signals.
5.  **Style**: Relative strength between sectors (e.g., Resources vs. Tech).

## Usage

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the dashboard:
    ```bash
    streamlit run app.py
    ```

## Data Source

-   **Baostock**: Official Chinese stock market data API.
