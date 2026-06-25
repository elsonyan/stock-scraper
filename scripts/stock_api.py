#!/usr/bin/env python3
"""
Stock Scraper - A股 and 港股通 data fetching
Optimized for batch queries with 新浪财经 API
"""

import requests
import time
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional


class StockScraper:
    """Stock data scraper for A股 and 港股通 markets"""
    
    def __init__(self, data_dir: str = None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn/'
        }
        self.batch_size = 500
        self.max_workers = 10
        
        # Set data directory - default to project root's data/ folder
        if data_dir is None:
            # Find project root (parent of stock-scraper)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            skill_dir = os.path.dirname(current_dir)
            project_root = os.path.dirname(skill_dir)
            self.data_dir = os.path.join(project_root, 'data')
        else:
            self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # History file paths (markdown format)
        self.a_history_file = os.path.join(self.data_dir, 'a_history.md')
        self.hk_history_file = os.path.join(self.data_dir, 'hk_history.md')
    
    def _parse_sina_response(self, text: str) -> Dict[str, Dict]:
        """Parse 新浪财经 response format"""
        result = {}
        for line in text.strip().split('\n'):
            if not line.strip() or 'var hq_str_' not in line:
                continue
            
            try:
                symbol = line.split('var hq_str_')[1].split('=')[0]
                data_str = line.split('"')[1]
                if not data_str:
                    continue
                
                fields = data_str.split(',')
                
                # Parse based on symbol type
                if symbol.startswith('hk'):
                    # 港股 format
                    if len(fields) < 10:
                        continue
                    result[symbol] = {
                        'name': fields[0],
                        'price': float(fields[6]) if fields[6] else 0,
                        'change': float(fields[7]) if fields[7] else 0,
                        'change_pct': float(fields[8]) if fields[8] else 0,
                        'open': float(fields[2]) if fields[2] else 0,
                        'high': float(fields[3]) if fields[3] else 0,
                        'low': float(fields[4]) if fields[4] else 0,
                        'prev_close': float(fields[5]) if fields[5] else 0,
                        'time': f"{fields[17]} {fields[18]}" if len(fields) > 18 else '',
                        'market': 'HK'
                    }
                else:
                    # A股 format
                    if len(fields) < 32:
                        continue
                    result[symbol] = {
                        'name': fields[0],
                        'open': float(fields[1]) if fields[1] else 0,
                        'pre_close': float(fields[2]) if fields[2] else 0,
                        'price': float(fields[3]) if fields[3] else 0,
                        'high': float(fields[4]) if fields[4] else 0,
                        'low': float(fields[5]) if fields[5] else 0,
                        'volume': int(fields[8]) if fields[8] else 0,
                        'amount': float(fields[9]) if fields[9] else 0,
                        'time': f"{fields[30]} {fields[31]}" if len(fields) > 31 else '',
                        'market': 'A'
                    }
            except (IndexError, ValueError) as e:
                continue
        
        return result
    
    def _fetch_batch(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch a batch of stock quotes"""
        url = f"https://hq.sinajs.cn/list={','.join(symbols)}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return self._parse_sina_response(response.text)
        except Exception as e:
            print(f"Error fetching batch: {e}")
        return {}
    
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get real-time quotes for specified stocks
        
        Args:
            symbols: List of stock symbols (e.g., ['sh600000', 'hk00700'])
        
        Returns:
            Dict of stock quotes
        """
        result = {}
        batches = [symbols[i:i+self.batch_size] for i in range(0, len(symbols), self.batch_size)]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._fetch_batch, batch): batch for batch in batches}
            for future in as_completed(futures):
                result.update(future.result())
        
        return result
    
    def get_a_stocks(self) -> Dict[str, Dict]:
        """
        Get all A股 stocks
        
        Returns:
            Dict of all A股 stock quotes
        """
        symbols = []
        
        # Shanghai stocks (600xxx, 601xxx, 603xxx, 688xxx)
        for prefix in ['600', '601', '603', '688']:
            for i in range(1000):
                symbols.append(f'sh{prefix}{i:03d}')
        
        # Shenzhen stocks (000xxx, 001xxx, 002xxx, 300xxx)
        for prefix in ['000', '001', '002', '300']:
            for i in range(1000):
                symbols.append(f'sz{prefix}{i:03d}')
        
        return self.get_quotes(symbols)
    
    def get_hk_stocks(self, codes: List[str] = None) -> Dict[str, Dict]:
        """
        Get 港股通 stocks
        
        Args:
            codes: List of HK stock codes (e.g., ['00700', '0941'])
                   If None, uses default major stocks
        
        Returns:
            Dict of 港股通 stock quotes
        """
        if codes is None:
            # Major 港股通 stocks
            codes = [
                '00700', '0941', '1299', '1398', '2318', '2628', '3690', '9988', '9999', '1024',
                '2382', '1810', '2020', '9618', '9888', '1038', '2331', '1928', '6098', '2601',
                '1211', '9961', '6862', '1929', '2388', '9633', '3988', '939', '1658', '6030',
                '1336', '6060', '1918', '2319', '9901', '1177', '2007', '6618', '1093', '1109',
                '6881', '2202', '1876', '9868', '2313', '1833', '00001', '00002', '00005', '00012'
            ]
        
        symbols = [f'hk{code}' for code in codes]
        return self.get_quotes(symbols)
    
    def get_market_overview(self) -> Dict:
        """
        Get market overview with key indices
        
        Returns:
            Dict with major index data
        """
        indices = [
            'sh000001',  # 上证指数
            'sz399001',  # 深证成指
            'sz399006',  # 创业板指
            'sh000300',  # 沪深300
            'sh000016',  # 上证50
            'sh000905',  # 中证500
        ]
        
        return self.get_quotes(indices)
    
    def _load_history(self, file_path: str) -> Dict[str, Dict]:
        """Load existing history from markdown table"""
        history = {}
        
        if not os.path.exists(file_path):
            return history
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Find header line (starts with |)
                header_idx = None
                for i, line in enumerate(lines):
                    if line.strip().startswith('|'):
                        header_idx = i
                        break
                
                if header_idx is None:
                    return history
                
                # Parse header
                header = [col.strip() for col in lines[header_idx].split('|')[1:-1]]
                
                # Skip separator line (|---|---|)
                data_start = header_idx + 2
                
                # Parse data rows
                for line in lines[data_start:]:
                    if not line.strip().startswith('|'):
                        continue
                    
                    values = [val.strip() for val in line.split('|')[1:-1]]
                    if len(values) < 2:
                        continue
                    
                    row = dict(zip(header, values))
                    stock_id = row.get('stock_id')
                    if stock_id:
                        history[stock_id] = row
        except Exception as e:
            print(f"Error loading history: {e}")
        
        return history
    
    def _save_history(self, history: Dict[str, Dict], file_path: str):
        """Save history to markdown table"""
        if not history:
            return
        
        # Get all date columns
        date_columns = set()
        for row in history.values():
            for key in row.keys():
                if key.startswith('p_'):
                    date_columns.add(key)
        
        # Sort date columns
        date_columns = sorted(date_columns)
        
        # Define columns
        columns = ['stock_name', 'stock_id'] + date_columns
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write('| ' + ' | '.join(columns) + ' |\n')
                
                # Write separator
                f.write('| ' + ' | '.join(['---'] * len(columns)) + ' |\n')
                
                # Write data rows
                for stock_id, row in sorted(history.items()):
                    values = []
                    for col in columns:
                        if col == 'stock_id':
                            values.append(stock_id)
                        else:
                            values.append(str(row.get(col, '')))
                    f.write('| ' + ' | '.join(values) + ' |\n')
            
            print(f"Saved {len(history)} stocks to {file_path}")
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def _cleanup_old_data(self, history: Dict[str, Dict], keep_days: int = 30) -> Dict[str, Dict]:
        """Remove data older than keep_days"""
        cutoff_date = (datetime.now() - timedelta(days=keep_days)).strftime('%Y%m%d')
        
        cleaned_history = {}
        for stock_id, row in history.items():
            cleaned_row = {
                'stock_name': row.get('stock_name', ''),
                'stock_id': stock_id
            }
            
            for key, value in row.items():
                if key.startswith('p_'):
                    date_str = key[2:]  # Remove 'p_' prefix
                    if date_str >= cutoff_date:
                        cleaned_row[key] = value
                else:
                    cleaned_row[key] = value
            
            cleaned_history[stock_id] = cleaned_row
        
        return cleaned_history
    
    def update_a_history(self, stocks: Dict[str, Dict]):
        """
        Update A股 history markdown table with new stock data
        
        Args:
            stocks: Dict of A股 stock quotes
        """
        today = datetime.now().strftime('%Y%m%d')
        price_key = f'p_{today}'
        
        # Load existing history
        history = self._load_history(self.a_history_file)
        
        # Update with new data (overwrite today's data if exists)
        for symbol, data in stocks.items():
            if not data or 'price' not in data:
                continue
            
            stock_id = symbol
            stock_name = data.get('name', '')
            
            if stock_id not in history:
                history[stock_id] = {
                    'stock_name': stock_name,
                    'stock_id': stock_id
                }
            
            # Update name if empty
            if not history[stock_id].get('stock_name'):
                history[stock_id]['stock_name'] = stock_name
            
            # Update price (overwrites existing value for today)
            history[stock_id][price_key] = data['price']
        
        # Cleanup old data (keep last 30 days)
        history = self._cleanup_old_data(history)
        
        # Save to file
        self._save_history(history, self.a_history_file)
    
    def update_hk_history(self, stocks: Dict[str, Dict]):
        """
        Update 港股通 history markdown table with new stock data
        
        Args:
            stocks: Dict of 港股通 stock quotes
        """
        today = datetime.now().strftime('%Y%m%d')
        price_key = f'p_{today}'
        
        # Load existing history
        history = self._load_history(self.hk_history_file)
        
        # Update with new data (overwrite today's data if exists)
        for symbol, data in stocks.items():
            if not data or 'price' not in data:
                continue
            
            stock_id = symbol
            stock_name = data.get('name', '')
            
            if stock_id not in history:
                history[stock_id] = {
                    'stock_name': stock_name,
                    'stock_id': stock_id
                }
            
            # Update name if empty
            if not history[stock_id].get('stock_name'):
                history[stock_id]['stock_name'] = stock_name
            
            # Update price (overwrites existing value for today)
            history[stock_id][price_key] = data['price']
        
        # Cleanup old data (keep last 30 days)
        history = self._cleanup_old_data(history)
        
        # Save to file
        self._save_history(history, self.hk_history_file)
    
    def update_history(self, stocks: Dict[str, Dict]):
        """
        Update history markdown tables with new stock data (auto-detect market type)
        
        Args:
            stocks: Dict of stock quotes
        """
        a_stocks = {}
        hk_stocks = {}
        
        for symbol, data in stocks.items():
            if symbol.startswith('hk'):
                hk_stocks[symbol] = data
            else:
                a_stocks[symbol] = data
        
        if a_stocks:
            self.update_a_history(a_stocks)
        
        if hk_stocks:
            self.update_hk_history(hk_stocks)
    
    def get_a_history(self, stock_id: str = None) -> List[Dict]:
        """
        Get A股 historical data
        
        Args:
            stock_id: Optional stock ID to filter. If None, returns all.
        
        Returns:
            List of historical data rows
        """
        history = self._load_history(self.a_history_file)
        
        if stock_id:
            if stock_id in history:
                return [history[stock_id]]
            return []
        
        return list(history.values())
    
    def get_hk_history(self, stock_id: str = None) -> List[Dict]:
        """
        Get 港股通 historical data
        
        Args:
            stock_id: Optional stock ID to filter. If None, returns all.
        
        Returns:
            List of historical data rows
        """
        history = self._load_history(self.hk_history_file)
        
        if stock_id:
            if stock_id in history:
                return [history[stock_id]]
            return []
        
        return list(history.values())
    
    def get_stock_history(self, stock_id: str) -> Dict:
        """
        Get historical data for a single stock (auto-detect market type)
        
        Args:
            stock_id: Stock ID (e.g., 'sh600000', 'sz000001', 'hk00700')
        
        Returns:
            Dict with stock info and price history, or empty dict if not found
        """
        # Auto-detect market type
        if stock_id.startswith('hk'):
            history = self._load_history(self.hk_history_file)
        else:
            history = self._load_history(self.a_history_file)
        
        if stock_id in history:
            return history[stock_id]
        
        return {}
    
    def search_stock(self, keyword: str) -> List[Dict]:
        """
        Search stocks by name or code (fuzzy match)
        
        Args:
            keyword: Search keyword (e.g., '茅台', '600519', '腾讯')
        
        Returns:
            List of matching stocks with history data
        """
        results = []
        keyword_lower = keyword.lower()
        
        # Search in A股 history
        a_history = self._load_history(self.a_history_file)
        for stock_id, data in a_history.items():
            name = data.get('stock_name', '').lower()
            if keyword_lower in name or keyword_lower in stock_id.lower():
                results.append(data)
        
        # Search in 港股通 history
        hk_history = self._load_history(self.hk_history_file)
        for stock_id, data in hk_history.items():
            name = data.get('stock_name', '').lower()
            if keyword_lower in name or keyword_lower in stock_id.lower():
                results.append(data)
        
        return results


