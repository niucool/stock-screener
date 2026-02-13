#!/usr/bin/env python
"""
Run the combined screener and display results.
"""

import sys
import os
import json
from datetime import datetime

def run_screener():
    """Run the combined screener."""
    
    print("=" * 80)
    print("COMBINED STOCK SCREENER - RUNNING NOW")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Criteria: Williams %R < -80, Buffett Score ≥ 5/10")
    print("=" * 80)
    
    try:
        # Import screener
        sys.path.append('.')
        from combined_screener import CombinedScreener
        
        # Initialize
        screener = CombinedScreener(
            min_buffett_score=5,
            technical_threshold=-80.0
        )
        
        # Run screening
        print("\n🔍 Screening stocks...")
        screened_stocks = screener.screen_stocks(top_n=10)
        
        if not screened_stocks:
            print("\n❌ No quality oversold stocks found.")
            print("This could be because:")
            print("1. No stocks are oversold enough (Williams %R < -80)")
            print("2. Oversold stocks don't meet Buffett quality criteria (≥5/10)")
            print("3. SEC data unavailable for some stocks")
            return None
        
        print(f"\n✅ Found {len(screened_stocks)} quality oversold stocks!")
        print("\n" + "=" * 80)
        
        # Display results
        for i, stock in enumerate(screened_stocks, 1):
            print(f"\n{i}. {stock['ticker']} - {stock['company_name'][:40]}")
            print(f"   Price: ${stock['close_price']:.2f}")
            print(f"   Buffett Score: {stock['fundamental_analysis']['buffett_score']}/10")
            print(f"   Combined Score: {stock['scores']['combined']:.1f}/100")
            
            # Technical indicators
            tech = stock['technical_indicators']
            print(f"   Technical: Williams %R {tech['williams_r_21']:.1f}, RSI {tech['rsi_14']:.1f}")
            print(f"   vs 200-day SMA: {tech['price_vs_sma200_pct']:.1f}%")
            print(f"   Relative Volume: {tech['relative_volume']:.1f}x")
            
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
                print(f"   Revenue: {revenue_str}")
            
            if 'NetIncome' in key_facts:
                net_income = key_facts['NetIncome']
                if net_income > 0:
                    print(f"   Net Income: ${net_income/1_000_000:.1f}M (positive)")
                else:
                    print(f"   Net Income: ${net_income/1_000_000:.1f}M (negative)")
        
        # Generate Telegram message
        print("\n" + "=" * 80)
        print("📱 TELEGRAM MESSAGE FORMAT:")
        print("=" * 80)
        
        telegram_report = screener.generate_report(screened_stocks, output_format='telegram')
        print(telegram_report)
        
        # Save results
        results_file = screener.save_results(screened_stocks)
        print(f"\n💾 Results saved to: {results_file}")
        
        return screened_stocks
        
    except Exception as e:
        print(f"\n❌ Error running screener: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_to_telegram(stocks):
    """Send results to Telegram."""
    
    print("\n" + "=" * 80)
    print("🤖 SENDING TO TELEGRAM...")
    print("=" * 80)
    
    try:
        sys.path.append('.')
        from telegram_bot import StockScreenerBot
        
        # Initialize bot
        bot = StockScreenerBot()
        
        # Generate report
        from combined_screener import CombinedScreener
        screener = CombinedScreener()
        report = screener.generate_report(stocks, output_format='telegram')
        
        # Send message
        import asyncio
        
        async def send():
            success = await bot.send_message(report)
            return success
        
        success = asyncio.run(send())
        
        if success:
            print("✅ Message sent successfully to Telegram!")
        else:
            print("❌ Failed to send message to Telegram.")
            print("Check your Telegram configuration in config/telegram_config.json")
            
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    
    # Run screener
    stocks = run_screener()
    
    if stocks:
        # Ask if user wants to send to Telegram
        print("\n" + "=" * 80)
        response = input("Send results to Telegram? (y/n): ")
        
        if response.lower() == 'y':
            send_to_telegram(stocks)
        else:
            print("\nTelegram delivery skipped.")
    
    print("\n" + "=" * 80)
    print("SCREENING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()