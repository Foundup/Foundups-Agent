# Implementation Plan: Live Chat Daemon Monitoring
**Created**: 2025-10-20 | **Status**: Ready to Execute

## Current State (What EXISTS)

### ✓ AI Overseer Module
- **Location**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`
- **Status**: Production with `monitor_daemon()` method (line 693)
- **WSP 77 Coordination**: 4-phase workflow implemented
- **Mission Types**: DAEMON_MONITORING, BUG_DETECTION, AUTO_REMEDIATION added

### ✓ Daemon Monitor Skill
- **Location**: `modules/communication/livechat/skills/youtube_daemon_monitor.json`
- **Version**: v2.0.0 with WSP 15 MPS scoring
- **Patterns**: 6 error patterns (unicode, oauth, duplicate, quota, stream_not_found, livechat)

### ✓ Live Daemon Running
- **Bash ID**: 56046d (YouTube daemon --no-lock)
- **Unicode Patterns Found**: `[U+1F310]`, `[U+1F30D]`, `[U+2600]`, `[U+2744]`, etc.
- **Status**: LIVE and generating detectable patterns

### ✓ ChatSender Module
- **Location**: `modules/communication/livechat/src/chat_sender.py`
- **Interface**: `async send_message(text, response_type, skip_delay)`
- **Features**: Rate limiting, emoji support, 200 char truncation

### ✓ Banter Engine
- **Location**: `modules/ai_intelligence/banter_engine/src/banter_engine.py`
- **Method**: `_convert_unicode_tags_to_emoji(text)`
- **Function**: Converts `[U+XXXX]` → actual emoji

## What's MISSING (TODOs)

### ❌ BashOutput Integration (Line 786)
```python
def _read_bash_output(self, bash_id: str, lines: int = 100) -> Optional[str]:
    # TODO: Integrate with actual BashOutput tool
    logger.warning("[BASH-READ] BashOutput integration not yet implemented")
    return None  # ← PLACEHOLDER
```

### ❌ Live Chat Announcements (012's Vision!)
- No `chat_sender` parameter in `monitor_daemon()` signature
- No announcement method exists
- No integration with ChatSender

### ❌ Auto-Fix Application (Line 834)
```python
def _apply_auto_fix(self, bug: Dict, skill: Dict) -> Dict:
    # Placeholder for WRE integration
    return {"success": True, "bug": bug["pattern_name"], "fix_applied": bug.get("fix_action")}
```

## Implementation Tasks

### Task 1: Implement `_read_bash_output()`
**File**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py:786`

**Change**:
```python
def _read_bash_output(self, bash_id: str, lines: int = 100) -> Optional[str]:
    """Read recent output from bash shell using BashOutput tool"""
    try:
        # Use BashOutput tool from Claude Code environment
        from tools import BashOutput  # If available in module context
        output = BashOutput(bash_id)
        return output.get("stdout", "")
    except Exception as e:
        logger.error(f"[BASH-READ] Failed to read bash {bash_id}: {e}")
        return None
```

**Status**: BLOCKED - Need to understand how to call BashOutput from Python module
**Alternative**: Pass bash_output as parameter instead of bash_id

### Task 2: Add ChatSender Integration
**File**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py:693`

**Change 1 - Update signature**:
```python
def monitor_daemon(
    self,
    bash_id: str,
    skill_path: Path,
    auto_fix: bool = True,
    report_complex: bool = True,
    chat_sender: Optional[Any] = None,  # NEW PARAMETER
    announce_to_chat: bool = True        # NEW PARAMETER
) -> Dict[str, Any]:
```

**Change 2 - Add announcement method**:
```python
async def _announce_to_chat(
    self,
    chat_sender,
    phase: str,
    detection: Dict,
    fix_result: Optional[Dict] = None
):
    """Post autonomous fix announcements to live chat"""
    from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine

    banter = BanterEngine(emoji_enabled=True)

    # Generate announcement based on phase
    if phase == "detection":
        error_type = detection["pattern_name"].replace("_", " ").title()
        priority = detection.get("wsp_15_mps", {}).get("priority", "P?")
        message = f"012 detected {error_type} [{priority}] [U+1F50D]"

    elif phase == "applying":
        message = "012 applying fix, restarting MAGAdoom [U+1F527]"

    elif phase == "complete":
        if fix_result.get("success"):
            message = "012 fix verified - MAGAdoom online [U+2714]"
        else:
            message = "012 fix failed - creating bug report [U+26A0]"

    # Render emoji
    rendered = banter._convert_unicode_tags_to_emoji(message)

    # Post to chat
    await chat_sender.send_message(rendered, response_type='update')
