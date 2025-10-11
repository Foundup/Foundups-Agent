#!/usr/bin/env python3
"""Check stream database for yWBpFZxh2ds"""
import sys
from modules.platform_integration.stream_resolver.src.stream_db import StreamResolverDB
from datetime import datetime

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
