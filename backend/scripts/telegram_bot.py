#!/usr/bin/env python
"""
Telegram Bot for Automated Stock Screener Delivery
Sends daily/weekly screening results via Telegram.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, time
import schedule
import time as time_module
from typing import Optional, Dict, Any
import sys

# Try to import telegram libraries
try:
    from telegram import Bot, Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    from telegram.constants import ParseMode
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("python-telegram-bot not installed. Install with: pip install python-telegram-bot")

# Import our screener
from combined_screener import CombinedScreener

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class StockScreenerBot:
    """Telegram bot for automated stock screener delivery."""
    
    def __init__(self, 
                 token: Optional[str] = None,
                 chat_id: Optional[str] = None,
                 config_file: str = '../config/telegram_config.json'):
        
        self.token = token
        self.chat_id = chat_id
        self.config_file = config_file
        self.bot: Optional[Bot] = None
        self.application: Optional[Application] = None
        
        # Load config if exists
        self.load_config()
        
        # Initialize screener
        self.screener = CombinedScreener(
            min_buffett_score=5,
            technical_threshold=-80.0
        )
        
        # Results cache
        self.last_results: Optional[Dict[str, Any]] = None
        self.last_run_time: Optional[datetime] = None
    
    def load_config(self):
        """Load Telegram configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                self.token = config.get('token', self.token)
                self.chat_id = config.get('chat_id', self.chat_id)
                
                logging.info(f"Loaded Telegram config from {self.config_file}")
                
            except Exception as e:
                logging.error(f"Error loading Telegram config: {e}")
        else:
            logging.warning(f"Telegram config file not found: {self.config_file}")
            logging.info("Create config file with: {'token': 'YOUR_BOT_TOKEN', 'chat_id': 'YOUR_CHAT_ID'}")
    
    def save_config(self):
        """Save Telegram configuration to file."""
        config = {
            'token': self.token,
            'chat_id': self.chat_id,
            'updated_at': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logging.info(f"Saved Telegram config to {self.config_file}")
    
    def validate_config(self) -> bool:
        """Validate that we have required configuration."""
        if not self.token:
            logging.error("Telegram bot token not configured")
            return False
        
        if not self.chat_id:
            logging.error("Telegram chat ID not configured")
            return False
        
        return True
    
    async def send_message(self, text: str, parse_mode: str = ParseMode.MARKDOWN) -> bool:
        """Send message to configured chat."""
        if not self.validate_config():
            return False
        
        try:
            if not self.bot:
                self.bot = Bot(token=self.token)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            
            logging.info(f"Message sent to chat {self.chat_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error sending Telegram message: {e}")
            return False
    
    async def send_daily_report(self):
        """Run screener and send daily report."""
        logging.info("Running daily stock screener report...")
        
        try:
            # Run screener
            screened_stocks = self.screener.screen_stocks(top_n=10)
            
            # Cache results
            self.last_results = {
                'timestamp': datetime.now().isoformat(),
                'stocks': screened_stocks
            }
            self.last_run_time = datetime.now()
            
            # Generate Telegram-formatted report
            report = self.screener.generate_report(screened_stocks, output_format='telegram')
            
            # Send report
            success = await self.send_message(report)
            
            if success:
                logging.info("Daily report sent successfully")
                
                # Save results to file
                if screened_stocks:
                    self.screener.save_results(screened_stocks)
                    
                    # Send summary stats
                    stats = self._generate_stats_message(screened_stocks)
                    await self.send_message(stats)
            else:
                logging.error("Failed to send daily report")
            
            return success
            
        except Exception as e:
            error_msg = f"Error generating daily report: {str(e)}"
            logging.error(error_msg)
            await self.send_message(f"❌ Error: {error_msg}")
            return False
    
    def _generate_stats_message(self, screened_stocks: list) -> str:
        """Generate statistics message."""
        if not screened_stocks:
            return "📊 *Statistics*: No quality oversold stocks found today."
        
        # Calculate averages
        tech_scores = [s['scores']['technical'] for s in screened_stocks]
        fund_scores = [s['scores']['fundamental'] for s in screened_stocks]
        comb_scores = [s['scores']['combined'] for s in screened_stocks]
        buffett_scores = [s['fundamental_analysis']['buffett_score'] for s in screened_stocks]
        
        stats = [
            "📊 *Screening Statistics*",
            f"• Stocks found: {len(screened_stocks)}",
            f"• Avg Buffett Score: {sum(buffett_scores)/len(buffett_scores):.1f}/10",
            f"• Avg Technical Score: {sum(tech_scores)/len(tech_scores):.1f}/100",
            f"• Avg Fundamental Score: {sum(fund_scores)/len(fund_scores):.1f}/100",
            f"• Avg Combined Score: {sum(comb_scores)/len(comb_scores):.1f}/100",
            "",
            "*Top 3 Stocks by Combined Score:*"
        ]
        
        for i, stock in enumerate(screened_stocks[:3], 1):
            stats.append(f"{i}. {stock['ticker']} - {stock['scores']['combined']:.1f}/100 "
                        f"({stock['fundamental_analysis']['buffett_score']}/10 Buffett)")
        
        return "\n".join(stats)
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        await update.message.reply_text(
            "🤖 *Stock Screener Bot*\n\n"
            "I automatically screen for oversold stocks with strong fundamentals.\n\n"
            "*Commands:*\n"
            "/start - Show this message\n"
            "/screen - Run screener now\n"
            "/last - Show last screening results\n"
            "/help - Show help\n\n"
            "Daily reports are sent at 8:00 PM PST.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_screen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /screen command - run screener manually."""
        await update.message.reply_text("🔄 Running stock screener...")
        
        success = await self.send_daily_report()
        
        if success:
            await update.message.reply_text("✅ Screening complete! Check your messages.")
        else:
            await update.message.reply_text("❌ Screening failed. Check logs for details.")
    
    async def handle_last(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /last command - show last results."""
        if not self.last_results:
            await update.message.reply_text("No screening results available yet.")
            return
        
        last_time = self.last_run_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_run_time else "Unknown"
        
        if self.last_results['stocks']:
            stocks = self.last_results['stocks'][:5]  # Show top 5
            message = [f"📅 *Last Screening Results* ({last_time})", ""]
            
            for i, stock in enumerate(stocks, 1):
                message.append(f"{i}. *{stock['ticker']}* - ${stock['close_price']:.2f}")
                message.append(f"   Buffett: {stock['fundamental_analysis']['buffett_score']}/10 | "
                             f"Combined: {stock['scores']['combined']:.1f}/100")
                message.append(f"   Williams %R: {stock['technical_indicators']['williams_r_21']:.1f}")
                message.append("")
            
            await update.message.reply_text("\n".join(message), parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"📅 Last screening ({last_time}): No quality stocks found.")
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        await update.message.reply_text(
            "🤖 *Stock Screener Bot Help*\n\n"
            "*How it works:*\n"
            "1. Scans S&P 500 for oversold stocks (Williams %R < -80)\n"
            "2. Analyzes fundamentals using Warren Buffett's 10 formulas\n"
            "3. Combines technical (30%) and fundamental (70%) scores\n"
            "4. Sends top 10 stocks daily at 8:00 PM PST\n\n"
            "*Data Sources:*\n"
            "• Price data: Yahoo Finance (via yfinance)\n"
            "• Fundamental data: SEC EDGAR API (official filings)\n\n"
            "*Commands:*\n"
            "/screen - Run screener now\n"
            "/last - Show last results\n"
            "/help - This message\n\n"
            "For issues, check the application logs.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    def setup_handlers(self, application: Application):
        """Setup command handlers."""
        application.add_handler(CommandHandler("start", self.handle_start))
        application.add_handler(CommandHandler("screen", self.handle_screen))
        application.add_handler(CommandHandler("last", self.handle_last))
        application.add_handler(CommandHandler("help", self.handle_help))
    
    async def run_bot(self):
        """Run the Telegram bot with polling."""
        if not TELEGRAM_AVAILABLE:
            logging.error("python-telegram-bot not installed. Cannot run bot.")
            return
        
        if not self.validate_config():
            logging.error("Invalid configuration. Cannot run bot.")
            return
        
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Setup handlers
        self.setup_handlers(self.application)
        
        # Start bot
        logging.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logging.info("Telegram bot is running. Press Ctrl+C to stop.")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping bot...")
            await self.application.stop()
    
    def run_scheduled(self):
        """Run scheduled tasks (for use without async bot)."""
        if not self.validate_config():
            return
        
        # Schedule daily report at 8:00 PM PST (20:00)
        # Note: schedule library uses system timezone
        schedule.every().day.at("20:00").do(self._run_scheduled_task)
        
        logging.info("Scheduled tasks configured: Daily report at 8:00 PM PST")
        
        # Run initial report
        logging.info("Running initial report...")
        asyncio.run(self.send_daily_report())
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time_module.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logging.info("Stopping scheduler...")
    
    def _run_scheduled_task(self):
        """Wrapper for scheduled task (runs in separate thread)."""
        asyncio.run(self.send_daily_report())


def setup_telegram_config():
    """Interactive setup for Telegram configuration."""
    print("🤖 Telegram Bot Setup")
    print("=" * 50)
    
    # Get bot token
    token = input("Enter your Telegram bot token (from @BotFather): ").strip()
    if not token:
        print("Token is required. Exiting.")
        return False
    
    # Get chat ID
    print("\nTo get your chat ID:")
    print("1. Start a chat with your bot")
    print("2. Send any message to the bot")
    print("3. Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates")
    print("4. Look for 'chat': {'id': <YOUR_CHAT_ID>}")
    
    chat_id = input("\nEnter your chat ID: ").strip()
    if not chat_id:
        print("Chat ID is required. Exiting.")
        return False
    
    # Create config
    config = {
        'token': token,
        'chat_id': chat_id,
        'setup_date': datetime.now().isoformat()
    }
    
    config_file = '../config/telegram_config.json'
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to {config_file}")
    print("\nNext steps:")
    print("1. Start the bot with: python telegram_bot.py --mode=bot (interactive)")
    print("2. Or run scheduled: python telegram_bot.py --mode=scheduled (daily at 8PM)")
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Stock Screener Telegram Bot')
    parser.add_argument('--mode', choices=['setup', 'bot', 'scheduled', 'test'],
                       default='test', help='Operation mode')
    parser.add_argument('--config', default='../config/telegram_config.json',
                       help='Path to config file')
    
    args = parser.parse_args()
    
    if args.mode == 'setup':
        setup_telegram_config()
    
    elif args.mode == 'test':
        # Test mode: run screener and print results
        print("🧪 Test Mode: Running screener without Telegram")
        bot = StockScreenerBot(config_file=args.config)
        
        # Run screener
        screened_stocks = bot.screener.screen_stocks(top_n=10)
        
        # Print results
        report = bot.screener.generate_report(screened_stocks, output_format='text')
        print(report)
        
        # Save results
        if screened_stocks:
            bot.screener.save_results(screened_stocks)
    
    elif args.mode == 'bot':
        # Run interactive bot
        if not TELEGRAM_AVAILABLE:
            print("Error: python-telegram-bot not installed.")
            print("Install with: pip install python-telegram-bot")
            return
        
        bot = StockScreenerBot(config_file=args.config)
        
        if not bot.validate_config():
            print("Invalid configuration. Run with --mode=setup first.")
            return
        
        # Run async bot
        asyncio.run(bot.run_bot())
    
    elif args.mode == 'scheduled':
        # Run scheduled tasks
        bot = StockScreenerBot(config_file=args.config)
        
        if not bot.validate_config():
            print("Invalid configuration. Run with --mode=setup first.")
            return
        
        bot.run_scheduled()


if __name__ == "__main__":
    main()