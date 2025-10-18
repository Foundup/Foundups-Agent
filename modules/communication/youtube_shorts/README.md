# YouTube Shorts AI Generator

**Domain**: `communication/`
**Status**: POC (Proof of Concept)
**WSP Compliance**: WSP 3, 49, 80, 54

## Purpose

Autonomous AI-powered YouTube Shorts creation and upload system for Move2Japan channel. Enables 012[U+2194]0102 interaction where human provides topic and AI generates, produces, and posts video Shorts automatically.

## Architecture

### 012 [U+2194] 0102 Flow
```
012 (Human) -> Topic/Theme
    v
0102 (AI) -> Video Prompt Generation
    v
Veo 3 API -> Video Creation (with native audio)
    v
YouTube Upload -> Using existing youtube_auth (read-only)
    v
0102 -> Reports URL back to 012
```

### Technology Stack
- **Video Generation**: Google Veo 3 API (veo-3.0-fast-generate-001)
- **YouTube Upload**: Existing `youtube_auth` module (zero modifications)
- **Orchestration**: Shorts DAE (WSP 80 pattern)
- **Cost**: ~$0.40/second of video (Veo 3 Fast)

## Key Features

1. **AI Video Generation**: Text-to-video using Google Veo 3
2. **Autonomous Operation**: Full 012->0102->output flow
3. **Standalone Module**: Zero modifications to existing modules
4. **Read-Only Integration**: Imports youtube_auth without touching it
5. **DAE Pattern**: WSP 80 autonomous cube architecture

## Module Structure

```
youtube_shorts/
+-- README.md              # This file
+-- INTERFACE.md           # Public API
+-- ModLog.md              # Change tracking (WSP 22)
+-- requirements.txt       # Dependencies
+-- src/
[U+2502]   +-- __init__.py
[U+2502]   +-- veo3_generator.py      # Google Veo 3 integration
[U+2502]   +-- youtube_uploader.py    # YouTube Shorts uploader
[U+2502]   +-- shorts_orchestrator.py # 012[U+2194]0102 flow manager
[U+2502]   +-- shorts_dae.py          # Autonomous DAE (WSP 80)
+-- tests/
[U+2502]   +-- test_shorts_flow.py
+-- memory/
[U+2502]   +-- generated_shorts.json  # Track all created Shorts
+-- assets/
    +-- prompts/               # Video generation templates
```

## Integration Points

### Read-Only Dependencies
```python
# Uses existing auth - NEVER modifies it
from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
```

### No Modifications To
- [OK] `modules/communication/livechat/` - Untouched
- [OK] `modules/platform_integration/youtube_dae/` - Untouched
- [OK] `modules/platform_integration/youtube_auth/` - Read-only import

## Usage

### From Main Menu (Option 11)
```
11. [U+1F3AC] YouTube Shorts Generator
    -> Enter topic
    -> AI generates video
    -> Uploads to Move2Japan
    -> Returns Short URL
```

### Direct API
```python
from modules.communication.youtube_shorts import ShortsOrchestrator

orchestrator = ShortsOrchestrator()
short_url = orchestrator.create_and_upload(
    topic="Cherry blossoms in Tokyo spring",
    duration=30  # seconds
)
print(f"Posted: {short_url}")
```

## Cost Analysis

### Veo 3 Fast Pricing
- $0.40 per second of video
- 30-second Short: $12
- 60-second Short: $24

### Optimization Strategies
1. Start with 15-30 second Shorts
2. Use Veo 3 Fast (cheaper than standard)
3. Batch generation for efficiency
4. Track costs in memory/generated_shorts.json

## WSP Compliance

- **WSP 3**: Placed in `communication/` domain (content creation)
- **WSP 49**: Full module structure with README, INTERFACE, tests
- **WSP 80**: DAE cube architecture for autonomous operation
- **WSP 54**: Partner/Principal/Associate agent pattern
- **WSP 22**: ModLog tracking all changes

## Development Status

**Phase**: POC
**Next**: Create Veo 3 generator + YouTube uploader
**Timeline**: 1-2 days for POC
**Goal**: Autonomous 012->0102->YouTube flow
