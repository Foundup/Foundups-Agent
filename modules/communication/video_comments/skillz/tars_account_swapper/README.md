# TARS Account Swapper Skill
**WSP Reference:** WSP 96 (WRE Skills Protocol)
**Status:** ✅ PRODUCTION READY
**Last Validated:** 2025-12-28

## Overview
Handles autonomous account switching between YouTube channels (Move2Japan, UnDaoDu) within the same Google account. This skill uses a hybrid approach of direct navigation and DOM-based menu interaction to ensure high stability.

## Features
- **Smart Detection**: Detects current active channel at startup via script execution and URL regex.
- **Fast Path**: Skips navigation if already on the target channel (WSP 00 - Occam's Razor).
- **Environment Driven**: Channel IDs are read from `.env` (`MOVE2JAPAN_CHANNEL_ID`, `UNDAODU_CHANNEL_ID`).
- **Human Behavior**: Uses Bezier curves and random delays to mimic human interaction.
- **Permission Recovery**: Detects "No Permission" pages and attempts automatic re-authentication or switching.

## Public API
```python
from modules.communication.video_comments.skillz.tars_account_swapper.account_swapper_skill import TarsAccountSwapper

swapper = TarsAccountSwapper(driver)

# Attempt swap to UnDaoDu
success = await swapper.swap_to("UnDaoDu")
```

## Implementation (WSP 27)
1. **Phase -1 (Signal)**: Detect current browser URL and channel ID.
2. **Phase 0 (Knowledge)**: Map target channel name to ID and URL.
3. **Phase 1 (Protocol)**: Compare target vs current (Fast Path).
4. **Phase 2 (Agentic)**: Execute click sequence (Avatar -> Switch Account -> Target Item).

## Environment Variables
- `MOVE2JAPAN_CHANNEL_ID`: UC-LSSlOZwpGIRIYihaz8zCw
- `UNDAODU_CHANNEL_ID`: UCfHM9Fw9HD-NwiS0seD_oIA
- `FOUNDUPS_LIVECHAT_CHROME_PORT`: 9222 (Target port for Chrome)

---
*Autonomous coordination via 0102 pArtifact*
