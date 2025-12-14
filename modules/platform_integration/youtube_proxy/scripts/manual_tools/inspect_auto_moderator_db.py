from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

"""Inspect auto_moderator.db schema and sample data."""
import sqlite3
from pathlib import Path

db_path = Path("modules/communication/livechat/memory/auto_moderator.db")

if not db_path.exists():
    print(f"Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"Database: {db_path}")
print(f"Tables found: {len(tables)}\n")
print("="*60)

for table_name in tables:
    table = table_name[0]
    print(f"\nTable: {table}")
    print("-"*60)

    # Get schema
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()

    print("Schema:")
    for col in columns:
        col_id, col_name, col_type, not_null, default, pk = col
        constraints = []
        if pk:
            constraints.append("PRIMARY KEY")
        if not_null:
            constraints.append("NOT NULL")
        constraint_str = f" ({', '.join(constraints)})" if constraints else ""
        print(f"  {col_name}: {col_type}{constraint_str}")

    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"\nRows: {count}")

    # Show sample data (first 3 rows)
    if count > 0:
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        rows = cursor.fetchall()
        print(f"\nSample data (first {len(rows)} rows):")
        for row in rows:
            # Handle Unicode in output
            row_str = str(row)
            print(f"  {row_str}".encode('ascii', errors='replace').decode('ascii'))

print("\n" + "="*60)

conn.close()
