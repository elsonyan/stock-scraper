---
name: stock-scraper
description: Scrape A股 and 港股通 stock data using batch APIs. Use when asked to query stock prices, get market data, fetch real-time quotes, or scrape financial data from Chinese/HK markets. Supports batch queries (500 stocks/request), concurrent requests, multiple data sources, and historical data storage.
---

# Stock Scraper

Scrape real-time stock data from A股 (China) and 港股通 (HK Stock Connect) markets using optimized batch APIs. Includes historical data storage with automatic cleanup.

## Quick Start

```python
from scripts.stock_api import StockScraper

scraper = StockScraper()

# Get real-time quotes
quotes = scraper.get_quotes(['sh600000', 'hk00700'])

# Update history
scraper.update_history(quotes)

# Get historical data
history = scraper.get_history()
```

## Features

### Real-time Data
- **A股**: Shanghai and Shenzhen stocks
- **港股通**: Hong Kong stocks via Stock Connect
- **Batch queries**: 500 stocks per request
- **Concurrent**: 10 parallel threads

### Historical Storage
- **Markdown format**: Separate files for A股 and 港股通 with table structure
- **Auto-cleanup**: Keeps last 30 days only
- **Fields**: `stock_name`, `stock_id`, `p_YYYYMMDD`

### Stock Search
- **Search by name**: Fuzzy match stock names (e.g., '茅台', '腾讯')
- **Search by code**: Match stock codes (e.g., '600519', '00700')
- **Auto-detect market**: Automatically finds stock in A股 or 港股通

## Data Sources

| Source | A股 | 港股通 | Batch Size | Speed |
|--------|-----|--------|------------|-------|
| 新浪财经 | ✅ | ✅ | 500/req | 0.07s |
| 腾讯财经 | ✅ | ✅ | 100/req | 0.1s |

**Primary**: 新浪财经 (most stable for both markets)

## API Reference

### Symbol Format

**A股**:
- Shanghai: `sh{6位代码}` (e.g., `sh600000`)
- Shenzhen: `sz{6位代码}` (e.g., `sz000001`)

**港股通**:
- `hk{5位代码}` (e.g., `hk00700`)

### Batch Query
```
https://hq.sinajs.cn/list=sh600000,sh600036,hk00700
```

## Implementation

See `scripts/stock_api.py` for complete implementation.

## Usage Examples

### Get Real-time Quotes

```python
scraper = StockScraper()

# A股
a_quotes = scraper.get_quotes(['sh600000', 'sh600036'])

# 港股通
hk_quotes = scraper.get_hk_stocks(['00700', '0941'])

# Combined
all_quotes = {**a_quotes, **hk_quotes}
```

### Update History

```python
# Fetch and save today's data
quotes = scraper.get_quotes(['sh600000', 'hk00700'])
scraper.update_history(quotes)

# History is saved to data/a_history.md and data/hk_history.md
# Old data (>30 days) is automatically removed
```

### Get Historical Data

```python
# Get single stock history (auto-detect A股/港股通)
stock = scraper.get_stock_history('sh600000')
print(f"{stock['stock_name']}: {stock}")

# Get all A股 history
a_history = scraper.get_a_history()

# Get all 港股通 history
hk_history = scraper.get_hk_history()

# Get specific stock from A股
stock = scraper.get_a_history('sh600000')
```

### Search Stocks by Name

```python
# Search by stock name or code
results = scraper.search_stock('茅台')
# Returns: [{'stock_name': '贵州茅台', 'stock_id': 'sh600519', ...}]

results = scraper.search_stock('腾讯')
# Returns: [{'stock_name': 'TENCENT', 'stock_id': 'hk00700', ...}]

results = scraper.search_stock('600036')
# Returns: [{'stock_name': '招商银行', 'stock_id': 'sh600036', ...}]
```

### Markdown Table Format

```
| stock_name | stock_id | p_20260624 | p_20260623 | ... |
| --- | --- | --- | --- | ... |
| TENCENT | hk00700 | 429.4 | 428.8 | ... |
| 浦发银行 | sh600000 | 8.9 | 8.85 | ... |
```

## Performance

- **A股 (5000 stocks)**: ~0.5s with 10 concurrent threads
- **港股通 (50 stocks)**: ~0.1s
- **History update**: <1s for 100 stocks
- **Auto-cleanup**: Runs on each update

## File Structure

```
stock-scraper/
├── SKILL.md
├── scripts/
│   └── stock_api.py
├── references/
│   └── api_docs.md
└── examples/
    └── quick_start.py

data/                     # Project root data directory
├── a_history.md          # A股 history (markdown table)
└── hk_history.md         # 港股通 history (markdown table)
```

## Guardrails

- Respect API rate limits (max 10 concurrent requests)
- History keeps last 30 days only
- Use proper User-Agent headers
- Handle connection errors gracefully
