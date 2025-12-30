#!/usr/bin/env python3
"""
Query Moderators and Verify Chat Logging
========================================

Checks:
1. Whack-a-MAGA leaderboard (all participants are moderators!)
2. Auto-moderator database (MOD/OWNER roles)
3. Chat telemetry logging status
4. Recent chat messages logged
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Database paths
AUTO_MOD_DB = PROJECT_ROOT / "modules/communication/livechat/memory/auto_moderator.db"
FOUNDUPS_DB = PROJECT_ROOT / "data/foundups.db"
WHACK_DB = PROJECT_ROOT / "modules/gamification/whack_a_magat/data/magadoom_scores.db"

print("="*80)
print(" MODERATOR & LOGGING AUDIT")
print("="*80)

# 1. Check Whack-a-MAGA Leaderboard
print("\n[1] WHACK-A-MAGA LEADERBOARD (All Participants = Moderators)")
print("-"*80)

if WHACK_DB.exists():
    conn = sqlite3.connect(WHACK_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, user_id, score, monthly_score, rank, frag_count, monthly_frag_count
        FROM profiles
        ORDER BY monthly_score DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    if rows:
        print(f"Found {len(rows)} participants on Whack-a-MAGA leaderboard:\n")
        for i, (username, user_id, score, monthly, rank, frags, monthly_frags) in enumerate(rows, 1):
            # Handle Unicode properly
            username_safe = username.encode('ascii', 'replace').decode('ascii')
            print(f"{i:2}. {username_safe:30} | Monthly: {monthly:6} XP | Rank: {rank:15} | Frags: {monthly_frags:3} this month")

        print("\n" + "="*80)
        print("ALL LEADERBOARD PARTICIPANTS ARE MODERATORS!")
        print("="*80)

        # Extract moderator usernames
        moderator_usernames = [row[0] for row in rows if row[0] != "Unknown"]
        print(f"\nModerator usernames to add to KNOWN_MODS:")
        print(moderator_usernames)
    else:
        print("No leaderboard data found.")

    conn.close()
else:
    print(f"⚠️ Whack-a-MAGA database not found: {WHACK_DB}")

# 2. Check Auto-Moderator Database
print("\n\n[2] AUTO-MODERATOR DATABASE (MOD/OWNER Roles)")
print("-"*80)

if AUTO_MOD_DB.exists():
    conn = sqlite3.connect(AUTO_MOD_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, user_id, role, message_count, last_seen
        FROM users
        WHERE role IN ('MOD', 'OWNER')
        ORDER BY message_count DESC
    """)

    rows = cursor.fetchall()

    if rows:
        print(f"Found {len(rows)} moderators in auto_moderator.db:\n")
        for i, (username, user_id, role, msg_count, last_seen) in enumerate(rows, 1):
            print(f"{i:2}. {username:30} | Role: {role:6} | Messages: {msg_count:5} | Last seen: {last_seen or 'N/A'}")
    else:
        print("No moderators found in database.")

    # Check total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    print(f"\nTotal users in database: {total}")

    conn.close()
else:
    print(f"⚠️ Auto-moderator database not found: {AUTO_MOD_DB}")

# 3. Check Chat Telemetry Logging
print("\n\n[3] CHAT TELEMETRY LOGGING STATUS")
print("-"*80)

if FOUNDUPS_DB.exists():
    conn = sqlite3.connect(FOUNDUPS_DB)
    cursor = conn.cursor()

    # Check if chat_messages table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_messages'")
    table_exists = cursor.fetchone()

    if table_exists:
        print("✅ chat_messages table exists in foundups.db")

        # Count total messages
        cursor.execute("SELECT COUNT(*) FROM chat_messages")
        total_messages = cursor.fetchone()[0]
        print(f"✅ Total messages logged: {total_messages:,}")

        # Check recent messages (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute("""
            SELECT COUNT(*)
            FROM chat_messages
            WHERE persisted_at > ?
        """, (yesterday,))
        recent_count = cursor.fetchone()[0]
        print(f"✅ Messages in last 24 hours: {recent_count:,}")

        # Show 10 most recent messages
        cursor.execute("""
            SELECT author_name, role, message_text, persisted_at
            FROM chat_messages
            ORDER BY persisted_at DESC
            LIMIT 10
        """)
        recent_messages = cursor.fetchall()

        if recent_messages:
            print(f"\n📝 Most recent 10 messages:")
            for author, role, text, timestamp in recent_messages:
                text_preview = text[:60] + "..." if len(text) > 60 else text
                print(f"   {timestamp[:19]} | {author:20} ({role:5}) | {text_preview}")

        # Check unique authors
        cursor.execute("SELECT COUNT(DISTINCT author_name) FROM chat_messages")
        unique_authors = cursor.fetchone()[0]
        print(f"\n✅ Unique chatters logged: {unique_authors:,}")

    else:
        print("❌ chat_messages table does NOT exist in foundups.db!")
        print("   Chat logging may not be active.")

    conn.close()
else:
    print(f"⚠️ FoundUps database not found: {FOUNDUPS_DB}")

# 4. Check for Moderation Action Logs
print("\n\n[4] MODERATION ACTIONS LOGGING")
print("-"*80)

if AUTO_MOD_DB.exists():
    conn = sqlite3.connect(AUTO_MOD_DB)
    cursor = conn.cursor()

    # Check for timeout/moderation tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"Tables in auto_moderator.db: {', '.join(tables)}")

    # Check if timeout actions are logged
    if 'timeout_actions' in tables or 'moderation_actions' in tables:
        print("✅ Moderation action logging table exists")

        # Try to get recent moderation actions
        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM timeout_actions
                WHERE timestamp > datetime('now', '-7 days')
            """)
            recent_actions = cursor.fetchone()[0]
            print(f"✅ Moderation actions in last 7 days: {recent_actions}")
        except:
            print("⚠️ Could not query timeout_actions table")
    else:
        print("⚠️ No dedicated moderation action logging table found")
        print(f"   Available tables: {tables}")

    conn.close()

print("\n" + "="*80)
print(" AUDIT COMPLETE")
print("="*80)
