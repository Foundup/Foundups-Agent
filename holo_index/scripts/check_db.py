#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('data/foundups.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('All Tables:', tables)

# Get HoloIndex tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%holo_index%'")
holo_tables = cursor.fetchall()
print('HoloIndex Tables:', holo_tables)

# Check violations table
if holo_tables:
    try:
        cursor.execute("SELECT * FROM modules_holo_index_violations")
        violations = cursor.fetchall()
        print('Violations:', violations)
    except Exception as e:
        print('Error checking violations:', e)

conn.close()
