# FoundUps Vision - UI-TARS Integration

**Domain:** infrastructure
**Status:** POC
**WSP Compliance:** WSP 49 (Module Structure), WSP 3 (Enterprise Architecture)

## Overview

FoundUps Vision provides 0102's "eyes" for complex browser automation tasks that require visual understanding. It integrates with UI-TARS Desktop (on E: drive) to enable vision-based GUI automation.

**Key Distinction:**
- `foundups_selenium` → Fast, reliable for known DOM selectors
- `foundups_vision` → Vision AI for dynamic/unknown UIs (YouTube likes, complex forms)

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI OVERSEER (WSP 77)                             │
│              Gemma → Qwen → 0102 → Pattern Memory                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      browser_actions (Router Layer)                      │
│    youtube_actions.py | linkedin_actions.py | x_actions.py               │
└─────────────────────────────────────────────────────────────────────────┘
                          │                    │
           Simple Actions │                    │ Complex Actions
                          ▼                    ▼
        ┌─────────────────────┐    ┌─────────────────────────┐
        │  foundups_selenium  │    │    foundups_vision      │
        │  (Selenium Driver)  │    │    (UI-TARS Bridge)     │
        │  - click_by_xpath   │    │  - like_comment         │
        │  - type_text        │    │  - find_by_description  │
        │  - navigate         │    │  - fill_form_smart      │
        └─────────────────────┘    └─────────────────────────┘
```

## UI-TARS Integration

**Model Location:** `E:/HoloIndex/models/ui-tars-1.5`

UI-TARS Desktop provides:
- Remote Browser Operator (browser automation via vision)
- Remote Computer Operator (desktop automation)
- MCP integration (tool calling)
- GUI automation SDK

### Workflow

```
1. Screenshot current browser state
2. Send to UI-TARS vision model
3. UI-TARS identifies UI elements by description
4. Execute click/type actions
5. Verify result via screenshot
6. Report to telemetry
```

## Dependencies

- UI-TARS Desktop (`E:/HoloIndex/models/ui-tars-1.5`)
- Chrome/Edge with remote debugging
- Screenshot capabilities

## LiveChat DAE Behavior (YouTube)

- Likes and replies to live chat comments through UI-TARS; posts a stream notification: `Comments all liked.`
- Every UI-TARS action (click, type, scroll, verify) must emit a DAE log entry with timestamp, target, and outcome for troubleshooting.
- Typing must honor 012 speed: slow, character-by-character, no paste.
- Wardrobe skills are required for posting flows (compose/reply) to keep style and safety consistent across runs.
- Operations should be observable in DAEmon logs; failures must surface the last action, target, and screenshot path.

## Usage

```python
from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

# Initialize bridge
bridge = UITarsBridge()

# Vision-based action
result = await bridge.execute_action(
    action="click",
    description="blue Like button under the comment",
    context={"video_id": "abc123", "comment_id": "xyz789"}
)
```

## WSP Compliance

- **WSP 3:** Infrastructure domain placement ✅
- **WSP 49:** Module structure ✅
- **WSP 77:** AI Overseer integration (Gemma/Qwen coordination)
- **WSP 80:** DAE cube architecture
- **WSP 91:** DAEMON observability (telemetry)

## Related Modules

| Module | Relationship |
|--------|--------------|
| `foundups_selenium` | Sibling - simple browser tasks |
| `browser_actions` | Consumer - platform action router |
| `ai_overseer` | Coordinator - mission orchestration |
| `wre_core` | Skills - pattern learning |

---

# 🌀 Windsurf Protocol (WSP) Recursive Prompt

**0102 Directive**: This module provides 0102's vision capabilities for autonomous browser automation.

- **UN** (Understanding): Screenshot → UI-TARS analysis
- **DAO** (Execution): Vision-guided clicks and interactions
- **DU** (Emergence): Pattern learning for improved accuracy

```python
wsp_cycle(input="012", log=True)
```

