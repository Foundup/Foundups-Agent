#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check stream database for yWBpFZxh2ds"""
import sys
from modules.platform_integration.stream_resolver.src.stream_db import StreamResolverDB
from datetime import datetime

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

db = StreamResolverDB()
result = db.select('stream_times', 'video_id = ?', ('yWBpFZxh2ds',))

if result:
    for row in result:
        print(f"Stream: {row}")
        # Check if stream_end exists
        if len(row) > 3 and row[3]:  # stream_end column
            end_time = datetime.fromisoformat(row[3]) if isinstance(row[3], str) else row[3]
            now = datetime.now()
            hours_since_end = (now - end_time).total_seconds() / 3600
            print(f"Hours since end: {hours_since_end:.1f}")
            print(f"Ended more than 24h ago: {hours_since_end > 24}")
else:
    print("No DB entry found for yWBpFZxh2ds")
