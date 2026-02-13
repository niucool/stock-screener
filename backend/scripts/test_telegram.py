#!/usr/bin/env python
"""
Test Telegram sending.
"""

import os
import json
import asyncio

def test_telegram():
    """Test Telegram connection."""
    
    print("Testing Telegram...")
    
    try:
        from telegram import Bot
        from telegram.constants import ParseMode
        
        # Check config
        config_file = '../config/telegram_config.json'
        if not os.path.exists(config_file):
            print(f"Config file not found: {config_file}")
            print("Please run: python telegram_bot.py --mode=setup")
            return False
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        token = config.get('token')
        chat_id = config.get('chat_id')
        
        if not token or not chat_id:
            print("Token or chat_id missing from config.")
            return False
        
        print(f"Token: {token[:10]}...")
        print(f"Chat ID: {chat_id}")
        
        # Test sending
        async def send_test():
            bot = Bot(token=token)
            await bot.send_message(
                chat_id=chat_id,
                text="🤖 *Stock Screener Test*\\nThis is a test message from your enhanced stock screener system.",
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        
        success = asyncio.run(send_test())
        
        if success:
            print("Test message sent successfully!")
            return True
        else:
            print("Failed to send test message.")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("TELEGRAM TEST")
    print("=" * 60)
    
    if test_telegram():
        print("\n✅ Telegram test passed!")
    else:
        print("\nTelegram test failed.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()