#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

import sqlite3

# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

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