```

**Change 3 - Integrate into workflow**:
```python
# Phase 3 (0102): Execute fixes or generate reports
for bug in classified_bugs:
    # Announce detection
    if chat_sender and announce_to_chat:
        await self._announce_to_chat(chat_sender, "detection", bug)

    if bug["auto_fixable"] and auto_fix:
        # Announce fix application
        if chat_sender and announce_to_chat:
            await self._announce_to_chat(chat_sender, "applying", bug)

        # Apply fix
        fix_result = self._apply_auto_fix(bug, skill)

        # Announce completion
        if chat_sender and announce_to_chat:
            await self._announce_to_chat(chat_sender, "complete", bug, fix_result)
```

### Task 3: Make `monitor_daemon()` Async
**File**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py:693`

**Change**:
```python
async def monitor_daemon(...) -> Dict[str, Any]:  # Add 'async'
    ...
```

**Reason**: ChatSender.send_message() is async

## Testing Plan

### Test 1: BashOutput Integration
```python
from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer
from pathlib import Path

overseer = AIIntelligenceOverseer(Path("O:/Foundups-Agent"))

# Test with live bash (manual bash_output for now)
bash_output = """
2025-10-20 15:07:03,735 - INFO - [U+1F310] NO-QUOTA mode
2025-10-20 15:07:04,541 - INFO - [U+1F30D] Evaluating global state
"""

# Pass as parameter instead of reading from bash
results = overseer.monitor_daemon_with_output(
    bash_output=bash_output,
    skill_path=Path("modules/communication/livechat/skills/youtube_daemon_monitor.json")
)

print(f"Bugs detected: {results['bugs_detected']}")
```

### Test 2: Live Chat Announcements
```python
import asyncio
from modules.communication.livechat.src.chat_sender import ChatSender

# Get YouTube service and chat_id from running daemon
chat_sender = ChatSender(youtube_service, live_chat_id)

# Run monitoring with announcements
results = await overseer.monitor_daemon(
    bash_id="56046d",  # Live YouTube daemon
    skill_path=Path("modules/communication/livechat/skills/youtube_daemon_monitor.json"),
    chat_sender=chat_sender,
    announce_to_chat=True
)
```

**Expected Output in UnDaoDu's chat**:
```
[15:35:22] 012 detected Unicode Error [P1] 🔍
[15:35:22] 012 applying fix, restarting MAGAdoom 🔧
[15:35:23] 012 fix verified - MAGAdoom online ✓
```

## Simplified Approach (Minimum Viable)

**Skip BashOutput integration initially** - just pass bash output as string:

```python
def monitor_daemon_with_output(
    self,
    bash_output: str,               # Pass output directly
    skill_path: Path,
    chat_sender: Optional[Any] = None,
    announce_to_chat: bool = True
) -> Dict[str, Any]:
    """Monitor daemon using provided bash output"""
    # ... same logic but use bash_output parameter
```

This allows testing the full workflow WITHOUT solving the BashOutput integration problem.

## Next Step

**DECISION NEEDED**:
1. Implement simplified version (bash_output as parameter) first?
2. Or solve BashOutput integration and implement full version?

**Recommendation**: Start with simplified version to prove the live chat announcements work, then add BashOutput integration later.

---
**WSP Compliance**: WSP 50 (Pre-Action), WSP 22 (ModLog), WSP 77 (Agent Coordination)
