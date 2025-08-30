"""Check database contents"""
import sqlite3
import os

db_path = "O:/Foundups-Agent/modules/gamification/whack_a_magat/data/magadoom_scores.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("SELECT COUNT(*) FROM profiles")
    count = cursor.fetchone()[0]
    print(f"Total profiles: {count}")
    
    # Get top 10 by monthly score
    cursor.execute("""
        SELECT user_id, username, score, monthly_score, frag_count, monthly_frag_count, current_month, rank
        FROM profiles 
        ORDER BY monthly_score DESC 
        LIMIT 10
    """)
    
    print("\nTop 10 by monthly score:")
    for row in cursor.fetchall():
        print(f"  {row[1]:20} (ID: {row[0][:20]}...) - Monthly: {row[3]} XP, All-time: {row[2]} XP")
    
    # Check for test users
    cursor.execute("SELECT COUNT(*) FROM profiles WHERE user_id LIKE 'test_user%'")
    test_count = cursor.fetchone()[0]
    print(f"\nTest users in database: {test_count}")
    
    # Get real users (non-test)
    cursor.execute("""
        SELECT user_id, username, score, monthly_score, frag_count
        FROM profiles 
        WHERE user_id NOT LIKE 'test_user%'
        ORDER BY monthly_score DESC 
        LIMIT 10
    """)
    
    print("\nReal users (non-test):")
    for row in cursor.fetchall():
        print(f"  {row[1]:20} - Monthly: {row[3]} XP, All-time: {row[2]} XP, Frags: {row[4]}")
    
    conn.close()
else:
    print(f"Database not found at {db_path}")