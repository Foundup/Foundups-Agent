# Karaoke Schema - ROADMAP

**Module**: `antifafm_broadcaster/schemas/karaoke`
**Status**: COMPLETE (lyrics cache), PARTIAL (live STT)
**Command**: `/karaoki`, `/lyrics`, `!karaoke`

## Overview

STT lyrics overlay with beat-synced text animation. Displays song lyrics synchronized with audio playback.

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Lyrics cache | ✅ COMPLETE | SQLite cache from whisper-stt |
| LRCLib lookup | ✅ COMPLETE | Fallback lyrics source |
| SRT overlay | ✅ COMPLETE | FFmpeg subtitles filter |
| Beat-sync pulse | ✅ COMPLETE | BPM-based fontsize animation |
| Live STT | ⏳ PLANNED | Real-time whisper transcription |

## Architecture

```
karaoke/
├── ROADMAP.md          # This file
├── INTERFACE.md        # Public API
├── src/
│   ├── __init__.py
│   ├── karaoke_schema.py
│   ├── lyrics_cache.py      # SQLite lyrics storage
│   └── stt_bridge.py        # Whisper STT integration
└── tests/
    └── test_karaoke.py
```

## FFmpeg Filter

```python
# With SRT subtitles
filter = "[1:v]scale=1920:1080,format=yuv420p[bg];"
filter += f"[bg]subtitles='{srt_path}':"
filter += f"force_style='FontSize={font_size},PrimaryColour=&H00FFFFFF,"
filter += f"OutlineColour=&H00000000,Outline=2,Shadow=1,Alignment=2,MarginV=80'"
filter += "[out]"

# Without SRT (placeholder)
bpm_freq = bpm / 60.0 * 6.28
fontsize_expr = f"{font_size}+10*sin(t*{bpm_freq:.4f})"
filter = f"[1:v]scale=1920:1080,format=yuv420p[bg];"
filter += f"[bg]drawtext=text='Karaoke Mode':fontsize='{fontsize_expr}'..."
```

## Lyrics Pipeline

```
1. Song plays on antifaFM
   ↓
2. Check lyrics_cache.db (SQLite)
   ↓
3. Cache HIT → Load SRT → FFmpeg overlay
   ↓
3. Cache MISS → Query LRCLib → Cache → SRT
   ↓
4. Still MISS → Show placeholder text
```

## Data Sources

| Source | Priority | API |
|--------|----------|-----|
| whisper-stt | 1 (pre-cached) | Local STT |
| lrclib | 2 (fallback) | lrclib.net API |
| genius | 3 (future) | Genius API |

## Configuration

```bash
ANTIFAFM_KARAOKE_FONT_SIZE=48
ANTIFAFM_KARAOKE_BPM=120
ANTIFAFM_LYRICS_CACHE_PATH=data/lyrics_cache.db
```

## Tasks

- [x] Implement lyrics SQLite cache
- [x] Integrate LRCLib API fallback
- [x] Create SRT generator from timed lyrics
- [x] Add beat-sync fontsize animation
- [ ] Add live STT with faster-whisper
- [ ] Add word-level highlighting
- [ ] Add color transitions per verse

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-05 | Lyrics cache + SRT overlay |
| 1.1.0 | 2026-03-05 | LRCLib fallback |
| 1.2.0 | 2026-03-06 | Beat-sync animation |

---
*WSP Compliant: WSP 3, WSP 27, WSP 49*
