# Stock Screener - Quick Reference Guide

## Common Trading Scenarios

### Momentum Trading

#### Find Breakout Candidates
```bash
# Preset
curl "http://localhost:5001/api/stock-all-data?preset=momentum_breakout"

# Custom
curl "http://localhost:5001/api/stock-all-data?RSI_14_from=55&RSI_14_to=75&ADX_14_from=25&Relative_Volume_from=1.5"
```

#### Find Strong Uptrends
```bash
curl "http://localhost:5001/api/stock-all-data?preset=strong_uptrend"
```

### Mean Reversion Trading

#### Oversold Bounce Candidates
```bash
curl "http://localhost:5001/api/stock-all-data?preset=oversold_bounce"
```

#### Overbought for Shorting
```bash
curl "http://localhost:5001/api/stock-all-data?preset=overbought_short"
```

### Volatility-Based Trading

#### Low Volatility (Swing Trading)
```bash
curl "http://localhost:5001/api/stock-all-data?preset=low_volatility"
```

#### High Volatility (Day Trading)
```bash
curl "http://localhost:5001/api/stock-all-data?preset=high_volatility"
```

### Volume Analysis

#### Volume Surge Detection
```bash
curl "http://localhost:5001/api/stock-all-data?preset=volume_surge"
```

#### High Volume with Momentum
```bash
curl "http://localhost:5001/api/stock-all-data?Relative_Volume_from=2&MACD_Hist_from=0&ADX_14_from=20"
```

## Indicator Combinations

### Bollinger Band Strategies

#### BB Squeeze Breakout
```bash
curl "http://localhost:5001/api/stock-all-data?BB_Width_to=5&Relative_Volume_from=1.5"
```

#### BB Bounce from Lower Band
```bash
curl "http://localhost:5001/api/stock-all-data?BB_Position_to=20&RSI_14_to=35"
```

#### BB Rejection at Upper Band
```bash
curl "http://localhost:5001/api/stock-all-data?BB_Position_from=80&Williams_R_14_from=-20"
```

### MACD Strategies

#### MACD Bullish Crossover
```bash
curl "http://localhost:5001/api/stock-all-data?MACD_Hist_from=0&RSI_14_from=45&RSI_14_to=65"
```

#### MACD Divergence Setup
```bash
# Negative MACD but positive histogram (bullish divergence)
curl "http://localhost:5001/api/stock-all-data?MACD_to=-0.5&MACD_Hist_from=0.1"
```

### Multi-Timeframe Alignment

#### Price Above All Major MAs
```bash
curl "http://localhost:5001/api/stock-all-data?Price_vs_SMA20_Pct_from=0&Price_vs_SMA50_Pct_from=0&Price_vs_SMA200_Pct_from=0"
```

#### Golden Cross Setup (50 > 200 MA)
```bash
curl "http://localhost:5001/api/stock-all-data?Price_vs_SMA50_Pct_from=0&Price_vs_SMA200_Pct_from=-2&Price_vs_SMA200_Pct_to=5"
```

## Advanced POST Queries

### Top 10 Momentum Stocks
```bash
curl -X POST http://localhost:5001/api/stock-screen \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "RSI_14": {"from": 55, "to": 75},
      "ADX_14": {"from": 25},
      "Relative_Volume": {"from": 1.5}
    },
    "sort_by": "ADX_14",
    "sort_order": "desc",
    "limit": 10
  }'
```

### Most Oversold Stocks
```bash
curl -X POST http://localhost:5001/api/stock-screen \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "RSI_14": {"from": 20, "to": 35}
    },
    "sort_by": "RSI_14",
    "sort_order": "asc",
    "limit": 20
  }'
```

### Highest Volatility Stocks
```bash
curl -X POST http://localhost:5001/api/stock-screen \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "ATR_Pct": {"from": 2}
    },
    "sort_by": "ATR_Pct",
    "sort_order": "desc",
    "limit": 15
  }'
```

## Indicator Quick Reference

### Momentum Indicators

| Indicator | Range | Overbought | Oversold | Best For |
|-----------|-------|------------|----------|----------|
| RSI_14 | 0-100 | >70 | <30 | Momentum & Reversals |
| Williams_R_14 | -100 to 0 | >-20 | <-80 | Overbought/Oversold |
| Stoch_K | 0-100 | >80 | <20 | Short-term Momentum |
| MFI_14 | 0-100 | >80 | <20 | Volume-weighted Momentum |
| CCI_14 | No fixed | >100 | <-100 | Cyclical Trends |

### Trend Indicators

| Indicator | Interpretation |
|-----------|----------------|
| ADX_14 | >25 = Strong Trend, <20 = Weak/Ranging |
| Price_vs_SMA20_Pct | >0 = Above MA (Bullish), <0 = Below MA (Bearish) |
| Plus_DI vs Minus_DI | Plus > Minus = Uptrend, Minus > Plus = Downtrend |
| MACD_Hist | >0 = Bullish, <0 = Bearish |

### Volatility Indicators

