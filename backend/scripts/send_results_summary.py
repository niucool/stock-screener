#!/usr/bin/env python
"""
Create summary of screener results for OpenClaw message tool.
"""

import json
from datetime import datetime

def create_summary():
    """Create summary message."""
    
    # Results from the screener run
    results = [
        {
            "rank": 1,
            "ticker": "INCY",
            "name": "INCYTE CORPORATION",
            "price": 98.84,
            "buffett": 10,
            "combined": 92.5,
            "williams": -87.0,
            "rsi": 43.1,
            "vs_sma200": 16.1
        },
        {
            "rank": 2,
            "ticker": "TROW",
            "name": "PRICE T ROWE GROUP INC",
            "price": 93.79,
            "buffett": 9,
            "combined": 86.5,
            "williams": -87.3,
            "rsi": 34.5,
            "vs_sma200": -7.9
        },
        {
            "rank": 3,
            "ticker": "PLTR",
            "name": "Palantir Technologies Inc.",
            "price": 135.68,
            "buffett": 9,
            "combined": 86.4,
            "williams": -86.4,
            "rsi": 34.4,
            "vs_sma200": -15.5
        },
        {
            "rank": 4,
            "ticker": "A",
            "name": "Agilent Technologies",
            "price": 128.90,
            "buffett": 9,
            "combined": 85.8,
            "williams": -86.8,
            "rsi": 34.7,
            "vs_sma200": 0.1
        },
        {
            "rank": 5,
            "ticker": "LULU",
            "name": "lululemon athletica inc.",
            "price": 175.86,
            "buffett": 9,
            "combined": 85.7,
            "williams": -85.9,
            "rsi": 41.7,
            "vs_sma200": -16.6
        }
    ]
    
    # Create message
    message_lines = []
    message_lines.append("📊 *ENHANCED STOCK SCREENER RESULTS*")
    message_lines.append(f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    message_lines.append("")
    message_lines.append("✅ *Workflow Complete:*")
    message_lines.append("1. ✅ Market data updated (1 day fresh)")
    message_lines.append("2. ✅ Combined screening executed")
    message_lines.append("3. ✅ Top 10 oversold stocks found")
    message_lines.append("")
    message_lines.append("🔍 *Screening Criteria:*")
    message_lines.append("• Williams %R < -80 (oversold)")
    message_lines.append("• Buffett Score ≥ 5/10 (quality)")
    message_lines.append("• Combined: 30% technical + 70% fundamental")
    message_lines.append("")
    message_lines.append("🏆 *Top 5 Quality Oversold Stocks:*")
    
    for stock in results:
        message_lines.append("")
        message_lines.append(f"{stock['rank']}. *{stock['ticker']}* - ${stock['price']:.2f}")
        message_lines.append(f"   {stock['name'][:30]}")
        message_lines.append(f"   Buffett: {stock['buffett']}/10 | Score: {stock['combined']:.0f}/100")
        message_lines.append(f"   Williams %R: {stock['williams']:.1f} | RSI: {stock['rsi']:.1f}")
        message_lines.append(f"   vs 200-day SMA: {stock['vs_sma200']:+.1f}%")
    
    message_lines.append("")
    message_lines.append("📈 *Analysis:*")
    message_lines.append("• INCY: Perfect Buffett score (10/10) - exceptional quality")
    message_lines.append("• TROW: Strong fundamentals, technically oversold")
    message_lines.append("• PLTR: High-growth tech with quality metrics")
    message_lines.append("• A: Agilent - stable business, good value")
    message_lines.append("• LULU: Premium brand, Buffett-approved quality")
    message_lines.append("")
    message_lines.append("💡 *Next Steps:*")
    message_lines.append("• Review detailed analysis in saved JSON file")
    message_lines.append("• Set up automated daily screening")
    message_lines.append("• Monitor these stocks for potential entry points")
    message_lines.append("")
    message_lines.append("_System: Enhanced Stock Screener v1.0_")
    message_lines.append("_Data: Yahoo Finance + SEC EDGAR API_")
    
    return "\n".join(message_lines)

def main():
    """Main function."""
    summary = create_summary()
    print(summary)
    
    # Also save to file
    output_file = "../data/results/summary_message.txt"
    with open(output_file, 'w') as f:
        f.write(summary)
    
    print(f"\n📝 Summary saved to: {output_file}")
    print("\n📋 Copy the message above to send via OpenClaw message tool.")

if __name__ == "__main__":
    main()