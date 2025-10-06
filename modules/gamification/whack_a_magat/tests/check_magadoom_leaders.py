#!/usr/bin/env python3
"""Quick script to check MAGADOOM HGS leaderboard and MOD leaders"""

import sqlite3

# Connect to database
conn = sqlite3.connect('modules/gamification/whack_a_magat/data/magadoom_scores.db')
cursor = conn.cursor()

# Query top 10 leaders
cursor.execute('''
    SELECT username, user_id, score, rank, level, frag_count,
           monthly_score, monthly_frag_count
    FROM profiles
    ORDER BY score DESC
    LIMIT 10
''')

rows = cursor.fetchall()

print("\n" + "="*80)
print("TOP 10 MAGADOOM HGS LEADERS (ALL-TIME)")
print("="*80)

for i, row in enumerate(rows, 1):
    username, user_id, score, rank, level, frags, monthly, monthly_frags = row

    # Truncate username if too long
    display_name = username if username else user_id[:20]

    print(f"{i:2}. {display_name:20} | Score: {score:6} | Rank: {rank:15} | "
          f"Level: {level:2} | Whacks: {frags:4} | Monthly: {monthly:5} ({monthly_frags} whacks)")

print("="*80)

# Check if there are MOD-specific scores
cursor.execute('''
    SELECT COUNT(*) FROM profiles WHERE user_id LIKE '%MOD%' OR username LIKE '%MOD%'
''')
mod_count = cursor.fetchone()[0]

print(f"\nTotal MOD entries in database: {mod_count}")

conn.close()
