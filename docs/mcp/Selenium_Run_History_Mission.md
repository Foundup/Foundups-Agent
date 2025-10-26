# Selenium Run History Mission - MCP Documentation

## Overview

The Selenium Run History Mission provides automated analysis and summarization of Selenium session data stored in `foundups.db`. This mission aggregates session statistics, performance metrics, and provides structured data ready for Qwen/Gemma AI processing.

## Mission Details

**Location**: `holo_index/missions/selenium_run_history.py`  
**MCP Method**: `selenium_run_history(days=7)`  
**WSP Compliance**: WSP 77 (Agent Coordination), WSP 90 (UTF-8 Enforcement)

## Invocation Methods

### Via MCP Client (Recommended)

```python
from holo_index.mcp_client.holo_mcp_client import HoloIndexMCPClient

async with HoloIndexMCPClient() as client:
    result = await client.selenium_run_history(days=7)

    if result['success']:
        print(f"Analyzed {result['data']['raw_session_count']} sessions")
        print(f"Success rate: {result['data']['overall_stats']['success_rate']:.1f}%")
```

### Direct CLI Execution

```bash
# Analyze last 7 days (default)
python holo_index/missions/selenium_run_history.py

# Analyze last 30 days
python holo_index/missions/selenium_run_history.py --days 30

# Use custom database path
python holo_index/missions/selenium_run_history.py --db-path /path/to/foundups.db
```

### Via MCP Gateway (Future)

```bash
# When integrated with MCP gateway
mcp-client call selenium_run_history --days 7
```

## Data Structure

### Overall Statistics

```json
{
  "total_sessions": 150,
  "success_rate": 87.3,
  "avg_duration": 45.2,
  "unique_urls": 12,
  "time_range": {
    "earliest": "2025-10-12T08:30:00",
    "latest": "2025-10-19T16:45:00",
    "days_span": 7
  }
}
```

### URL Breakdown

```json
{
  "https://example.com/page1": {
    "total_runs": 45,
    "success_count": 42,
    "failed_count": 2,
    "timeout_count": 1,
    "avg_duration": 32.1,
    "success_rate": 93.3,
    "last_run": "2025-10-19T16:30:00",
    "last_hash": "abc123...",
    "unique_hashes": ["abc123", "def456"],
    "browsers_used": ["chrome", "firefox"],
    "recent_runs": [
      {
        "start_time": "2025-10-19T16:30:00",
        "status": "success",
        "duration": 28,
        "hash": "abc123"
      }
    ]
  }
}
```

## Database Schema

The mission automatically creates the `selenium_sessions` table if it doesn't exist:

```sql
CREATE TABLE selenium_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT CHECK(status IN ('success', 'failed', 'timeout', 'error')),
    hash TEXT,
    duration_seconds INTEGER,
    user_agent TEXT,
    browser TEXT DEFAULT 'chrome',
    session_id TEXT,
    error_message TEXT,
    page_title TEXT,
    screenshot_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Integration with Qwen/Gemma

The mission output is specifically structured for AI summarization:

```python
# Example AI summary generation
mission_result = await client.selenium_run_history(days=7)

summary_prompt = f"""
Analyze this Selenium run data and provide insights:

Overall: {mission_result['data']['overall_stats']}
Top URLs: {list(mission_result['data']['url_breakdown'].keys())[:5]}

Generate a concise executive summary.
"""

ai_summary = await qwen.generate_summary(summary_prompt)
```

## Error Handling

### Database Connection Issues

```json
{
  "mission": "selenium_run_history",
  "error": "Database connection failed: [Errno 2] No such file or directory",
  "summary_ready": false
}
```

### Empty Dataset

```json
{
  "mission": "selenium_run_history",
  "parameters": {"days_analyzed": 7, "table_existed": true},
  "overall_stats": {"total_sessions": 0},
  "raw_session_count": 0,
  "summary_ready": true
}
```

## Performance Considerations

- **Database Indexes**: Automatically created for optimal query performance
- **Memory Usage**: Processes data in chunks for large datasets
- **Time Filtering**: Uses indexed timestamps for efficient date range queries
- **Caching**: Results can be cached for repeated analysis

## Security Features

- **Read-Only Operations**: Never modifies session data
- **Parameterized Queries**: Prevents SQL injection
- **Path Validation**: Validates database file paths
- **Error Sanitization**: Safe error messages without sensitive data

## Future Enhancements

- Real-time session monitoring integration
- Advanced analytics (trend analysis, anomaly detection)
- Multi-database support
- Export capabilities (CSV, JSON)
- Dashboard integration
