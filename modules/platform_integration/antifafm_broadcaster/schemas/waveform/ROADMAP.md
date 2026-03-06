# Waveform Schema - ROADMAP

**Module**: `antifafm_broadcaster/schemas/waveform`
**Status**: COMPLETE
**Command**: `/waveform`, `/wave`, `!waveform`

## Overview

Audio waveform visualization using FFmpeg showwaves filter. Real-time audio-reactive visuals.

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Waveform display | COMPLETE | showwaves FFmpeg filter |
| Multiple modes | COMPLETE | cline, line, point, p2p, scale |
| Color config | COMPLETE | Multi-color waveform |
| antifaFM branding | COMPLETE | Logo overlay |

## Architecture

```
waveform/
├── ROADMAP.md          # This file
├── __init__.py         # WaveformSchema class
└── tests/
    └── test_waveform.py
```

## FFmpeg Filter

```python
# Waveform visualization
mode = 'cline'  # Connected line mode
colors = '0xff0000|0xffffff'  # Red/white
rate = 30

filter = f"color=c=black:s=1920x1080:r={rate}[bg];"
filter += f"[0:a]showwaves=s=1920x540:mode={mode}:colors={colors}:rate={rate}[wave];"
filter += f"[bg][wave]overlay=0:270[prefmt];"
filter += f"[prefmt]drawtext=text='antifaFM':fontsize=36:fontcolor=white@0.7:"
filter += f"x=20:y=20:shadowcolor=black@0.5:shadowx=2:shadowy=2[prefinal];"
filter += f"[prefinal]format=yuv420p[out]"
```

## Waveform Modes

| Mode | Description |
|------|-------------|
| cline | Connected line (default) |
| line | Vertical lines |
| point | Points only |
| p2p | Point-to-point |
| scale | Vertical bars |

## Configuration

```bash
ANTIFAFM_WAVEFORM_MODE=cline
ANTIFAFM_WAVEFORM_COLORS=0xff0000|0xffffff
ANTIFAFM_WAVEFORM_RATE=30
```

## Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/waveform` | Switch to waveform schema | MOD/OWNER |
| `/wave` | Alias for waveform | MOD/OWNER |

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-06 | Initial modular implementation |

---
*WSP Compliant: WSP 3, WSP 27, WSP 49*
