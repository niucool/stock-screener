#!/usr/bin/env python
"""
SEC EDGAR API Client for Fundamental Data
Fetches company financial statements for Buffett formula calculations.
"""

import requests
import json
import sqlite3
import time
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class SECAPIClient:
    """Client for SEC EDGAR API with caching and rate limiting."""
    
    def __init__(self, cache_db='../data/sec_cache.db', cache_ttl_days=7):
        self.base_url = "https://data.sec.gov/api/xbrl"
        self.headers = {
            'User-Agent': 'StockScreener/1.0 (florinel.chis@gmail.com)',
            'Accept': 'application/json'
        }
        self.cache_db = cache_db
        self.cache_ttl_days = cache_ttl_days
        self._init_cache_db()
        
        # Ticker to CIK mapping (S&P 500 companies)
        self.ticker_to_cik = self._load_ticker_cik_mapping()
    
    def _init_cache_db(self):
        """Initialize SQLite cache database."""
        os.makedirs(os.path.dirname(self.cache_db), exist_ok=True)
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        # Create cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sec_data (
                cik TEXT NOT NULL,
                data_type TEXT NOT NULL,
                fetched_at TIMESTAMP NOT NULL,
                data_json TEXT NOT NULL,
                PRIMARY KEY (cik, data_type)
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cik_type ON sec_data (cik, data_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fetched_at ON sec_data (fetched_at)')
        
        conn.commit()
        conn.close()
    
    def _load_ticker_cik_mapping(self):
        """Load ticker to CIK mapping from SEC or local file."""
        mapping_file = '../data/ticker_cik_mapping.json'
        
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                return json.load(f)
        
        # If no mapping file, create a basic one (we'll enhance this)
        # For now, return empty dict - we'll fetch mapping dynamically
        return {}
    
    def _get_cached_data(self, cik, data_type):
        """Get cached data if not expired."""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(days=self.cache_ttl_days)
        
        cursor.execute('''
            SELECT data_json FROM sec_data 
            WHERE cik = ? AND data_type = ? AND fetched_at > ?
        ''', (cik, data_type, cutoff.isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
    
    def _cache_data(self, cik, data_type, data):
        """Cache data with timestamp."""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sec_data (cik, data_type, fetched_at, data_json)
            VALUES (?, ?, ?, ?)
        ''', (cik, data_type, datetime.now().isoformat(), json.dumps(data)))
        
        conn.commit()
        conn.close()
    
    def resolve_ticker_to_cik(self, ticker):
        """Resolve stock ticker to SEC CIK number."""
        # First check our mapping
        if ticker in self.ticker_to_cik:
            return self.ticker_to_cik[ticker]
        
        # Try to fetch from SEC API
        try:
            # SEC provides a company tickers endpoint
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # The SEC API returns a dict with numeric keys
                for key, company in data.items():
                    if company.get('ticker') == ticker.upper():
                        cik = str(company['cik_str']).zfill(10)  # Pad to 10 digits
                        self.ticker_to_cik[ticker] = cik
                        
                        # Save updated mapping
                        mapping_file = '../data/ticker_cik_mapping.json'
                        with open(mapping_file, 'w') as f:
                            json.dump(self.ticker_to_cik, f, indent=2)
                        
                        return cik
        except Exception as e:
            logging.warning(f"Failed to resolve CIK for {ticker}: {e}")
        
        # Fallback: known CIKs for major companies
        known_ciks = {
            'AAPL': '0000320193',
            'MSFT': '0000789019',
            'GOOGL': '0001652044',
            'AMZN': '0001018724',
            'META': '0001326801',
            'TSLA': '0001318605',
            'NVDA': '0001045810',
            'JPM': '0000019617',
            'JNJ': '0000200406',
            'V': '0001403161',
            'PG': '0000080424',
            'UNH': '0000731766',
            'HD': '0000354950',
            'MA': '0001141391',
            'CVX': '0000093410',
            'LLY': '0000059478',
            'AVGO': '0001730168',
            'XOM': '0000034088',
            'MRK': '0000310158',
            'ABBV': '0001551152'
        }
        
        if ticker in known_ciks:
            return known_ciks[ticker]
        
        return None
    
    def fetch_company_facts(self, ticker):
        """Fetch company facts (balance sheet, income statement, cash flow)."""
        cik = self.resolve_ticker_to_cik(ticker)
        if not cik:
            logging.error(f"Could not resolve CIK for ticker: {ticker}")
            return None
        
        # Check cache first
        cached = self._get_cached_data(cik, 'companyfacts')
        if cached:
            logging.info(f"Using cached SEC data for {ticker} (CIK: {cik})")
            return cached
        
        # Fetch from SEC API
        try:
            url = f"{self.base_url}/companyfacts/CIK{cik}.json"
            logging.info(f"Fetching SEC data for {ticker} from {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the result
            self._cache_data(cik, 'companyfacts', data)
            
            logging.info(f"Successfully fetched SEC data for {ticker}")
            return data
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching SEC data for {ticker}: {e}")
            return None
    
    def fetch_submissions(self, ticker):
        """Fetch company submissions (10-K, 10-Q filings)."""
        cik = self.resolve_ticker_to_cik(ticker)
        if not cik:
            return None
        
        # Check cache
        cached = self._get_cached_data(cik, 'submissions')
        if cached:
            return cached
        
        # Fetch from SEC API
        try:
            url = f"{self.base_url}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self._cache_data(cik, 'submissions', data)
            return data
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching submissions for {ticker}: {e}")
            return None
    
    def extract_financial_facts(self, companyfacts):
        """Extract key financial facts from companyfacts data."""
        if not companyfacts or 'facts' not in companyfacts:
            return None
        
        facts = companyfacts['facts']
        us_gaap = facts.get('us-gaap', {})
        dei = facts.get('dei', {})
        
        extracted = {
            'ticker': str(companyfacts.get('cik', '')).lstrip('0'),
            'entityName': companyfacts.get('entityName', ''),
            'facts': {}
        }
        
        # Helper to get latest value
        def get_latest_value(fact_data):
            if not fact_data or 'units' not in fact_data:
                return None
            
            # Get USD values first, then any other currency
            units = fact_data['units']
            if 'USD' in units:
                usd_data = units['USD']
            elif 'USD/shares' in units:
                usd_data = units['USD/shares']
            else:
                # Get first available unit
                for unit_name, unit_data in units.items():
                    usd_data = unit_data
                    break
                else:
                    return None
            
            # Get most recent value
            if not usd_data:
                return None
            
            # Sort by end date, get latest
            sorted_data = sorted(
                usd_data,
                key=lambda x: (x.get('end', ''), x.get('filed', '')),
                reverse=True
            )
            
            if sorted_data:
                return sorted_data[0].get('val')
            return None
        
        # Key financial metrics for Buffett formulas
        key_metrics = {
            # Balance Sheet
            'Assets': 'Assets',
            'CurrentAssets': 'AssetsCurrent',
            'Liabilities': 'Liabilities',
            'CurrentLiabilities': 'LiabilitiesCurrent',
            'LongTermDebt': 'LongTermDebt',
            'TotalDebt': 'Debt',
            'Equity': 'StockholdersEquity',
            'CashAndEquivalents': 'CashAndCashEquivalentsAtCarryingValue',
            'ShortTermInvestments': 'ShortTermInvestments',
            
            # Income Statement
            'Revenue': 'RevenueFromContractWithCustomerExcludingAssessedTax',
            'OperatingIncome': 'OperatingIncomeLoss',
            'NetIncome': 'NetIncomeLoss',
            'InterestExpense': 'InterestExpense',
            
            # Cash Flow
            'OperatingCashFlow': 'NetCashProvidedByUsedInOperatingActivities',
            'FreeCashFlow': 'FreeCashFlow',
            'CapitalExpenditures': 'PaymentsToAcquirePropertyPlantAndEquipment',
            
            # Shares
            'SharesOutstanding': 'CommonStockSharesOutstanding'
        }
        
        for display_name, fact_name in key_metrics.items():
            if fact_name in us_gaap:
                value = get_latest_value(us_gaap[fact_name])
                if value is not None:
                    extracted['facts'][display_name] = value
        
        # Get Entity Common Stock from DEI
        if 'EntityCommonStockSharesOutstanding' in dei:
            value = get_latest_value(dei['EntityCommonStockSharesOutstanding'])
            if value is not None:
                extracted['facts']['SharesOutstanding'] = value
        
        return extracted
    
    def cleanup_old_cache(self):
        """Remove cache entries older than TTL."""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(days=self.cache_ttl_days)
        
        cursor.execute('DELETE FROM sec_data WHERE fetched_at < ?', (cutoff.isoformat(),))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logging.info(f"Cleaned up {deleted} old cache entries")
        return deleted


def test_sec_api():
    """Test the SEC API client."""
    client = SECAPIClient()
    
    # Test with Apple
    ticker = 'AAPL'
    print(f"Testing SEC API for {ticker}...")
    
    # Resolve CIK
    cik = client.resolve_ticker_to_cik(ticker)
    print(f"CIK for {ticker}: {cik}")
    
    # Fetch company facts
    facts = client.fetch_company_facts(ticker)
    if facts:
        print(f"Successfully fetched company facts for {ticker}")
        
        # Extract financial facts
        extracted = client.extract_financial_facts(facts)
        if extracted:
            print(f"\nExtracted financial facts for {ticker}:")
            for key, value in extracted['facts'].items():
                print(f"  {key}: {value}")
    
    # Cleanup old cache
    deleted = client.cleanup_old_cache()
    print(f"\nCleaned up {deleted} old cache entries")


if __name__ == "__main__":
    test_sec_api()