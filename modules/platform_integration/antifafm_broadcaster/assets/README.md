# antifaFM Broadcaster - Assets

Visual assets for Layer 1 (static) and Layer 2.5 (animated effects).

## Directory Structure

```
assets/
├── README.md                 # This file
├── default_visual.png        # Layer 1: Static background (auto-generated if missing)
├── backgrounds/              # Layer 2.5: Image cycling library
│   └── (add 5-10 branded images here)
└── overlays/                 # Layer 2.5: Animated GIF overlays
    └── antifafm_pulse.gif    # Logo pulse animation
```

## Layer 1: Static Image

**File**: `default_visual.png`

- Resolution: 1920x1080 (16:9)
- Format: PNG (or JPEG)
- Auto-generated with "antifaFM" text if missing

## Layer 2.5: Visual Effects Assets

### Background Images (`backgrounds/`)

For image cycling effect. Add branded images here.

**Requirements**:
- Resolution: 1920x1080 (or larger, will be scaled)
- Format: PNG, JPEG, or WEBP
- Naming: Sequential preferred (`bg_01.png`, `bg_02.png`, etc.)
- Quantity: 5-10 images recommended for variety

**Enable via ENV**:
```bash
ANTIFAFM_FX_IMAGE_CYCLE=true
ANTIFAFM_FX_IMAGE_DIR=modules/platform_integration/antifafm_broadcaster/assets/backgrounds/
```

### GIF Overlays (`overlays/`)

For animated overlay in corner of stream.

**Requirements**:
- Resolution: 150-200px (will be scaled)
- Format: GIF (animated)
- Transparency: Supported
- Loop: Seamless

**Create default GIF programmatically**:
```python
from modules.platform_integration.antifafm_broadcaster.src.visual_effects import create_default_gif
from pathlib import Path

gif_path = Path("assets/overlays/antifafm_pulse.gif")
create_default_gif(gif_path, text="antifaFM")
```

**Enable via ENV**:
```bash
ANTIFAFM_FX_GIF_OVERLAY=true
ANTIFAFM_FX_GIF_PATH=modules/platform_integration/antifafm_broadcaster/assets/overlays/antifafm_pulse.gif
```

## Creating Assets with FFmpeg

### Generate Placeholder Background
```bash
ffmpeg -f lavfi -i "color=c=black:s=1920x1080:d=1" \
  -vf "drawtext=text='antifaFM':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" \
  -frames:v 1 default_visual.png
```

### Generate Pulsing GIF
```bash
ffmpeg -f lavfi -i "color=c=black@0:s=200x200:d=3:r=15" \
  -vf "drawtext=text='antifaFM':fontsize=24:fontcolor=white@'0.5+0.5*sin(t*3)':x=(w-text_w)/2:y=(h-text_h)/2" \
  -gifflags +transdiff -loop 0 overlays/antifafm_pulse.gif
```

## Brand Guidelines

When creating antifaFM assets:
- Colors: Red (#FF0000), Black (#000000), White (#FFFFFF)
- Style: Bold, anti-fascist imagery
- Text: Sans-serif fonts preferred
- Content: Music-focused, political solidarity themes
