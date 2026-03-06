# Video Loop Schema - ROADMAP

**Module**: `antifafm_broadcaster/schemas/video_loop`
**Status**: COMPLETE
**Command**: `/video`, `!grid`

## Overview

Background video loop with optional color pulse effect. The foundational visual layer for antifaFM streaming.

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Video loop | ✅ COMPLETE | Loop MP4/WebM infinitely |
| Color pulse | ✅ COMPLETE | Hue shift effect |
| Scale/pad | ✅ COMPLETE | Fit to 1920x1080 |
| Video library | ✅ COMPLETE | Registry + rotation |
| OBS rotation | ✅ COMPLETE | stream_orchestrator.py |

## Architecture

```
video_loop/
├── ROADMAP.md          # This file
├── INTERFACE.md        # Public API
├── src/
│   ├── __init__.py
│   └── video_loop_schema.py
└── tests/
    └── test_video_loop.py
```

## FFmpeg Filter

```python
filter = "[1:v]scale=1920:1080:force_original_aspect_ratio=decrease"
filter += ",pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
if color_pulse:
    filter += ",hue=h=sin(t*0.1)*15"
filter += ",format=yuv420p[out]"
```

## Integration

- **Video Library**: `src/video_library.py` manages video registry
- **OBS Rotation**: `src/stream_orchestrator.py` rotates on song change
- **CLI**: YouTube menu → antifaFM → Schema options

## Configuration

```bash
ANTIFAFM_DEFAULT_VISUAL=path/to/video.mp4
ANTIFAFM_FX_COLOR_PULSE=true
```

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-26 | Initial implementation |
| 1.1.0 | 2026-03-06 | OBS rotation via stream_orchestrator |

---
*WSP Compliant: WSP 3, WSP 27, WSP 49*