def main():
    """Demo usage"""
    scraper = StockScraper()
    
    print("=" * 60)
    print("Stock Scraper Demo with History")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Get some A股 stocks
    print("\n1. Fetching A股 stocks...")
    a_quotes = scraper.get_quotes(['sh600000', 'sh600036', 'sz000001', 'sz000002'])
    print(f"   Got {len(a_quotes)} A股 stocks")
    
    # Get some 港股通 stocks
    print("\n2. Fetching 港股通 stocks...")
    hk_quotes = scraper.get_hk_stocks(['00700', '0941', '1299'])
    print(f"   Got {len(hk_quotes)} 港股通 stocks")
    
    # Update history
    print("\n3. Updating history...")
    scraper.update_history({**a_quotes, **hk_quotes})
    
    # Show A股 history
    print("\n4. A股 history:")
    a_history = scraper.get_a_history()
    for row in a_history[:3]:
        print(f"   {row.get('stock_name')}: {row.get('stock_id')}")
        for key, value in row.items():
            if key.startswith('p_'):
                print(f"     {key}: {value}")
    
    # Show 港股通 history
    print("\n5. 港股通 history:")
    hk_history = scraper.get_hk_history()
    for row in hk_history[:3]:
        print(f"   {row.get('stock_name')}: {row.get('stock_id')}")
        for key, value in row.items():
            if key.startswith('p_'):
                print(f"     {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
