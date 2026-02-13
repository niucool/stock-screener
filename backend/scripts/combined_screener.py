#!/usr/bin/env python
"""
Combined Stock Screener: Technical + Fundamental Analysis
Finds oversold stocks with strong fundamentals (Buffett formulas).
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime
import json
import os
from typing import List, Dict, Any, Optional

# Import our modules
from sec_api import SECAPIClient
from buffett_formulas import BuffettFormulaEngine, FormulaStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class CombinedScreener:
    """
    Screens stocks using:
    1. Technical analysis (oversold conditions)
    2. Fundamental analysis (Buffett's 10 formulas)
    3. Combined scoring (30% technical + 70% fundamental)
    """
    
    def __init__(self, 
                 price_db_path='../data/stocks.db',
                 sec_cache_db='../data/sec_cache.db',
                 min_buffett_score=5,
                 technical_threshold=-80.0):
        
        self.price_db_path = price_db_path
        self.sec_client = SECAPIClient(cache_db=sec_cache_db)
        self.min_buffett_score = min_buffett_score
        self.technical_threshold = technical_threshold
        
    def get_oversold_stocks(self) -> pd.DataFrame:
        """Get technically oversold stocks from database."""
        conn = sqlite3.connect(self.price_db_path)
        
        query = f"""
            SELECT
                symbol,
                close,
                williams_r_21,
                ema_13_williams_r,
                rsi_14,
                rsi_21,
                adx_14,
                price_vs_sma200_pct,
                pct_from_52w_high,
                pct_from_52w_low,
                bb_position,
                relative_volume,
                macd_hist,
                volume,
                hist_volatility_20,
                data_age_days
            FROM stock_indicators
            WHERE williams_r_21 < {self.technical_threshold}
            AND data_age_days <= 1  -- Only fresh data (today or yesterday)
            ORDER BY williams_r_21 ASC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        logging.info(f"Found {len(df)} technically oversold stocks (Williams %R < {self.technical_threshold})")
        return df
    
    def analyze_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Analyze fundamentals using Buffett formulas."""
        try:
            # Fetch SEC data
            companyfacts = self.sec_client.fetch_company_facts(ticker)
            if not companyfacts:
                return {
                    'success': False,
                    'error': f"Could not fetch SEC data for {ticker}",
                    'score': 0,
                    'results': []
                }
            
            # Extract financial facts
            financial_facts = self.sec_client.extract_financial_facts(companyfacts)
            if not financial_facts or 'facts' not in financial_facts:
                return {
                    'success': False,
                    'error': f"Could not extract financial facts for {ticker}",
                    'score': 0,
                    'results': []
                }
            
            # Evaluate Buffett formulas
            engine = BuffettFormulaEngine(financial_facts['facts'])
            results = engine.evaluate_all()
            
            # Calculate score
            pass_count = sum(1 for r in results if r.status == FormulaStatus.PASS)
            total_formulas = len(results)
            score = (pass_count / total_formulas) * 100 if total_formulas > 0 else 0
            
            # Convert results to dict
            results_dict = [r.to_dict() for r in results]
            
            return {
                'success': True,
                'ticker': ticker,
                'company_name': financial_facts.get('entityName', ticker),
                'score': score,
                'pass_count': pass_count,
                'total_formulas': total_formulas,
                'results': results_dict,
                'financial_facts': financial_facts['facts']
            }
            
        except Exception as e:
            logging.error(f"Error analyzing fundamentals for {ticker}: {e}")
            return {
                'success': False,
                'error': str(e),
                'score': 0,
                'results': []
            }
    
    def calculate_technical_score(self, row: pd.Series) -> float:
        """Calculate technical score (0-100) based on oversold intensity."""
        # Williams %R is between -100 and 0, with -100 being most oversold
        # Convert to 0-100 scale where 100 is most oversold
        williams_r = row['williams_r_21']
        
        # Normalize: (-100 to threshold) -> (100 to 0)
        # More negative = higher score
        if williams_r <= -100:
            tech_score = 100
        elif williams_r >= self.technical_threshold:
            tech_score = 0
        else:
            # Map range [-100, threshold] to [100, 0]
            tech_score = 100 * (-100 - williams_r) / (-100 - self.technical_threshold)
        
        # Adjust based on other indicators
        adjustments = 0
        
        # RSI confirmation (lower RSI = more oversold)
        rsi_14 = row['rsi_14']
        if rsi_14 < 30:
            adjustments += 10
        elif rsi_14 < 40:
            adjustments += 5
        
        # Distance from 52-week low (closer = more oversold)
        pct_from_low = row['pct_from_52w_low']
        if pct_from_low < 10:
            adjustments += 10
        elif pct_from_low < 20:
            adjustments += 5
        
        # Bollinger Band position (lower = more oversold)
        bb_pos = row['bb_position']
        if bb_pos < 10:
            adjustments += 10
        elif bb_pos < 20:
            adjustments += 5
        
        # Relative volume (high volume on down day = capitulation)
        rel_vol = row['relative_volume']
        if rel_vol > 1.5:
            adjustments += 5
        
        final_score = min(tech_score + adjustments, 100)
        return final_score
    
    def screen_stocks(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        Main screening function:
        1. Find technically oversold stocks
        2. Analyze fundamentals for each
        3. Filter by minimum Buffett score
        4. Rank by combined score
        """
        logging.info("Starting combined stock screening...")
        
        # Step 1: Get oversold stocks
        oversold_df = self.get_oversold_stocks()
        if oversold_df.empty:
            logging.warning("No oversold stocks found")
            return []
        
        logging.info(f"Analyzing fundamentals for {len(oversold_df)} oversold stocks...")
        
        screened_stocks = []
        
        for _, row in oversold_df.iterrows():
            ticker = row['symbol']
            
            # Step 2: Analyze fundamentals
            fundamental_result = self.analyze_fundamentals(ticker)
            
            if not fundamental_result['success']:
                logging.debug(f"Skipping {ticker}: {fundamental_result.get('error', 'Unknown error')}")
                continue
            
            # Step 3: Check minimum Buffett score
            pass_count = fundamental_result['pass_count']
            if pass_count < self.min_buffett_score:
                logging.debug(f"Skipping {ticker}: Buffett score {pass_count}/10 < minimum {self.min_buffett_score}")
                continue
            
            # Step 4: Calculate scores
            technical_score = self.calculate_technical_score(row)
            fundamental_score = fundamental_result['score']  # 0-100
            
            # Combined score: 30% technical + 70% fundamental
            combined_score = (technical_score * 0.3) + (fundamental_score * 0.7)
            
            # Prepare stock data
            stock_data = {
                'ticker': ticker,
                'company_name': fundamental_result.get('company_name', ticker),
                'close_price': float(row['close']),
                'technical_indicators': {
                    'williams_r_21': float(row['williams_r_21']),
                    'rsi_14': float(row['rsi_14']),
                    'rsi_21': float(row['rsi_21']),
                    'ema_williams_r': float(row['ema_13_williams_r']),
                    'adx_14': float(row['adx_14']),
                    'price_vs_sma200_pct': float(row['price_vs_sma200_pct']),
                    'pct_from_52w_high': float(row['pct_from_52w_high']),
                    'pct_from_52w_low': float(row['pct_from_52w_low']),
                    'bb_position': float(row['bb_position']),
                    'relative_volume': float(row['relative_volume']),
                    'macd_hist': float(row['macd_hist']),
                    'hist_volatility': float(row['hist_volatility_20'])
                },
                'fundamental_analysis': {
                    'buffett_score': pass_count,
                    'total_formulas': fundamental_result['total_formulas'],
                    'score_percentage': fundamental_score,
                    'formula_results': fundamental_result['results'],
                    'key_financials': fundamental_result.get('financial_facts', {})
                },
                'scores': {
                    'technical': technical_score,
                    'fundamental': fundamental_score,
                    'combined': combined_score
                },
                'data_freshness': {
                    'price_data_age_days': int(row['data_age_days']),
                    'analysis_timestamp': datetime.now().isoformat()
                }
            }
            
            screened_stocks.append(stock_data)
        
        # Step 5: Sort by combined score (descending)
        screened_stocks.sort(key=lambda x: x['scores']['combined'], reverse=True)
        
        # Step 6: Return top N
        top_stocks = screened_stocks[:top_n]
        
        logging.info(f"Screening complete. Found {len(top_stocks)} quality oversold stocks.")
        
        return top_stocks
    
    def generate_report(self, screened_stocks: List[Dict[str, Any]], 
                       output_format: str = 'text') -> str:
        """Generate human-readable report."""
        
        if not screened_stocks:
            return "No quality oversold stocks found."
        
        report_lines = []
        
        if output_format == 'text':
            report_lines.append("=" * 120)
            report_lines.append("COMBINED STOCK SCREENER REPORT - OVERSOLD WITH QUALITY FUNDAMENTALS")
            report_lines.append("=" * 120)
            report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            report_lines.append(f"Criteria: Williams %R < {self.technical_threshold}, Buffett Score ≥ {self.min_buffett_score}/10")
            report_lines.append(f"Found: {len(screened_stocks)} quality oversold stocks")
            report_lines.append("=" * 120)
            report_lines.append("")
            
            for i, stock in enumerate(screened_stocks, 1):
                report_lines.append(f"{i}. {stock['ticker']} - {stock['company_name']}")
                report_lines.append(f"   Price: ${stock['close_price']:.2f}")
                report_lines.append(f"   Scores: Technical {stock['scores']['technical']:.1f}/100 | "
                                  f"Fundamental {stock['scores']['fundamental']:.1f}/100 | "
                                  f"Combined {stock['scores']['combined']:.1f}/100")
                report_lines.append(f"   Buffett Score: {stock['fundamental_analysis']['buffett_score']}/10 formulas passed")
                
                # Technical highlights
                tech = stock['technical_indicators']
                report_lines.append(f"   Technical: Williams %R {tech['williams_r_21']:.1f} | "
                                  f"RSI {tech['rsi_14']:.1f} | "
                                  f"vs 200-day SMA: {tech['price_vs_sma200_pct']:.1f}%")
                
                # Fundamental highlights
                fund = stock['fundamental_analysis']
                key_facts = fund.get('key_financials', {})
                
                if 'Revenue' in key_facts:
                    revenue = key_facts['Revenue']
                    if revenue > 1_000_000_000:
                        revenue_str = f"${revenue/1_000_000_000:.1f}B"
                    elif revenue > 1_000_000:
                        revenue_str = f"${revenue/1_000_000:.1f}M"
                    else:
                        revenue_str = f"${revenue:,.0f}"
                    report_lines.append(f"   Revenue: {revenue_str}")
                
                if 'NetIncome' in key_facts:
                    net_income = key_facts['NetIncome']
                    if net_income > 0:
                        report_lines.append(f"   Net Income: ${net_income/1_000_000:.1f}M (positive)")
                    else:
                        report_lines.append(f"   Net Income: ${net_income/1_000_000:.1f}M (negative)")
                
                report_lines.append("")
        
        elif output_format == 'json':
            report = {
                'timestamp': datetime.now().isoformat(),
                'criteria': {
                    'technical_threshold': self.technical_threshold,
                    'min_buffett_score': self.min_buffett_score
                },
                'summary': {
                    'total_found': len(screened_stocks)
                },
                'stocks': screened_stocks
            }
            return json.dumps(report, indent=2)
        
        elif output_format == 'telegram':
            # Compact format for Telegram
            report_lines.append(f"📊 *Combined Stock Screener Report*")
            report_lines.append(f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_")
            report_lines.append(f"Found *{len(screened_stocks)}* quality oversold stocks")
            report_lines.append("")
            
            for i, stock in enumerate(screened_stocks[:10], 1):  # Top 10 for Telegram
                buffett_score = stock['fundamental_analysis']['buffett_score']
                combined_score = stock['scores']['combined']
                
                # Emoji based on score
                if combined_score > 80:
                    emoji = "🟢"
                elif combined_score > 60:
                    emoji = "🟡"
                else:
                    emoji = "🟠"
                
                report_lines.append(f"{emoji} *{stock['ticker']}* - ${stock['close_price']:.2f}")
                report_lines.append(f"  Buffett: {buffett_score}/10 | Combined: {combined_score:.0f}/100")
                report_lines.append(f"  Williams %R: {stock['technical_indicators']['williams_r_21']:.1f} | "
                                  f"RSI: {stock['technical_indicators']['rsi_14']:.1f}")
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def save_results(self, screened_stocks: List[Dict[str, Any]], 
                    output_dir: str = '../data/results'):
        """Save screening results to JSON file."""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"combined_screener_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'criteria': {
                'technical_threshold': self.technical_threshold,
                'min_buffett_score': self.min_buffett_score
            },
            'summary': {
                'total_stocks_screened': len(screened_stocks)
            },
            'stocks': screened_stocks
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logging.info(f"Results saved to {filepath}")
        return filepath


def run_screener():
    """Run the combined screener and print results."""
    screener = CombinedScreener(
        min_buffett_score=5,  # Minimum 5/10 Buffett formulas
        technical_threshold=-80.0  # Williams %R < -80
    )
    
    print("Running Combined Stock Screener...")
    print("=" * 80)
    
    # Screen stocks
    screened_stocks = screener.screen_stocks(top_n=20)
    
    # Generate report
    report = screener.generate_report(screened_stocks, output_format='text')
    print(report)
    
    # Save results
    if screened_stocks:
        saved_file = screener.save_results(screened_stocks)
        print(f"\nResults saved to: {saved_file}")
    
    return screened_stocks


if __name__ == "__main__":
    run_screener()