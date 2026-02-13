#!/usr/bin/env python
"""
Schedule Stock Screener with OpenClaw Cron
Sets up automatic daily screening at 8:00 PM PST.
"""

import json
import os
import logging
from datetime import datetime, timedelta
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def create_openclaw_cron_job():
    """
    Create OpenClaw cron job for daily stock screening.
    This creates a JSON configuration that can be loaded into OpenClaw's cron system.
    """
    
    # Job configuration
    job_config = {
        "name": "daily-stock-screener",
        "description": "Daily stock screening at 8:00 PM PST",
        "schedule": {
            "kind": "cron",
            "expr": "0 20 * * 1-5",  # 8:00 PM PST Monday-Friday (20:00 UTC-8 = 04:00 UTC next day)
            "tz": "America/Vancouver"  # PST/PDT timezone
        },
        "payload": {
            "kind": "agentTurn",
            "message": "Run the daily stock screener and send results via Telegram. Use the combined_screener.py script to find top 10 oversold stocks with strong fundamentals (Buffett score ≥ 5/10). Send formatted report via Telegram bot.",
            "model": "deepseek/deepseek-chat",
            "thinking": "verbose",
            "timeoutSeconds": 300
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7960853847",  # Your Telegram chat ID
            "bestEffort": True
        },
        "enabled": True
    }
    
    # Save to file
    config_dir = '../config'
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, 'openclaw_cron_job.json')
    
    with open(config_file, 'w') as f:
        json.dump(job_config, f, indent=2)
    
    logging.info(f"Cron job configuration saved to {config_file}")
    
    # Also create a simple script that OpenClaw can run
    script_content = '''#!/usr/bin/env python
"""
OpenClaw Stock Screener Task
Runs daily screening and sends results via Telegram.
"""

import sys
import os

# Add scripts directory to path
sys.path.append(os.path.dirname(__file__))

from combined_screener import CombinedScreener
from telegram_bot import StockScreenerBot

def main():
    """Run screener and send results."""
    print("🔄 Running daily stock screener...")
    
    # Initialize screener
    screener = CombinedScreener(
        min_buffett_score=5,
        technical_threshold=-80.0
    )
    
    # Run screening
    screened_stocks = screener.screen_stocks(top_n=10)
    
    # Initialize Telegram bot
    bot = StockScreenerBot()
    
    # Generate and send report
    if screened_stocks:
        report = screener.generate_report(screened_stocks, output_format='telegram')
        
        # Send via Telegram (async)
        import asyncio
        success = asyncio.run(bot.send_message(report))
        
        if success:
            print(f"✅ Report sent successfully ({len(screened_stocks)} stocks)")
            
            # Save results
            screener.save_results(screened_stocks)
        else:
            print("❌ Failed to send report")
    else:
        message = "📊 *Daily Stock Screener Report*\\n\\nNo quality oversold stocks found today."
        import asyncio
        asyncio.run(bot.send_message(message))
        print("⚠️ No quality stocks found")
    
    print("✅ Daily screening complete")

if __name__ == "__main__":
    main()
'''
    
    script_file = os.path.join(config_dir, 'run_daily_screener.py')
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    logging.info(f"Script saved to {script_file}")
    
    return config_file, script_file

def create_systemd_service():
    """
    Create systemd service for running the screener on a Linux server.
    For Windows, this would create a scheduled task instead.
    """
    
    service_content = '''[Unit]
Description=Daily Stock Screener
After=network.target

[Service]
Type=oneshot
User=openclaw
WorkingDirectory=/root/.openclaw/workspace/stock-screener/backend/scripts
ExecStart=/usr/bin/python3 /root/.openclaw/workspace/stock-screener/backend/scripts/run_daily_screener.py
Environment="PYTHONPATH=/root/.openclaw/workspace/stock-screener/backend/scripts"

[Install]
WantedBy=multi-user.target
'''
    
    service_file = '../config/daily-stock-screener.service'
    
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    logging.info(f"Systemd service file saved to {service_file}")
    
    # Also create timer for 8:00 PM PST
    timer_content = '''[Unit]
Description=Run stock screener daily at 8:00 PM PST

[Timer]
OnCalendar=Mon..Fri 20:00:00 America/Vancouver
Persistent=true

[Install]
WantedBy=timers.target
'''
    
    timer_file = '../config/daily-stock-screener.timer'
    
    with open(timer_file, 'w') as f:
        f.write(timer_content)
    
    logging.info(f"Systemd timer file saved to {timer_file}")
    
    return service_file, timer_file

