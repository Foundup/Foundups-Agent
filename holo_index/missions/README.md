# HoloIndex Missions Directory

## Overview

This directory contains autonomous missions that can be executed via the HoloIndex MCP client. Missions are specialized analysis tasks that provide structured data for Qwen/Gemma summarization and processing.

## Available Missions

### selenium_run_history.py
**Purpose**: Analyze and summarize Selenium session data from foundups.db

**Features**:
- Aggregates session statistics by URL
- Tracks success rates and performance metrics
- Provides structured data for AI summarization
- Handles missing database tables gracefully

**Usage**:
```python
from holo_index.mcp_client.holo_mcp_client import HoloIndexMCPClient

async with HoloIndexMCPClient() as client:
    result = await client.selenium_run_history(days=7)
```

**CLI Usage**:
```bash
python holo_index/missions/selenium_run_history.py --days 7
```

## Mission Architecture

Each mission follows the WSP framework:
- **WSP 77**: Agent Coordination Protocol
- **WSP 90**: UTF-8 Enforcement
- **Structured Output**: Ready for Qwen/Gemma processing

## Adding New Missions

1. Create mission file in this directory
2. Implement mission class with `execute_mission()` method
3. Add async method to `HoloIndexMCPClient`
4. Update this README
5. Add tests in `holo_index/tests/`

## Integration

Missions are automatically discoverable through the MCP client interface and can be invoked by Qwen/Gemma agents for specialized analysis tasks.
