"""Fix monthly scores for August 2025"""
import sqlite3
from datetime import datetime

db_path = "O:/Foundups-Agent/modules/gamification/whack_a_magat/data/magadoom_scores.db"
current_month = "2025-08"  # August 2025

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# For users with scores but no current_month set, migrate their scores to August monthly
cursor.execute("""
    UPDATE profiles 
    SET monthly_score = score,
        monthly_frag_count = frag_count,
        current_month = ?
    WHERE current_month = '' OR current_month IS NULL
""", (current_month,))

affected = cursor.rowcount
conn.commit()

print(f"✅ Migrated {affected} users to August 2025 monthly tracking")

# Show the updated leaderboard
cursor.execute("""
    SELECT username, score, monthly_score, frag_count, monthly_frag_count, current_month
    FROM profiles 
    WHERE monthly_score > 0
    ORDER BY monthly_score DESC 
    LIMIT 10
""")

print(f"\n🏆 AUGUST 2025 LEADERBOARD:")
for row in cursor.fetchall():
    print(f"  {row[1]:20} - Monthly: {row[2]:4} XP ({row[4]:2} whacks) | All-time: {row[1]:4} XP")

conn.close()