| Indicator | Interpretation |
|-----------|----------------|
| ATR_Pct | Higher = More Volatile |
| BB_Width | Narrow = Low Vol (Squeeze), Wide = High Vol |
| Hist_Volatility_20 | Annualized volatility percentage |

### Volume Indicators

| Indicator | Interpretation |
|-----------|----------------|
| Relative_Volume | >1.5 = Above Average, >2.0 = Surge |
| ADOSC | >0 = Accumulation, <0 = Distribution |

## Screening Workflows

### Day Trading Workflow

1. **Find High Volatility Stocks**
```bash
curl "http://localhost:5001/api/stock-all-data?preset=high_volatility"
```

2. **Filter for Volume**
```bash
curl "http://localhost:5001/api/stock-all-data?ATR_Pct_from=3&Relative_Volume_from=1.5"
```

3. **Check for Setup**
```bash
curl "http://localhost:5001/api/stock-all-data?ATR_Pct_from=3&BB_Position_from=60&MACD_Hist_from=0"
```

### Swing Trading Workflow

1. **Find Trending Stocks**
```bash
curl "http://localhost:5001/api/stock-all-data?preset=strong_uptrend"
```

2. **Filter for Pullbacks**
```bash
curl "http://localhost:5001/api/stock-all-data?Price_vs_SMA50_Pct_from=0&Price_vs_SMA20_Pct_from=-5&Price_vs_SMA20_Pct_to=0"
```

3. **Confirm with RSI**
```bash
curl "http://localhost:5001/api/stock-all-data?Price_vs_SMA50_Pct_from=0&RSI_14_from=35&RSI_14_to=55"
```

### Position Trading Workflow

1. **Find Strong Long-term Trends**
```bash
curl "http://localhost:5001/api/stock-all-data?Price_vs_SMA200_Pct_from=10&ADX_14_from=30"
```

2. **Low Volatility Preference**
```bash
curl "http://localhost:5001/api/stock-all-data?Price_vs_SMA200_Pct_from=10&ATR_Pct_to=2"
```

## Risk Management Tips

### Position Sizing Based on ATR
- **Low Risk:** ATR_Pct < 1.5 → Larger position size
- **Medium Risk:** ATR_Pct 1.5-3.0 → Normal position size
- **High Risk:** ATR_Pct > 3.0 → Smaller position size

### Stop Loss Placement
- **Tight Stops:** 1-1.5x ATR_14
- **Normal Stops:** 2-2.5x ATR_14
- **Loose Stops:** 3-4x ATR_14

### Entry Timing
- **Conservative:** Wait for RSI 40-60 range
- **Aggressive:** Enter on RSI >60 with momentum
- **Reversal:** Enter on RSI <30 with volume

## Data Maintenance

### Fetch Latest Data
```bash
cd backend/scripts
python fetch_stock_data.py
```

### Process Indicators
```bash
python process_stock_data.py
```

### Validate Data Quality
```bash
python validate_data.py
```

### Recommended Schedule
- **Daily:** Run fetch + process before market open
- **Weekly:** Run validation script
- **Monthly:** Review and update preset strategies

## Troubleshooting

### No Results Returned
- Check if data is fresh (use `max_age` parameter)
- Verify filters aren't too restrictive
- Try a preset to test connectivity

### Stale Data Warning
```bash
# Only show data from last 3 days
curl "http://localhost:5001/api/stock-all-data?max_age=3&preset=momentum_breakout"
```

### Performance Issues
- Use POST endpoint with limit parameter
- Narrow filters to reduce result set
- Consider caching frequent queries

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/config/indicators` | GET | Get all indicator metadata |
| `/api/config/presets` | GET | Get preset strategies |
| `/api/sp500` | GET | Get S&P 500 companies list |
| `/api/stock-all-data` | GET | Screen stocks with filters |
| `/api/stock-screen` | POST | Advanced screening with sorting |
| `/api/stock-data/<symbol>` | GET | Get data for specific symbol |

## Python Integration Example

```python
import requests
import pandas as pd

# Get momentum breakout stocks
response = requests.get(
    'http://localhost:5001/api/stock-all-data',
    params={'preset': 'momentum_breakout'}
)
stocks = response.json()
df = pd.DataFrame(stocks)

# Filter for top 10 by ADX
top_stocks = df.nlargest(10, 'ADX_14')
print(top_stocks[['Symbol', 'Close', 'RSI_14', 'ADX_14', 'Relative_Volume']])
```

## JavaScript/Frontend Integration Example

```javascript
// Fetch oversold stocks
fetch('http://localhost:5001/api/stock-all-data?preset=oversold_bounce')
  .then(response => response.json())
  .then(stocks => {
    console.log(`Found ${stocks.length} oversold stocks`);
    stocks.forEach(stock => {
      console.log(`${stock.Symbol}: RSI=${stock.RSI_14}, Williams=%R=${stock.Williams_R_14}`);
    });
  });
```

---

**Pro Tip:** Combine multiple filters for better accuracy. Single-indicator strategies often produce false signals.

**Remember:** Always backtest strategies and use proper risk management. Past performance doesn't guarantee future results.
