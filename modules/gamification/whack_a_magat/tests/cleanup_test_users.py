"""Clean up test users from database"""
import sqlite3
import os

db_path = "O:/Foundups-Agent/modules/gamification/whack_a_magat/data/magadoom_scores.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count test users before deletion
    cursor.execute("SELECT COUNT(*) FROM profiles WHERE user_id LIKE 'test_user%'")
    test_count = cursor.fetchone()[0]
    print(f"Found {test_count} test users to remove")
    
    # Delete test users
    cursor.execute("DELETE FROM profiles WHERE user_id LIKE 'test_user%'")
    conn.commit()
    
    print(f"[OK] Removed {test_count} test users from database")
    
    # Show remaining top users
    cursor.execute("""
        SELECT username, monthly_score, score, frag_count 
        FROM profiles 
        ORDER BY monthly_score DESC 
        LIMIT 5
    """)
    
    print("\nTop 5 real users after cleanup:")
    for row in cursor.fetchall():
        print(f"  {row[0]:20} - Monthly: {row[1]} XP, All-time: {row[2]} XP, Frags: {row[3]}")
    
    conn.close()
else:
    print(f"Database not found at {db_path}")