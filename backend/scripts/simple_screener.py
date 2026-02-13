#!/usr/bin/env python
"""
Simple screener runner without Unicode characters.
"""

import sys
import os
import json
from datetime import datetime

def run_simple_screener():
    """Run screener and return results."""
    
    print("=" * 80)
    print("STOCK SCREENER - RUNNING")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Criteria: Williams %R < -80, Buffett Score >= 5/10")
    print("=" * 80)
    
    try:
        sys.path.append('.')
        from combined_screener import CombinedScreener
        
        screener = CombinedScreener(min_buffett_score=5, technical_threshold=-80.0)
        
        print("\nScreening stocks...")
        screened_stocks = screener.screen_stocks(top_n=10)
        
        if not screened_stocks:
            print("\nNo quality oversold stocks found.")
            return None
        
        print(f"\nFound {len(screened_stocks)} quality oversold stocks!")
        print("\n" + "=" * 80)
        
        # Simple display
        for i, stock in enumerate(screened_stocks, 1):
            print(f"\n{i}. {stock['ticker']} - {stock['company_name'][:30]}")
            print(f"   Price: ${stock['close_price']:.2f}")
            print(f"   Buffett: {stock['fundamental_analysis']['buffett_score']}/10")
            print(f"   Combined: {stock['scores']['combined']:.1f}/100")
            
            tech = stock['technical_indicators']
            print(f"   Williams %R: {tech['williams_r_21']:.1f}, RSI: {tech['rsi_14']:.1f}")
            print(f"   vs SMA200: {tech['price_vs_sma200_pct']:.1f}%")
        
        # Save results
        results_file = screener.save_results(screened_stocks)
        print(f"\nResults saved to: {results_file}")
        
        return screened_stocks
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_telegram_simple(stocks):
    """Send simple message to Telegram."""
    
    print("\n" + "=" * 80)
    print("SENDING TO TELEGRAM...")
    print("=" * 80)
    
    try:
        sys.path.append('.')
        from telegram_bot import StockScreenerBot
        
        bot = StockScreenerBot()
        
        # Create simple message
        message_lines = []
        message_lines.append(f"Stock Screener Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        message_lines.append(f"Found {len(stocks)} quality oversold stocks")
        message_lines.append("")
        
        for i, stock in enumerate(stocks[:5], 1):  # Send top 5
            buffett = stock['fundamental_analysis']['buffett_score']
            combined = stock['scores']['combined']
            williams = stock['technical_indicators']['williams_r_21']
            
            message_lines.append(f"{i}. {stock['ticker']} - ${stock['close_price']:.2f}")
            message_lines.append(f"   Buffett: {buffett}/10 | Score: {combined:.0f}/100")
            message_lines.append(f"   Williams %R: {williams:.1f}")
            message_lines.append("")
        
        message = "\n".join(message_lines)
        
        # Send
        import asyncio
        
        async def send():
            return await bot.send_message(message)
        
        success = asyncio.run(send())
        
        if success:
            print("Message sent to Telegram!")
        else:
            print("Failed to send to Telegram.")
            
    except Exception as e:
        print(f"Telegram error: {e}")

def main():
    """Main function."""
    
    stocks = run_simple_screener()
    
    if stocks:
        print("\n" + "=" * 80)
        response = input("Send to Telegram? (y/n): ")
        
        if response.lower() == 'y':
            send_telegram_simple(stocks)
    
    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)

if __name__ == "__main__":
    main()