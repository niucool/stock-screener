# Enhanced Stock Screener System

## Overview

This enhanced stock screener system combines your existing technical analysis with Warren Buffett's fundamental analysis formulas, adding full automation and Telegram delivery. The system now:

1. **Finds oversold stocks** using technical indicators (Williams %R, RSI, etc.)
2. **Analyzes fundamentals** using Buffett's 10 investment formulas with SEC data
3. **Ranks stocks** by combined score (30% technical + 70% fundamental)
4. **Automatically delivers** top 10 stocks daily at 8:00 PM PST via Telegram
5. **Provides multiple scheduling options** (OpenClaw cron, systemd, Windows Task Scheduler)

## Key Enhancements vs. Original

| Feature | Original System | Enhanced System |
|---------|----------------|-----------------|
| **Analysis Type** | Technical only | Technical + Fundamental (Buffett formulas) |
| **Data Sources** | NASDAQ API + Yahoo Finance | + SEC EDGAR API (official filings) |
| **Automation** | Manual web UI | Fully automated daily scans |
| **Delivery** | Web browser | Telegram bot (mobile-friendly) |
| **Scheduling** | Manual refresh | Automatic 8:00 PM PST daily |
| **Quality Filter** | Risk categories | Buffett quality score (≥5/10 required) |
| **Ranking** | Basic filtering | Weighted scoring (30% tech + 70% fund) |

## Architecture

```
stock-screener/
├── backend/
│   ├── api/                    # Existing Flask API
│   ├── data/                   # SQLite databases
│   └── scripts/               # NEW: Enhanced scripts
│       ├── sec_api.py         # SEC EDGAR API client
│       ├── buffett_formulas.py # Buffett's 10 formulas
│       ├── combined_screener.py # Technical + fundamental
│       ├── telegram_bot.py    # Telegram delivery
│       └── schedule_screener.py # Scheduling setup
├── frontend/                  # Existing React UI
└── config/                   # NEW: Configuration files
```

## New Components

### 1. SEC API Client (`sec_api.py`)
- Fetches official financial data from SEC EDGAR
- Smart caching (7-day TTL for fundamentals)
- Ticker to CIK mapping
- Extracts key financial facts for Buffett formulas

### 2. Buffett Formula Engine (`buffett_formulas.py`)
- Implements Warren Buffett's 10 investment criteria:
  1. Cash Test: Cash > Total Debt
  2. Debt-to-Equity Ratio < 0.5
  3. Free Cash Flow to Debt > 0.25
  4. Return on Equity > 15%
  5. Current Ratio > 1.5
  6. Operating Margin > 12%
  7. Asset Turnover > 0.5
  8. Interest Coverage > 3×
  9. Earnings Stability (positive)
  10. Capital Allocation (ROE > 15%)
- Returns PASS/FAIL for each formula
- Calculates overall quality score (0-10)

### 3. Combined Screener (`combined_screener.py`)
- Finds oversold stocks (Williams %R < -80)
- Analyzes fundamentals for each
- Filters by minimum Buffett score (default: ≥5/10)
- Calculates combined score (30% technical + 70% fundamental)
- Ranks stocks and generates reports

### 4. Telegram Bot (`telegram_bot.py`)
- Sends formatted reports to Telegram
- Interactive commands: `/screen`, `/last`, `/help`
- Configurable via JSON file
- Supports both interactive bot and scheduled delivery

### 5. Scheduling System (`schedule_screener.py`)
- Multiple scheduling options:
  - **OpenClaw cron** (recommended for OpenClaw users)
  - **Systemd service/timer** (Linux servers)
  - **Windows Task Scheduler** (Windows machines)
- Daily at 8:00 PM PST (Monday-Friday)
- Automatic error handling and logging

## Installation & Setup

### Step 1: Install Dependencies

```bash
cd stock-screener/backend/scripts
pip install -r ../config/requirements.txt
```

Required packages:
- `yfinance` - Stock price data
- `pandas`, `numpy` - Data processing
- `requests` - HTTP requests
- `schedule` - Scheduling (optional)
- `python-telegram-bot` - Telegram integration (optional)

### Step 2: Configure Telegram Bot

