# Boot Layer Rotator Skill

## Purpose
Master schema rotation controller for antifaFM stream visuals. Cycles through different visual schemas every 10 minutes, with each schema having its own 2-minute internal view rotation.

## Schemas

| Schema | Status | Description |
|--------|--------|-------------|
| **gcc** | ✓ Implemented | Strait of Hormuz shipping tracker |
| **video** | ✓ Implemented | Curated video playlist |
| **news** | ✓ Implemented | Live news headlines |
| **chess** | ○ Coming Soon | Chess matches and puzzles |
| **checkers** | ○ Coming Soon | Classic checkers gameplay |
| **cams** | ○ Coming Soon | Global webcam feeds |
| **karaoke** | ○ Coming Soon | Song lyrics sing-along |
| **weather** | ○ Coming Soon | Weather visualization |
| **crypto** | ○ Coming Soon | BTC/ETH price charts |

## Rotation Cycle

```
10 min    10 min    10 min    10 min
┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
│ GCC │ → │VIDEO│ → │NEWS │ → │CHESS│ → ...
└─────┘   └─────┘   └─────┘   └─────┘
  ↓
2m Hormuz
2m Gulf
2m Tankers
(repeat)
```

## Commands

```bash
# Start rotation daemon
python executor.py --daemon

# List available schemas
python executor.py --list

# Skip to specific schema
python executor.py --skip-to chess

# Pause rotation (stakeholder control)
python executor.py --override

# Resume rotation
python executor.py --clear
```

## Fallback Behavior

When a schema is not implemented or fails to load:
- Shows "Coming Soon" splash screen
- Displays schema name + "0102🦞" signature
- Animated gradient background
- Continues rotation after 10 minutes

## Stakeholder/Delegate Control

- **Override**: Pause all rotation (manual control mode)
- **Skip-to**: Jump to specific schema immediately
- **Clear**: Resume automatic rotation

## OBS Setup

Requires browser source named `BootLayer_Browser` in OBS scene.

## WSP Compliance
- WSP 27: Universal DAE Architecture
- WSP 103: CLI Interface Standard
