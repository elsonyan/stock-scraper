# API Reference

## 新浪财经 API

### Base URL
```
https://hq.sinajs.cn/list={symbols}
```

### Symbol Format

**A股**:
- Shanghai: `sh{6位代码}` (e.g., `sh600000`)
- Shenzhen: `sz{6位代码}` (e.g., `sz000001`)

**港股通**:
- `rt_hk{5位代码}` (e.g., `rt_hk00700`)

### Batch Query
```
https://hq.sinajs.cn/list=sh600000,sh600036,sz000001,rt_hk00700
```

### Response Format

**A股**:
```javascript
var hq_str_sh600000="浦发银行,10.00,10.05,10.10,10.15,9.95,10.09,10.10,12345678,123456789.00,100,10.09,200,10.08,300,10.07,400,10.06,500,10.05,100,10.10,200,10.11,300,10.12,400,10.13,500,10.14,2023-01-01,15:00:00,00,";
```

Fields (0-31):
| Index | Field | Description |
|-------|-------|-------------|
| 0 | name | Stock name |
| 1 | open | Opening price |
| 2 | pre_close | Previous close |
| 3 | price | Current price |
| 4 | high | Day high |
| 5 | low | Day low |
| 8 | volume | Volume |
| 9 | amount | Turnover |
| 30 | date | Date |
| 31 | time | Time |

**港股通**:
```javascript
var hq_str_rt_hk00700="TENCENT,腾讯控股,414.000,414.800,439.800,412.600,428.800,14.000,3.375,428.800,429.000,428.400,428.600,428.800,429.000,429.200,429.400,429.600,429.800,430.000,2023/01/01,15:00:00,00,";
```

Fields:
| Index | Field | Description |
|-------|-------|-------------|
| 0 | name_en | English name |
| 1 | name_cn | Chinese name |
| 2 | open | Opening price |
| 3 | high | Day high |
| 4 | low | Day low |
| 5 | prev_close | Previous close |
| 6 | price | Current price |
| 7 | change | Price change |
| 8 | change_pct | Change percentage |
| 12 | volume | Volume |
| 30 | date | Date |
| 31 | time | Time |

### Limits
- Max symbols per request: 800 (URL length ~8KB)
- Recommended: 500 symbols per request
- Rate limit: No official limit, but be reasonable

## 东方财富 API

### List API
```
https://push2.eastmoney.com/api/qt/clist/get
```

### Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| pn | 1 | Page number |
| pz | 5000 | Page size (max 5000) |
| po | 1 | Sort order (1=desc) |
| np | 1 | ? |
| ut | bd1d9ddb04089700cf9c27f6f7426281 | Token |
| fltt | 2 | ? |
| invt | 2 | ? |
| fid | f3 | Sort field |
| fs | - | Market filter |
| fields | f2,f3,f4,f12,f14 | Return fields |

### Market Filter (fs)

**A股**:
```
m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23
```

**港股通**:
```
m:128+t:3,m:128+t:4,m:128+t:1,m:128+t:2
```

### Response Fields

| Field | Description |
|-------|-------------|
| f2 | Current price |
| f3 | Change percentage |
| f4 | Price change |
| f12 | Stock code |
| f14 | Stock name |

### Limits
- Max page size: 5000
- Rate limit: Unknown, but connection may drop for large requests

## Usage Examples

### Basic Query
```python
import requests

url = "https://hq.sinajs.cn/list=sh600000,sh600036"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://finance.sina.com.cn/"
}

response = requests.get(url, headers=headers)
print(response.text)
```

### Batch Query with Processing
```python
import requests
from concurrent.futures import ThreadPoolExecutor

def fetch_batch(symbols):
    url = f"https://hq.sinajs.cn/list={','.join(symbols)}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.sina.com.cn/"
    }
    response = requests.get(url, headers=headers, timeout=10)
    return response.text

# Split into batches of 500
all_symbols = [f'sh{i:06d}' for i in range(1, 5001)]
batches = [all_symbols[i:i+500] for i in range(0, len(all_symbols), 500)]

# Fetch concurrently
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_batch, batch) for batch in batches]
    results = [f.result() for f in futures]
```

### Error Handling
```python
import requests
from requests.exceptions import RequestException

def safe_fetch(url, headers, timeout=10):
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        print(f"Error: {e}")
        return None
```
