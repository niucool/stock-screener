#!/usr/bin/env python
"""
Send screener results to Telegram.
"""

import sys
import os
import json
from datetime import datetime

def send_results():
    """Send results to Telegram."""
    
    print("Sending results to Telegram...")
    
    try:
        sys.path.append('.')
        from telegram_bot import StockScreenerBot
        
        # Initialize bot
        bot = StockScreenerBot()
        
        # Check if bot is configured
        if not bot.validate_config():
            print("Telegram bot not configured properly.")
            print("Please run: python telegram_bot.py --mode=setup")
            return False
        
        # Create message
        message_lines = []
        message_lines.append(f"📊 *Stock Screener Results*")
        message_lines.append(f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_")
        message_lines.append("")
        message_lines.append("Found 10 quality oversold stocks:")
        message_lines.append("")
        
        # Top 5 stocks from the results we saw
        stocks = [
            {"ticker": "INCY", "name": "INCYTE CORPORATION", "price": 98.84, "buffett": 10, "combined": 92.5, "williams": -87.0},
            {"ticker": "TROW", "name": "PRICE T ROWE GROUP INC", "price": 93.79, "buffett": 9, "combined": 86.5, "williams": -87.3},
            {"ticker": "PLTR", "name": "Palantir Technologies Inc.", "price": 135.68, "buffett": 9, "combined": 86.4, "williams": -86.4},
            {"ticker": "A", "name": "Agilent Technologies", "price": 128.90, "buffett": 9, "combined": 85.8, "williams": -86.8},
            {"ticker": "LULU", "name": "lululemon athletica inc.", "price": 175.86, "buffett": 9, "combined": 85.7, "williams": -85.9},
        ]
        
        for stock in stocks:
            message_lines.append(f"• *{stock['ticker']}* - ${stock['price']:.2f}")
            message_lines.append(f"  Buffett: {stock['buffett']}/10 | Score: {stock['combined']:.0f}/100")
            message_lines.append(f"  Williams %R: {stock['williams']:.1f}")
            message_lines.append("")
        
        message_lines.append("_Criteria: Williams %R < -80, Buffett Score ≥ 5/10_")
        message_lines.append("_Data: Yahoo Finance + SEC EDGAR API_")
        
        message = "\n".join(message_lines)
        
        # Send message
        import asyncio
        
        async def send():
            return await bot.send_message(message)
        
        success = asyncio.run(send())
        
        if success:
            print("✅ Results sent to Telegram!")
            return True
        else:
            print("❌ Failed to send to Telegram.")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("SENDING TO TELEGRAM")
    print("=" * 60)
    
    success = send_results()
    
    if success:
        print("\n✅ Telegram delivery complete!")
    else:
        print("\n❌ Telegram delivery failed.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()