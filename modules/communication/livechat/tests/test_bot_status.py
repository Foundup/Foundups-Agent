#!/usr/bin/env python3
"""Quick bot status checker"""

import os
import sys
import json
from datetime import datetime, timedelta

# Check if bot is running
def check_bot_status():
    log_path = "modules/communication/livechat/memory/chat_logs/live_chat_debug.log"
    
    if not os.path.exists(log_path):
        print("❌ No log file found - bot never ran")
        return
    
    # Check last modified time
    mtime = os.path.getmtime(log_path)
    last_modified = datetime.fromtimestamp(mtime)
    time_since = datetime.now() - last_modified
    
    print(f"📊 BOT STATUS CHECK")
    print(f"="*40)
    print(f"Log last updated: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time since update: {time_since.total_seconds()/60:.1f} minutes")
    
    if time_since.total_seconds() < 60:
        print("✅ Bot is ACTIVE (log recently updated)")
    elif time_since.total_seconds() < 300:
        print("⚠️ Bot might be idle (no recent activity)")
    else:
        print("❌ Bot is NOT running (log is old)")
    
    # Check database
    db_path = "modules/communication/chat_rules/data/chat_rules.db"
    if os.path.exists(db_path):
        db_mtime = os.path.getmtime(db_path)
        db_modified = datetime.fromtimestamp(db_mtime)
        db_time_since = datetime.now() - db_modified
        print(f"\n📊 DATABASE STATUS")
        print(f"Last updated: {db_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Time since: {db_time_since.total_seconds()/60:.1f} minutes")
    
    print(f"\n💡 QUICK ACTIONS:")
    if time_since.total_seconds() > 300:
        print("1. Start bot: python main.py → Option 1")
        print("2. Check if you're live on YouTube")
        print("3. Test with 'love maga' in chat")
    else:
        print("1. Test 'love maga' in chat")
        print("2. Test '/score' command")
        print("3. Check terminal for output")

if __name__ == "__main__":
    check_bot_status()