1. Create a bot with [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
3. Get your chat ID (send message to bot, then visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`)
4. Run setup:

```bash
python telegram_bot.py --mode=setup
```

### Step 3: Test the System

```bash
# Test the combined screener
python combined_screener.py

# Test Telegram delivery
python telegram_bot.py --mode=test

# Run full system test
python schedule_screener.py --action=test
```

### Step 4: Choose Scheduling Method

#### Option A: OpenClaw Cron (Recommended for OpenClaw Users)

```bash
# Create OpenClaw cron configuration
python schedule_screener.py --action=openclaw

# Then in OpenClaw:
openclaw cron add --file config/openclaw_cron_job.json
openclaw cron enable daily-stock-screener
```

#### Option B: Linux Systemd

```bash
# Create systemd service files
python schedule_screener.py --action=systemd

# Install and enable
sudo cp config/daily-stock-screener.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now daily-stock-screener.timer
```

#### Option C: Windows Task Scheduler

```powershell
# Create task configuration
python schedule_screener.py --action=windows

# Install (Run as Administrator in PowerShell)
.\config\register-windows-task.ps1
```

## Usage

### Manual Screening

```bash
# Run combined screener
python combined_screener.py

# Output: Top 20 oversold stocks with Buffett analysis
```

### Telegram Bot Commands

Start a chat with your bot and use:

- `/start` - Welcome message
- `/screen` - Run screener now
- `/last` - Show last results
- `/help` - Help information

### Web UI (Existing)

The original web interface still works:
1. Start backend: `cd backend/api && python app.py`
2. Start frontend: `cd frontend && npm start`
3. Visit: `http://localhost:3000`

## Data Flow

1. **Price Data**: Yahoo Finance → SQLite cache (1-day TTL)
2. **Fundamental Data**: SEC EDGAR API → SQLite cache (7-day TTL)
3. **Technical Analysis**: Calculate indicators from price data
4. **Fundamental Analysis**: Apply Buffett formulas to SEC data
5. **Combined Scoring**: 30% technical + 70% fundamental
6. **Filtering**: Keep stocks with Buffett score ≥ 5/10
7. **Ranking**: Sort by combined score
8. **Delivery**: Send top 10 via Telegram

## Sample Output

```
📊 Combined Stock Screener Report
_2026-02-12 20:00:00_
Found 8 quality oversold stocks

🟢 AAPL - $182.63
  Buffett: 7/10 | Combined: 85/100
  Williams %R: -92.3 | RSI: 28.5

🟢 MSFT - $415.86
  Buffett: 8/10 | Combined: 82/100
  Williams %R: -88.7 | RSI: 31.2

🟡 GOOGL - $152.34
  Buffett: 6/10 | Combined: 75/100
  Williams %R: -85.1 | RSI: 29.8
```

## Configuration

### Key Parameters (in `combined_screener.py`)

```python
# Technical threshold (Williams %R)
technical_threshold = -80.0  # More negative = more oversold

# Minimum Buffett score
min_buffett_score = 5  # Require 5/10 formulas to pass

# Scoring weights
technical_weight = 0.3  # 30%
fundamental_weight = 0.7  # 70%

# Number of stocks to return
top_n = 10
```

### Telegram Configuration (`config/telegram_config.json`)

```json
{
  "token": "YOUR_BOT_TOKEN",
  "chat_id": "YOUR_CHAT_ID",
  "updated_at": "2026-02-12T20:00:00"
}
```

## Monitoring & Logging

- **Logs**: `backend/logs/backend.log` and `backend/logs/refresh_job_state.json`
- **Results**: `backend/data/results/combined_screener_YYYYMMDD_HHMMSS.json`
- **Cache**: `backend/data/sec_cache.db` and `backend/data/stocks.db`

Check status:
```bash
# Check refresh job status
curl http://localhost:5001/api/refresh-status

# View latest results
ls -la backend/data/results/
```

## Troubleshooting

### Common Issues

1. **SEC API rate limits**: Caching handles this automatically
2. **Missing CIK for ticker**: System has fallback mapping for major stocks
3. **Telegram sending fails**: Check token and chat ID configuration
4. **No stocks found**: Adjust `technical_threshold` or `min_buffett_score`

### Debug Mode

```bash
# Enable debug logging
export LOGLEVEL=DEBUG
python combined_screener.py

# Test SEC API directly
python -c "from sec_api import SECAPIClient; c = SECAPIClient(); print(c.fetch_company_facts('AAPL'))"
```

## Performance

- **Initial run**: 3-5 minutes (fetching all data)
- **Cached run**: 15-30 seconds
- **SEC data cache**: 7 days TTL
- **Price data cache**: 1 day TTL
- **Memory usage**: ~500MB (SEC cache) + ~10MB (price cache)

## Security Considerations

1. **Telegram token**: Keep in config file, not in code
2. **SEC API**: Uses public data, no authentication needed
3. **Local storage**: All data stored locally in SQLite
4. **Network access**: Only outbound to Yahoo Finance and SEC APIs

## Future Enhancements

Planned features:
- Portfolio tracking and alerts
- Backtesting of screening strategy
- More technical indicators (MACD, Bollinger Bands)
- International market support
- Custom formula definitions
- Email/SMS alerts as alternative to Telegram

## Support

For issues or questions:
1. Check logs: `backend/logs/backend.log`
2. Test components individually
3. Adjust configuration parameters
4. Contact: florinel.chis@gmail.com

## License

MIT License - See LICENSE file for details.

---

**Automated Delivery**: Set up once, receive top oversold stocks daily at 8:00 PM PST via Telegram.

**Quality Focus**: Combines technical timing with Buffett's quality criteria.

**Zero Cost**: Uses 100% free data sources (Yahoo Finance + SEC EDGAR).