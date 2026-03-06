# antifaFM Visual Output Schemas

Modular schema architecture for antifaFM broadcaster visual outputs.

**Version**: 3.0.0 (2026-03-06)

## Overview

Each schema is a self-contained module with its own ROADMAP.md, implementation, and tests. This enables independent expansion without monolithic growth.

## Available Schemas

| Schema | Status | Mode | Commands | Description |
|--------|--------|------|----------|-------------|
| [video_loop](video_loop/) | COMPLETE | FFMPEG | `/video` | Background video with color pulse |
| [karaoke](karaoke/) | COMPLETE | FFMPEG | `/karaoki` | STT lyrics with beat-sync |
| [entangled](entangled/) | COMPLETE | FFMPEG | `/entangled`, `/0102` | Bell state 0102 visualization |
| [waveform](waveform/) | COMPLETE | FFMPEG | `/waveform` | Audio waveform |
| [spectrum](spectrum/) | COMPLETE | FFMPEG | `/spectrum` | Frequency spectrum |
| [news_ticker](news_ticker/) | PARTIAL | FFMPEG | `/news` | RSS headline ticker |
| [livecam](livecam/) | PLANNED | OBS | `/cam`, `/grid` | Multi-camera + CamSentinel |

## Quick Start

```python
from modules.platform_integration.antifafm_broadcaster.schemas import (
    SchemaType, get_schema_by_name, list_schemas
)

# List all registered schemas
print(list_schemas())
# {'video_loop': True, 'karaoke': True, ...}

# Get and instantiate a schema
KaraokeSchema = get_schema_by_name("karaoke")
karaoke = KaraokeSchema()

# Build FFmpeg filter
filter_str = karaoke.build_ffmpeg_filter()
```

## Architecture

```
schemas/
├── README.md           # This file
├── __init__.py         # Registry with auto-import
├── base.py             # BaseSchema ABC + dataclasses
│
├── video_loop/
│   ├── __init__.py     # VideoLoopSchema + registration
│   ├── ROADMAP.md      # Schema-specific roadmap
│   └── tests/
│
├── karaoke/
│   ├── __init__.py     # KaraokeSchema + registration
│   ├── ROADMAP.md
│   └── tests/
│
├── entangled/
│   ├── __init__.py     # EntangledSchema (0102 Bell state)
│   ├── ROADMAP.md
│   └── tests/
│
├── waveform/
│   ├── __init__.py     # WaveformSchema
│   ├── ROADMAP.md
│   └── tests/
│
├── spectrum/
│   ├── __init__.py     # SpectrumSchema
│   ├── ROADMAP.md
│   └── tests/
│
├── news_ticker/
│   ├── __init__.py     # NewsTickerSchema
│   ├── ROADMAP.md
│   └── tests/
│
└── livecam/
    ├── __init__.py     # LivecamSchema (Layer 7)
    ├── ROADMAP.md
    └── tests/
```

## BaseSchema Interface

All schemas inherit from `BaseSchema`:

```python
from .base import BaseSchema, SchemaMode, SchemaConfig

class MySchema(BaseSchema):
    NAME = "my_schema"
    DISPLAY_NAME = "My Schema"
    DESCRIPTION = "Description here"
    MODE = SchemaMode.FFMPEG  # or OBS, HYBRID

    def build_ffmpeg_filter(self) -> str:
        """Build FFmpeg filter_complex string."""
        return "[1:v]scale=1920:1080[out]"

    def get_obs_scene(self) -> Optional[OBSSceneConfig]:
        """Return OBS scene config (for OBS/HYBRID mode)."""
        return None
```

## Schema Modes

| Mode | Description | Example |
|------|-------------|---------|
| `FFMPEG` | Pure FFmpeg filter (headless) | video_loop, karaoke |
| `OBS` | OBS scene control | livecam |
| `HYBRID` | FFmpeg + OBS overlays | Future |

## Registration

Schemas auto-register when their module is imported:

```python
# In schema module's __init__.py
from .. import register_schema, SchemaType

class MySchema(BaseSchema):
    ...

register_schema(SchemaType.MY_SCHEMA, MySchema)
```

## SchemeManager Integration

The `SchemeManager` automatically uses modular schemas:

```python
from ..src.scheme_manager import SchemeManager, OutputScheme

manager = SchemeManager()
manager.set_scheme(OutputScheme.KARAOKE)

# Uses modular schema (falls back to legacy if not found)
filter_str = manager.build_ffmpeg_filter()

# Access schema instance directly
karaoke = manager.get_modular_schema("karaoke")
if karaoke:
    karaoke.set_srt('/path/to/lyrics.srt')
```

## Adding a New Schema

1. Create directory: `schemas/my_schema/`
2. Create `__init__.py` with schema class
3. Add `SchemaType.MY_SCHEMA` to `schemas/__init__.py`
4. Add import to `schemas/__init__.py`
5. Create `ROADMAP.md` with schema-specific roadmap
6. Create `tests/` directory

## WSP Compliance

- **WSP 3**: Module Organization (schemas as sub-modules)
- **WSP 11**: Interface Protocol (BaseSchema contract)
- **WSP 27**: Universal DAE Architecture
- **WSP 49**: Module Structure (ROADMAP.md per schema)
- **WSP 72**: Module Independence (schemas don't cross-depend)
- **WSP 84**: Code Reuse (shared base + registry)

## Related Documentation

- [Main ROADMAP](../ROADMAP.md) - Overall broadcaster roadmap
- [INTERFACE](../INTERFACE.md) - Public API specification
- [ModLog](../ModLog.md) - Change history
