# Hermes Trade v0.1

A live price chart dashboard for algorithmic trading built with Dash and yfinance.

## Features

- **Real-time price charts**: Candlestick charts with volume bars
- **Multiple assets**: Stocks (AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA), Crypto (BTC-USD, ETH-USD), Forex (EUR-USD), Commodities (Gold)
- **Flexible timeframes**: 1d, 5d, 1mo, 3mo, 6mo, 1y
- **Multiple intervals**: 1m, 5m, 15m, 30m, 1h, 1d
- **Auto-refresh**: Updates every 60 seconds
- **Live metrics**: Current price, % change, last update timestamp
- **Dark theme**: Professional CYBORG theme optimized for trading

## Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

Or with `pip3`:
```bash
pip3 install -r requirements.txt
```

Or with `uv`:
```bash
uv pip install -r requirements.txt --system
```

2. **Run the application:**

```bash
python3 app.py
```

3. **Open in browser:**

Navigate to `http://localhost:8050`

## Tech Stack

- **Dash** — Web framework
- **Plotly** — Interactive charts
- **yfinance** — Free market data (no API key required)
- **Bootstrap (Cyborg theme)** — Dark UI styling
- **Pandas** — Data processing

## Usage

1. Select a symbol from the dropdown (stocks, crypto, forex, commodities)
2. Choose a time period (1d to 1y)
3. Select an interval for candles (1m to 1d)
4. Chart updates automatically every 60 seconds
5. View current price, % change, and last update time in the header

## License

MIT License - See LICENSE file for details
