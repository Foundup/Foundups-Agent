# Spectrum Schema - ROADMAP

**Module**: `antifafm_broadcaster/schemas/spectrum`
**Status**: COMPLETE
**Command**: `/spectrum`, `/freq`, `!spectrum`

## Overview

Frequency spectrum visualization using FFmpeg showfreqs filter. Displays audio frequency distribution in real-time.

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Spectrum display | COMPLETE | showfreqs FFmpeg filter |
| Multiple modes | COMPLETE | bar, line |
| Log frequency scale | COMPLETE | Logarithmic distribution |
| Multi-color gradient | COMPLETE | RGB color spectrum |
| antifaFM branding | COMPLETE | Logo overlay |

## Architecture

```
spectrum/
├── ROADMAP.md          # This file
├── __init__.py         # SpectrumSchema class
└── tests/
    └── test_spectrum.py
```

## FFmpeg Filter

```python
# Frequency spectrum visualization
mode = 'bar'  # Bar chart mode
colors = '0xff0000|0x00ff00|0x0000ff'  # RGB gradient
rate = 30
fscale = 'log'  # Logarithmic frequency scale

filter = f"color=c=black:s=1920x1080:r={rate}[bg];"
filter += f"[0:a]showfreqs=s=1920x540:mode={mode}:colors={colors}:fscale={fscale}[spec];"
filter += f"[bg][spec]overlay=0:270[prefmt];"
filter += f"[prefmt]drawtext=text='antifaFM':fontsize=36:fontcolor=white@0.7:"
filter += f"x=20:y=20:shadowcolor=black@0.5:shadowx=2:shadowy=2[prefinal];"
filter += f"[prefinal]format=yuv420p[out]"
```

## Spectrum Modes

| Mode | Description |
|------|-------------|
| bar | Vertical bars (default) |
| line | Connected line |

## Frequency Scale

| Scale | Description |
|-------|-------------|
| log | Logarithmic (default) - better for music |
| lin | Linear |

## Configuration

```bash
ANTIFAFM_SPECTRUM_MODE=bar
ANTIFAFM_SPECTRUM_COLORS=0xff0000|0x00ff00|0x0000ff
ANTIFAFM_SPECTRUM_RATE=30
ANTIFAFM_SPECTRUM_FSCALE=log
```

## Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/spectrum` | Switch to spectrum schema | MOD/OWNER |
| `/freq` | Alias for spectrum | MOD/OWNER |

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-06 | Initial modular implementation |

---
*WSP Compliant: WSP 3, WSP 27, WSP 49*
