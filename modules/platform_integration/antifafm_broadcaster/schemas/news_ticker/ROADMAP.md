# News Ticker Schema - ROADMAP

**Module**: `antifafm_broadcaster/schemas/news_ticker`
**Status**: PARTIAL (basic ticker), PLANNED (military alerts)
**Command**: `/news`, `!news`, `!ticker`

## Overview

Scrolling news ticker with RSS aggregation. Enhanced version includes military alerts categorization inspired by MIDDLE EAST MULTI-LIVE.

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Basic ticker | ✅ COMPLETE | Scrolling text overlay |
| Headlines queue | ✅ COMPLETE | NewsOrchestrator |
| RSS aggregation | ⏳ PLANNED | Multi-source feeds |
| Military alerts | ⏳ PLANNED | Categorized headlines |
| AI classification | ⏳ PLANNED | Gemma category detection |
| Source badges | ⏳ PLANNED | Colored source indicators |

## Architecture

```
news_ticker/
├── ROADMAP.md              # This file
├── INTERFACE.md            # Public API
├── src/
│   ├── __init__.py
│   ├── ticker_schema.py    # Main schema class
│   ├── military_alerts.py  # Enhanced RSS (Layer 7)
│   └── rss_aggregator.py   # Feed fetching
├── data/
│   └── news_sources.json   # RSS feed config
└── tests/
    └── test_news_ticker.py
```

## FFmpeg Filter

```python
# Scrolling ticker
speed = 100  # pixels per second
font_size = 36
filter = "[1:v]scale=1920:1080,format=yuv420p[bg];"
filter += f"[bg]drawtext=text='{text}':"
filter += f"fontsize={font_size}:fontcolor=white:"
filter += f"x=w-mod(t*{speed}\\,w+tw):y=h-50:"
filter += f"shadowcolor=black:shadowx=2:shadowy=2[out]"
```

## Military Alerts Categories

```
MILITARY ALERTS | MISSILES | DRONES | SHELLING | AIRSPACE | NOTAMS | NAVAL |
AIR-FORCE | NATO | US MILITARY | DEPLOYMENTS | MOBILIZATION | EXERCISES |
AID | TALKS | SANCTIONS | SUMMIT | CEASEFIRE
```

## News Sources

```json
{
  "sources": [
    {
      "id": "shephard",
      "name": "SHEPHARD",
      "url": "https://shephard.com/rss",
      "categories": ["MILITARY ALERTS", "DEPLOYMENTS"],
      "badge_color": "#4CAF50"
    },
    {
      "id": "reuters_world",
      "name": "REUTERS",
      "url": "https://feeds.reuters.com/Reuters/worldNews",
      "categories": ["AID", "TALKS", "SANCTIONS"],
      "badge_color": "#FF9800"
    }
  ]
}
```

## AI Classification (Gemma)

```python
def classify_headline(headline: str) -> str:
    """Classify headline into military alert category."""
    prompt = f"""Classify this headline into ONE category:
MISSILES, DRONES, SHELLING, AIRSPACE, NAVAL, DEPLOYMENTS,
SANCTIONS, TALKS, CEASEFIRE, OTHER

Headline: {headline}
Category:"""
    result = gemma(prompt, max_tokens=10)
    return result.strip().upper()
```

## Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/news` | Switch to news ticker schema | MOD/OWNER |
| `/news top` | Show top 3 headlines | MOD/OWNER |
| `/ticker on/off` | Toggle ticker overlay | MOD/OWNER |

## Configuration

```bash
ANTIFAFM_TICKER_ENABLED=true
ANTIFAFM_TICKER_SPEED=100
ANTIFAFM_TICKER_CATEGORIES=all  # or comma-separated
ANTIFAFM_TICKER_SOURCES=all     # or comma-separated
ANTIFAFM_TICKER_REFRESH=300     # seconds
```

## Tasks

- [x] Implement basic scrolling ticker
- [x] Create NewsOrchestrator for headline queue
- [ ] Create `rss_aggregator.py` - Multi-source fetching
- [ ] Create `military_alerts.py` - Category classification
- [ ] Add Gemma AI classification
- [ ] Create `data/news_sources.json` - Feed config
- [ ] Add source badges with colors
- [ ] Add headline deduplication
- [ ] Add time-ago display

## Integration Points

| Component | Integration |
|-----------|-------------|
| AI Overseer | `skillz/agentic_news_ticker/` for AI headlines |
| Livecam | Military alerts ticker at bottom of grid |
| Headlines DB | SQLite cache for deduplication |

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-01 | Basic scrolling ticker |
| 1.1.0 | 2026-03-06 | NewsOrchestrator queue |
| 0.2.0 | TBD | Military alerts categories |

---
*WSP Compliant: WSP 3, WSP 27, WSP 49*
