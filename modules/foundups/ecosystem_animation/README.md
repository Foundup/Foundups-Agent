# Ecosystem Animation Module

**Location**: `modules/foundups/ecosystem_animation/`
**Type**: Visual Animation (Frontend)
**WSP**: 49 (Module Structure)

## Overview

Interactive 10-year ecosystem growth animation for the pAVS Litepaper. Shows the ecosystem expanding visually without relying on numbers - the visual speaks for itself.

## Visual Language

| Metric | Visual Representation |
|--------|----------------------|
| BTC Reserve | Central glowing orb (size = reserve) |
| FoundUps | Orbiting particles (density = count) |
| Revenue Flow | Particles streaming INTO core |
| Health | Color gradient (green = thriving) |
| Milestones | Burst effects (fireworks) |

## Usage

### Web (Static)

```html
<canvas id="ecosystemCanvas"></canvas>
<script src="js/ecosystem-growth.js"></script>
<script>
    EcosystemGrowth.init('ecosystemCanvas');
</script>
```

### Interactive Controls

- **Timeline Slider**: Drag Y0-Y10 to see growth
- **Scenario Buttons**: Conservative / Baseline / OpenClaw
- **Auto-Play**: Click Play to animate full 10 years

## File Locations

| File | Purpose |
|------|---------|
| `public/ecosystem.html` | Entry HTML |
| `public/js/ecosystem-growth.js` | Animation code (~500 lines) |
| `public/data/ten_year_projection.json` | Data source |

## Data Flow

```
ten_year_projection.py → ten_year_projection.json → ecosystem-growth.js → Canvas
```

## Layers (Occam's Approach)

1. **Static Core**: Glowing orb representing BTC reserve
2. **Timeline Slider**: User controls year (0-10)
3. **Particle System**: FoundUps as orbiting particles
4. **Revenue Flow**: Fee particles flowing into core
5. **Milestone Bursts**: Celebration effects at key events
6. **Scenario Switcher**: Compare growth paths

## Related Modules

- `simulator/economics/ten_year_projection.py`: Data generator
- `public/js/foundup-cube.js`: Sibling animation (cube lifecycle)

## Screenshots

*See live at: https://foundups.ai/ecosystem.html*
