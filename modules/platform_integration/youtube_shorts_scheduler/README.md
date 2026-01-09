# YouTube Shorts Scheduler

**WSP Compliant Module** - YouTube Studio automation for Shorts scheduling.

## Overview

Automated scheduling system for YouTube Shorts across multiple channels:
- **Move2Japan** (UC-LSSlOZwpGIRIYihaz8zCw)
- **UnDaoDu** (UCfHM9Fw9HD-NwiS0seD_oIA)
- **FoundUps** (UCSNTUXjAgpd4sgWYP0xoJgw)

## Features

- Selenium/UI-TARS DOM automation for YouTube Studio
- Multi-channel scheduling with time slot management
- Smart slot allocation (max 3 per day, 3 hours apart)
- Automatic title/description generation (FFCPLN format)
- Schedule tracking with JSON persistence
- Visibility workflow automation (Unlisted -> Scheduled -> Public)

## Architecture

```
youtube_shorts_scheduler/
├── README.md           # This file
├── INTERFACE.md        # Public API documentation
├── ModLog.md           # Change log
├── requirements.txt    # Dependencies
├── src/
│   ├── __init__.py
│   ├── scheduler.py           # Main scheduler orchestrator
│   ├── channel_config.py      # Multi-channel configuration
│   ├── dom_automation.py      # Selenium DOM interactions
│   ├── schedule_tracker.py    # Schedule state management
│   └── content_generator.py   # Title/description templates
└── tests/
    ├── __init__.py
    └── test_scheduler.py
```

## Time Slot Strategy

| Slot | Japan Time | EST Time | Purpose |
|------|------------|----------|---------|
| 1    | 5:00 AM    | 3:00 PM  | US afternoon engagement |
| 2    | 11:00 AM   | 9:00 PM  | US prime time |
| 3    | 5:00 PM    | 3:00 AM  | Japan morning / EU |

## Usage

```python
from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import YouTubeShortsScheduler

# Initialize for a channel
scheduler = YouTubeShortsScheduler(channel="move2japan")

# Gather existing schedule
scheduler.gather_existing_schedule()

# Schedule unlisted videos
scheduler.run_scheduling_workflow(max_videos=10)
```

## DOM Selectors Reference

See `src/dom_automation.py` for comprehensive selector documentation:
- Page 1: Channel Content (Shorts List)
- Page 2: Video Details/Edit Page
- Page 3: Visibility/Scheduling Dialog

## CLI Usage (V0.5.0)

```bash
python main.py
# Select 1 (YouTube) → 6 (Shorts Scheduler)
# Options:
#   1. Enhance First Unlisted Short (Layer 1+2)
#   2. Dry Run (preview only)
#   3. Schedule First Unlisted Short (Layer 1+2+3)
```

## WRE Layer Stack

```
L0:   Select unlisted video
L1:   Open visibility dialog + expand schedule
L2:   Set DATE
L3:   Set TIME
L4:   Click Done → "Scheduled"
L5.1: Related Video modal
L5.2: Select video
L5.3: SAVE
L5.4: Return to list
L5.5: REFRESH (F5) ← CRITICAL before loop
```

## WSP Compliance

- WSP 3: Platform Integration domain
- WSP 22: ModLog documentation
- WSP 49: Standard module structure
- WSP 62: scripts/launch.py extraction
- WSP 80: DAE pattern for autonomous scheduling
- WSP 95: SKILLz.md for content enhancement

