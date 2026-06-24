#!/usr/bin/env python3
"""
Quick start example for Stock Scraper with History
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.stock_api import StockScraper


def main():
    scraper = StockScraper()
    
    print("=" * 60)
    print("Stock Scraper - A股 & 港股通 History Demo")
    print("=" * 60)
    
    # 1. Get A股 stocks
    print("\n1. Fetching A股 stocks...")
    a_symbols = [f'sh600{i:03d}' for i in range(100)]  # First 100 A股 stocks
    a_quotes = scraper.get_quotes(a_symbols)
    valid_a = {k: v for k, v in a_quotes.items() if v and v.get('price', 0) > 0}
    print(f"   Got {len(valid_a)} valid A股 stocks")
    
    # 2. Get 港股通 stocks
    print("\n2. Fetching 港股通 stocks...")
    hk_codes = [
        '00700', '0941', '1299', '1398', '2318', '2628', '3690', '9988', '9999', '1024',
        '2382', '1810', '2020', '9618', '9888', '1038', '2331', '1928', '6098', '2601',
        '1211', '9961', '6862', '1929', '2388', '9633', '3988', '939', '1658', '6030',
        '1336', '6060', '1918', '2319', '9901', '1177', '2007', '6618', '1093', '1109',
        '6881', '2202', '1876', '9868', '2313', '1833', '00001', '00002', '00005', '00012'
    ]
    hk_quotes = scraper.get_hk_stocks(hk_codes)
    valid_hk = {k: v for k, v in hk_quotes.items() if v and v.get('price', 0) > 0}
    print(f"   Got {len(valid_hk)} valid 港股通 stocks")
    
    # 3. Combine and update history
    print("\n3. Updating history...")
    all_quotes = {**valid_a, **valid_hk}
    scraper.update_history(all_quotes)
    
    # 4. Show sample data
    print("\n4. Sample from history.csv:")
    history = scraper.get_history()
    
    print("\n   A股 stocks:")
    for row in history:
        if row.get('stock_id', '').startswith(('sh', 'sz')):
            print(f"     {row.get('stock_name')}: {row.get('stock_id')} = {row.get('p_20260624', 'N/A')}")
            if history.index(row) >= 4:
                break
    
    print("\n   港股通 stocks:")
    count = 0
    for row in history:
        if row.get('stock_id', '').startswith('hk'):
            print(f"     {row.get('stock_name')}: {row.get('stock_id')} = {row.get('p_20260624', 'N/A')}")
            count += 1
            if count >= 5:
                break
    
    # 5. Show file info
    print("\n5. File info:")
    csv_path = scraper.history_file
    if os.path.exists(csv_path):
        size = os.path.getsize(csv_path)
        lines = sum(1 for _ in open(csv_path, 'r', encoding='utf-8'))
        print(f"   File: {csv_path}")
        print(f"   Size: {size:,} bytes")
        print(f"   Lines: {lines} (including header)")
        print(f"   Stocks: {lines - 1}")
    
    print("\n" + "=" * 60)
    print("Done! Both A股 and 港股通 are in history.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()