def create_windows_task():
    """
    Create Windows scheduled task configuration.
    """
    
    task_content = '''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2026-02-12T00:00:00</Date>
    <Author>StockScreener</Author>
    <Description>Daily Stock Screener at 8:00 PM PST</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-02-12T20:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Monday />
          <Tuesday />
          <Wednesday />
          <Thursday />
          <Friday />
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>"C:\\Users\\JimTiny\\.openclaw\\workspace\\stock-screener\\backend\\scripts\\run_daily_screener.py"</Arguments>
      <WorkingDirectory>C:\\Users\\JimTiny\\.openclaw\\workspace\\stock-screener\\backend\\scripts</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
'''
    
    task_file = '../config/daily-stock-screener.xml'
    
    with open(task_file, 'w') as f:
        f.write(task_content)
    
    logging.info(f"Windows task XML saved to {task_file}")
    
    # Also create PowerShell script to register the task
    ps_script = '''# PowerShell script to register scheduled task
$taskName = "DailyStockScreener"
$taskDescription = "Runs stock screener daily at 8:00 PM PST"
$taskPath = "\\StockScreener\\"
$scriptPath = "C:\\Users\\JimTiny\\.openclaw\\workspace\\stock-screener\\backend\\scripts\\run_daily_screener.py"
$pythonPath = "python"

# Create action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`""

# Create trigger (Monday-Friday at 8:00 PM)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday -At "8:00PM"

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Register task
Register-ScheduledTask -TaskName $taskName -Description $taskDescription -Action $action -Trigger $trigger -Settings $settings -Force

Write-Host "Scheduled task '$taskName' registered successfully"
Write-Host "Task will run: Monday-Friday at 8:00 PM PST"
Write-Host "Script: $scriptPath"
'''
    
    ps_file = '../config/register-windows-task.ps1'
    
    with open(ps_file, 'w') as f:
        f.write(ps_script)
    
    logging.info(f"PowerShell script saved to {ps_file}")
    
    return task_file, ps_file

def test_screener():
    """Test the screener to ensure it works."""
    logging.info("Testing stock screener...")
    
    try:
        # Import and run screener
        sys.path.append(os.path.dirname(__file__))
        
        from combined_screener import CombinedScreener
        
        screener = CombinedScreener(
            min_buffett_score=5,
            technical_threshold=-80.0
        )
        
        # Run screening
        screened_stocks = screener.screen_stocks(top_n=5)
        
        if screened_stocks:
            logging.info(f"Test successful! Found {len(screened_stocks)} stocks")
            
            # Print summary
            for i, stock in enumerate(screened_stocks[:3], 1):
                logging.info(f"{i}. {stock['ticker']} - Buffett: {stock['fundamental_analysis']['buffett_score']}/10, "
                           f"Combined: {stock['scores']['combined']:.1f}/100")
            
            return True
        else:
            logging.warning("Test successful but no stocks found (may be normal)")
            return True
            
    except Exception as e:
        logging.error(f"Test failed: {e}")
        return False

