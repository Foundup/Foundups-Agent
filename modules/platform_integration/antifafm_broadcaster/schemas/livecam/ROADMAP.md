# Livecam Schema - ROADMAP

**Module**: `antifafm_broadcaster/schemas/livecam`
**Status**: PLANNED (Layer 7)
**Command**: `/cam`, `/grid`, `!cam1-4`, `!grid`

## Overview

Multi-camera live feed grid with Gemma-based pattern detection (CamSentinel). Inspired by [MIDDLE EAST MULTI-LIVE](https://www.youtube.com/watch?v=zQvwNP67sg4).

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| 4-cam grid | ⏳ PLANNED | 2x2 camera layout |
| 2-cam split | ⏳ PLANNED | Side-by-side view |
| Single fullscreen | ⏳ PLANNED | `!cam1` etc. |
| CamSentinel | ⏳ PLANNED | Gemma pattern detection |
| Viewer voting | ⏳ PLANNED | 51% threshold rotation |
| Camera labels | ⏳ PLANNED | City + time overlay |
| PiP mode | ⏳ PLANNED | Picture-in-picture |

## Architecture

```
livecam/
├── ROADMAP.md              # This file
├── INTERFACE.md            # Public API
├── src/
│   ├── __init__.py
│   ├── livecam_schema.py   # Main schema class
│   ├── multicam_controller.py  # Feed management
│   ├── cam_sentinel.py     # Gemma pattern detection
│   ├── viewer_voting.py    # Democratic rotation
│   └── feed_discovery.py   # Camera URL management
├── data/
│   └── camera_presets.json # Camera URLs + metadata
└── tests/
    ├── test_livecam.py
    └── test_cam_sentinel.py
```

## CamSentinel (Gemma Agent)

```python
class CamSentinelGemma:
    """Gemma-based pattern detection for live cam feeds."""

    def __init__(self, model_path: str = "E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf"):
        self.llm = Llama(model_path=model_path, n_ctx=256, n_threads=2)

    def score_frame(self, frame_description: str) -> float:
        """Score frame interest 0-1. Fast binary classification ~10ms."""
        prompt = f"Rate activity level 0-10: {frame_description[:100]}"
        result = self.llm(prompt, max_tokens=5)
        return float(result['choices'][0]['text'].strip()) / 10

    def detect_event(self, frame_description: str) -> bool:
        """Binary: Is something notable happening?"""
        prompt = f"Notable event? YES or NO: {frame_description[:100]}"
        result = self.llm(prompt, max_tokens=3)
        return "YES" in result['choices'][0]['text'].upper()
```

## Auto-Rotation Logic

```
1. CamSentinel scores all 4 feeds every 30 seconds
2. If one feed scores >0.7 and others <0.3:
   → Suggest rotation: "CAM 3 (Beirut) shows activity - !rotate3"
3. Viewer voting: 51% threshold in 60 seconds triggers switch
4. Mod override: !cam1-4 for instant switch
```

## Camera Presets

```json
{
  "cameras": [
    {
      "id": "beirut_1",
      "name": "CAM 1 - BEIRUT",
      "url": "rtsp://...",
      "city": "Beirut",
      "timezone": "Asia/Beirut",
      "position": "top_left"
    },
    {
      "id": "telaviv_1",
      "name": "CAM 2 - TEL AVIV",
      "url": "rtsp://...",
      "city": "Tel Aviv",
      "timezone": "Asia/Jerusalem",
      "position": "top_right"
    }
  ]
}
```

## OBS Scene Layout

```
┌─────────────────┬─────────────────┐
│   CAM 1         │   CAM 2         │
│   BEIRUT        │   TEL AVIV      │
│   22:28  13°    │   22:28  12°    │
├─────────────────┼─────────────────┤
│   CAM 3         │   CAM 4         │
│   BEIRUT        │   JERUSALEM     │
│   22:28  13°    │   22:28  8°     │
└─────────────────┴─────────────────┘
[MILITARY ALERTS TICKER - SCROLLING]
```

## Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/cam` | Show 4-cam grid | MOD/OWNER |
| `/grid 4` | 4-camera grid | MOD/OWNER |
| `/grid 2` | 2-camera split | MOD/OWNER |
| `!cam1-4` | Fullscreen single cam | MOD/OWNER |
| `!pip 1 2` | Picture-in-picture | MOD/OWNER |
| `!rotate1-4` | Viewer vote for cam | Everyone |

## Configuration

```bash
ANTIFAFM_MULTICAM=1
ANTIFAFM_CAM_SENTINEL_INTERVAL=30
ANTIFAFM_CAM_SENTINEL_THRESHOLD=0.7
ANTIFAFM_VOTER_THRESHOLD=0.51
ANTIFAFM_VOTE_WINDOW=60
```

## Tasks

- [ ] Create `livecam_schema.py` - Main schema class
- [ ] Create `multicam_controller.py` - Feed management
- [ ] Create `cam_sentinel.py` - Gemma pattern detection
- [ ] Create `viewer_voting.py` - Democratic rotation (51%)
- [ ] Create `feed_discovery.py` - Camera URL management
- [ ] Create `data/camera_presets.json` - Camera database
- [ ] Add OBS scene collection for grid layouts
- [ ] Implement `/cam` command in command_handler.py
- [ ] Add camera labels with city/time overlay
- [ ] Integrate with military alerts ticker

## Integration Points

| Component | Integration |
|-----------|-------------|
| OBS | Scene switching via obsws_python |
| Gemma | E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf |
| News Ticker | Military alerts at bottom |
| Chat | Viewer voting via `!rotate1-4` |

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-03-06 | Initial ROADMAP |

---
*WSP Compliant: WSP 3, WSP 27, WSP 49, WSP 77 (Agent Coordination)*