def setup_environment():
    """Setup Python environment with required packages."""
    logging.info("Setting up environment...")
    
    requirements = [
        'yfinance>=0.2.38',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'requests>=2.31.0',
        'schedule>=1.2.0',
        'python-telegram-bot>=20.7'  # Optional, for Telegram bot
    ]
    
    requirements_file = '../config/requirements.txt'
    
    with open(requirements_file, 'w') as f:
        for req in requirements:
            f.write(req + '\n')
    
    logging.info(f"Requirements file saved to {requirements_file}")
    
    # Create setup script
    setup_script = '''#!/bin/bash
# Setup script for Stock Screener

echo "Setting up Stock Screener environment..."

# Install Python packages
pip install -r requirements.txt

# Create necessary directories
mkdir -p ../data/results
mkdir -p ../logs
mkdir -p ../config

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure Telegram bot: python telegram_bot.py --mode=setup"
echo "2. Test screener: python schedule_screener.py --test"
echo "3. Set up scheduling based on your platform:"
echo "   - Linux: Use systemd service"
echo "   - Windows: Use scheduled task"
echo "   - OpenClaw: Use cron job configuration"
'''
    
    setup_file = '../config/setup.sh'
    
    with open(setup_file, 'w') as f:
        f.write(setup_script)
    
    logging.info(f"Setup script saved to {setup_file}")
    
    return requirements_file, setup_file

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Schedule Stock Screener')
    parser.add_argument('--action', choices=['setup', 'test', 'create-all', 'openclaw', 'systemd', 'windows'],
                       default='test', help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'setup':
        # Setup environment
        requirements_file, setup_file = setup_environment()
        print(f"✅ Environment setup files created:")
        print(f"   - {requirements_file}")
        print(f"   - {setup_file}")
        print("\nRun: bash setup.sh to install dependencies")
    
    elif args.action == 'test':
        # Test screener
        success = test_screener()
        if success:
            print("✅ Screener test passed!")
        else:
            print("❌ Screener test failed")
            sys.exit(1)
    
    elif args.action == 'openclaw':
        # Create OpenClaw cron job
        config_file, script_file = create_openclaw_cron_job()
        print(f"✅ OpenClaw cron job configuration created:")
        print(f"   - Config: {config_file}")
        print(f"   - Script: {script_file}")
        print("\nTo use with OpenClaw:")
        print("1. Load the cron job: openclaw cron add --file config/openclaw_cron_job.json")
        print("2. Enable it: openclaw cron enable daily-stock-screener")
    
    elif args.action == 'systemd':
        # Create systemd service (Linux)
        service_file, timer_file = create_systemd_service()
        print(f"✅ Systemd service files created:")
        print(f"   - Service: {service_file}")
        print(f"   - Timer: {timer_file}")
        print("\nTo install on Linux:")
        print("1. sudo cp config/daily-stock-screener.* /etc/systemd/system/")
        print("2. sudo systemctl daemon-reload")
        print("3. sudo systemctl enable --now daily-stock-screener.timer")
    
    elif args.action == 'windows':
        # Create Windows scheduled task
        task_file, ps_file = create_windows_task()
        print(f"✅ Windows scheduled task files created:")
        print(f"   - Task XML: {task_file}")
        print(f"   - PowerShell script: {ps_file}")
        print("\nTo install on Windows:")
        print("1. Open PowerShell as Administrator")
        print("2. Run: .\\config\\register-windows-task.ps1")
    
    elif args.action == 'create-all':
        # Create all configurations
        print("Creating all scheduling configurations...")
        
        # Setup environment
        requirements_file, setup_file = setup_environment()
        
        # OpenClaw
        config_file, script_file = create_openclaw_cron_job()
        
        # Systemd (Linux)
        service_file, timer_file = create_systemd_service()
        
        # Windows
        task_file, ps_file = create_windows_task()
        
        print("\n✅ All configurations created!")
        print("\n📁 Files created:")
        print(f"  Environment:")
        print(f"    - {requirements_file}")
        print(f"    - {setup_file}")
        print(f"  OpenClaw:")
        print(f"    - {config_file}")
        print(f"    - {script_file}")
        print(f"  Linux (systemd):")
        print(f"    - {service_file}")
        print(f"    - {timer_file}")
        print(f"  Windows:")
        print(f"    - {task_file}")
        print(f"    - {ps_file}")
        
        # Test screener
        print("\n🧪 Testing screener...")
        success = test_screener()
        if success:
            print("✅ Screener test passed!")
        else:
            print("⚠️ Screener test had issues (may be normal if no stocks match criteria)")
        
        print("\n🎯 Next steps:")
        print("1. Install dependencies: pip install -r config/requirements.txt")
        print("2. Configure Telegram: python telegram_bot.py --mode=setup")
        print("3. Choose scheduling method based on your platform")
        print("4. Test manually: python combined_screener.py")


if __name__ == "__main__":
    main()