# Git → Social Media Event-Driven Architecture

**Date**: 2025-11-29
**Session**: Architecture Deep Dive - 0102 Event Queue Integration
**User Request**: "shouldn't 0102 push to queue, that then AI_overseer monitors and then agentically decides what to do with it... use the occums the existing modules..."

---

## Architecture Discovery

### Existing Modules Mapped

#### 1. GitPushDAE (Autonomous Daemon)
**File**: `modules/infrastructure/git_push_dae/src/git_push_dae.py`

**Status**: OPERATIONAL - Autonomous daemon following WSP 91

**Architecture**:
```python
class GitPushDAE:
    def start_daemon(self):
        """Runs monitoring_cycle() every 5 minutes (check_interval=300)"""
        while not self.stop_event.is_set():
            self.monitoring_cycle()
            self.stop_event.wait(self.check_interval)

    def monitoring_cycle(self):
        """Main loop: gather context → make decision → execute push"""
        context = self._gather_push_context()  # git status, quality, timing
        decision = self.make_push_decision(context)  # 7 agentic criteria
        if decision.should_push:
            self._execute_push(decision, context)  # Calls GitLinkedInBridge
```

**Current Integration**: Calls `GitLinkedInBridge.push_and_post()` directly (OLD unified interface)

**Gap**: Only works for AUTONOMOUS commits. Manual commits bypass this daemon entirely.

---

#### 2. HoloDAE (Code Intelligence Daemon)
**File**: `holo_index/qwen_advisor/holodae_coordinator.py`, `autonomous_holodae.py`

**Status**: OPERATIONAL - Background monitoring with WRE triggers

**Architecture**:
```python
class HoloDAECoordinator:
    def _monitoring_loop(self):
        """Background thread monitoring file changes"""
        while not self.monitoring_stop_event.is_set():
            result = self._run_monitoring_cycle()  # Detect file changes

            if result.has_actionable_events():
                wre_triggers = self._check_wre_triggers(result)  # WSP 96 v1.3
                if wre_triggers:
                    self._execute_wre_skills(wre_triggers)

            self.monitoring_stop_event.wait(self.monitoring_interval)
```

**Current Integration**: Monitors file changes, executes WRE skills for code quality

**Gap**: No git commit event detection or social media integration

---

#### 3. AI Overseer (MCP Coordinator)
**File**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`, `mcp_integration.py`

**Status**: OPERATIONAL - Qwen + Gemma + 0102 mission coordination

**Architecture**:
```python
class AIOverseerMCPIntegration:
    def __init__(self):
        # Event queue for async MCP communication (line 100)
        self.event_queue: asyncio.Queue = asyncio.Queue()

        # Rubik DAE MCP servers configured
        self.servers = {
            "compose": MCPServer(tools=["read_file", "git_commit"]),
            "build": MCPServer(tools=["docker_build", "e2b_sandbox"]),
            "knowledge": MCPServer(tools=["memory_store", "knowledge_graph"]),
            "community": MCPServer(tools=["liveagent_message", "sociograph_update"])
        }

class AIIntelligenceOverseer:
    def coordinate_mission(self, mission_description: str, mission_type: MissionType):
        """Qwen orchestrates → 0102 arbitrates → 012 observes (WSP 80)"""
```

**Current Integration**: Event queue EXISTS but NO event processing loop

**Gap**: No daemon mode to consume events from queue and make agentic decisions

---

#### 4. Social Media Orchestrator (Multi-Account Poster)
**File**: `modules/platform_integration/social_media_orchestrator/src/multi_account_manager.py`

**Status**: OPERATIONAL - Event routing with multi-account support

**Architecture**:
```python
class SocialMediaEventRouter:
    async def handle_event(self, event_type: str, event_data: Dict) -> Dict[str, Any]:
        """
        Routes events to appropriate accounts.

        Supported event_types:
        - 'git_push' → LinkedIn: development_updates (1263645), X: foundups
        - 'youtube_live' → LinkedIn: foundups_company, X: foundups
        - 'code_milestone' → Multiple accounts
        """
        accounts_to_post = self.manager.get_accounts_for_event(event_type)
        content = self._prepare_content(event_type, event_data)

        # Post to each account in parallel
        tasks = [self.manager.post_to_account(platform, key, content)
                 for platform, keys in accounts_to_post.items()
                 for key in keys]
        results = await asyncio.gather(*tasks)
        return formatted_results
```

**Current Integration**: Event routing configured in `social_accounts.yaml`

**Configuration** (`config/social_accounts.yaml` lines 67-71):
```yaml
event_routing:
  git_push:
    linkedin:
      - "development_updates"  # Company ID: 1263645
    x_twitter:
      - "foundups"
```

**Gap**: No integration with git events or AI Overseer

---

## Problem Statement

**Current State**:
- Manual commits don't trigger social media posts (GitPushDAE is autonomous-only)
- Post-commit hook I created calls GitLinkedInBridge directly (duplicate system)
- AI Overseer has event queue but no processing loop
- SocialMediaEventRouter exists but not integrated with git flow

**User Requirement**:
> "shouldn't 0102 push to queue, that then AI_overseer monitors and then agentically decides what to do with it... we have all these modules that needs to seamless interact... use the occums the existing modules..."

---

## Proposed Architecture (Occam's Razor)

### Option 1: Event-Driven via AI Overseer (RECOMMENDED)

**Flow**: Git Hook → Event Queue → AI Overseer Event Loop → Social Media DAE

**Why This Approach**:
1. ✅ Uses existing `event_queue` in AI Overseer MCP integration (line 100)
2. ✅ Works for ALL commits (manual + autonomous)
3. ✅ AI Overseer can make agentic decisions (Qwen analysis)
4. ✅ Leverages existing SocialMediaEventRouter
5. ✅ No duplicate systems created
6. ✅ User explicitly requested: "push to queue, that then AI_overseer monitors"

**Components to Add**:

#### A. Event Processing Loop in AI Overseer
**File**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`

**New Method**:
```python
class AIIntelligenceOverseer:
    async def start_event_processing_daemon(self):
        """
        Event processing daemon for AI Overseer.
        Consumes events from queue and makes agentic decisions.
        WSP 91 compliant daemon lifecycle.
        """
        self.logger.info("[AI-OVERSEER] Starting event processing daemon...")

        while self.daemon_active:
            try:
                # Get event from queue (timeout for graceful shutdown)
                event = await asyncio.wait_for(
                    self.mcp_integration.event_queue.get(),
                    timeout=5.0
                )

                # Agentic decision: Should we process this event?
                decision = await self._make_event_decision(event)

                if decision['should_process']:
                    # Route to appropriate handler
                    await self._process_event(event, decision)
                else:
                    self.logger.info(f"[AI-OVERSEER] Skipping event: {decision['reasoning']}")

            except asyncio.TimeoutError:
                # No events - continue monitoring
                continue
            except Exception as e:
                self.logger.error(f"[AI-OVERSEER] Event processing error: {e}")

    async def _make_event_decision(self, event: Dict) -> Dict:
        """
        Agentic decision using Qwen analysis.

        Criteria:
        1. Event type matches configured handlers
        2. Rate limiting not exceeded
        3. Content quality meets threshold
        4. Not during quiet hours
        """
        # Use Qwen to analyze commit significance
        if event['type'] == 'git_commit':
            commit_analysis = await self._analyze_commit_with_qwen(event['data'])

            return {
                'should_process': commit_analysis['social_value'] >= 0.6,
                'reasoning': commit_analysis['reasoning'],
                'confidence': commit_analysis['confidence']
            }

        # Default: process all events
        return {'should_process': True, 'reasoning': 'Auto-process', 'confidence': 1.0}

    async def _process_event(self, event: Dict, decision: Dict):
        """Process event by calling Social Media DAE"""
        from modules.platform_integration.social_media_orchestrator.src.multi_account_manager import SocialMediaEventRouter

        router = SocialMediaEventRouter()

        # Call Social Media DAE with event data
        results = await router.handle_event(
            event_type=event['type'],
            event_data=event['data']
        )

        self.logger.info(f"[AI-OVERSEER] Social media posting complete: {results}")
```

#### B. Post-Commit Hook Integration
**File**: `.git/hooks/post-commit`

**Updated Implementation**:
```bash
#!/bin/bash
# Post-commit hook: Push git commit event to AI Overseer queue
# WSP 91: Event-driven architecture

echo "[0102] Post-commit hook: Pushing event to AI Overseer queue..."

# Get commit details
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
FILES_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD | wc -l)
AUTHOR=$(git log -1 --pretty=%an)

# Push to AI Overseer event queue
python3 << 'PYTHON_SCRIPT'
import sys
import asyncio
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

try:
    from modules.ai_intelligence.ai_overseer.src.mcp_integration import AIOverseerMCPIntegration

    # Initialize MCP integration
    mcp = AIOverseerMCPIntegration()

    # Create event data
    event = {
        'type': 'git_commit',
        'data': {
            'hash': '$COMMIT_HASH',
            'message': '''$COMMIT_MSG''',
            'files_changed': $FILES_CHANGED,
            'author': '$AUTHOR',
            'timestamp': datetime.now().isoformat()
        }
    }

    # Push to queue (async operation)
    asyncio.run(mcp.event_queue.put(event))

    print("[0102] ✅ Event pushed to AI Overseer queue")
    print("[0102]    AI Overseer will decide whether to post to social media")

except Exception as e:
    print(f"[0102] ⚠️  Failed to push event: {e}")
    # Don't fail commit if event push fails
    sys.exit(0)

PYTHON_SCRIPT

echo "[0102] Post-commit hook complete!"
```

#### C. GitPushDAE Integration (Autonomous Commits)
**File**: `modules/infrastructure/git_push_dae/src/git_push_dae.py`

**Update `_execute_push()` method**:
```python
def _execute_push(self, decision: PushDecision, context: PushContext):
    """Execute push with event-driven social media integration"""

    # ... existing commit and push logic ...

    # NEW: Push to AI Overseer event queue instead of GitLinkedInBridge
    try:
        import asyncio
        from modules.ai_intelligence.ai_overseer.src.mcp_integration import AIOverseerMCPIntegration

        mcp = AIOverseerMCPIntegration()

        event = {
            'type': 'git_commit',
            'data': {
                'hash': commit_hash,
                'message': commit_message,
                'files_changed': len(context.uncommitted_changes),
                'author': '0102 (GitPushDAE)',
                'timestamp': datetime.now().isoformat(),
                'autonomous': True  # Flag for autonomous commits
            }
        }

        # Push to queue
        asyncio.run(mcp.event_queue.put(event))

        self.logger.info("[GitPushDAE] ✅ Event pushed to AI Overseer queue")

    except Exception as e:
        self.logger.error(f"[GitPushDAE] Failed to push event: {e}")
```

---

### Integration Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     GIT COMMIT EVENT                            │
│  (Manual commit OR GitPushDAE autonomous commit)                │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ .git/hooks/          │
        │ post-commit          │ ← Triggered on EVERY commit
        └──────────┬───────────┘
                   │ event = {'type': 'git_commit', 'data': {...}}
                   │
                   ▼
        ┌──────────────────────────────────┐
        │ AI Overseer MCP Integration      │
        │ event_queue.put(event)           │ ← asyncio.Queue (line 100)
        └──────────┬───────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────────────┐
        │ AI Overseer Event Processing Loop        │
        │ start_event_processing_daemon()          │ ← NEW daemon
        └──────────┬───────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │ Agentic Decision (Qwen Analysis)    │
        │ _make_event_decision(event)         │
        │ - Analyze commit significance       │
        │ - Check rate limits                 │
        │ - Evaluate social value ≥ 0.6      │
        │ - Check timing windows              │
        └──────────┬──────────────────────────┘
                   │
                   ├─── should_process=False ──→ [Skip, log reasoning]
                   │
                   └─── should_process=True
                        │
                        ▼
        ┌─────────────────────────────────────────────┐
        │ Social Media DAE                            │
        │ SocialMediaEventRouter.handle_event()       │
        │ - Route to accounts (social_accounts.yaml)  │
        │ - LinkedIn: development_updates (1263645)   │
        │ - X/Twitter: foundups                       │
        └──────────┬──────────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────┐
        │ Multi-Account Parallel Post │
        │ - LinkedIn API              │
        │ - X API                     │
        └─────────────────────────────┘
```

---

### Alternative Options (Considered but NOT Recommended)

#### Option 2: Extend GitPushDAE Only
**Flow**: GitPushDAE → SocialMediaEventRouter (direct call)

**Pros**:
- Simple integration
- Uses existing daemon

**Cons**:
- ❌ Only works for autonomous commits
- ❌ Manual commits still bypass system
- ❌ No event queue (less flexible)
- ❌ Doesn't match user's request for queue-based architecture

#### Option 3: Extend HoloDAE WRE Triggers
**Flow**: Post-commit hook → Touch trigger file → HoloDAE WRE skill → Social Media DAE

**Pros**:
- Uses existing monitoring loop
- File-based triggers (simple)

**Cons**:
- ❌ File-based triggers are less elegant than event queue
- ❌ HoloDAE is for code intelligence, not social media
- ❌ Mixing concerns (code quality vs social media)

---

## Implementation Plan

### Phase 1: Add Event Processing to AI Overseer
**Files to Modify**:
1. `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`
   - Add `start_event_processing_daemon()` method
   - Add `_make_event_decision()` with Qwen analysis
   - Add `_process_event()` to call Social Media DAE

2. `modules/ai_intelligence/ai_overseer/src/mcp_integration.py`
   - Verify event_queue is accessible from main AIIntelligenceOverseer class

**Test**:
```python
# Manual test of event processing
from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer
import asyncio

overseer = AIIntelligenceOverseer()

# Push test event
event = {
    'type': 'git_commit',
    'data': {
        'hash': 'abc123',
        'message': 'TEST: Verify event processing',
        'files_changed': 5
    }
}

await overseer.mcp_integration.event_queue.put(event)

# Start daemon (should consume event)
await overseer.start_event_processing_daemon()
```

### Phase 2: Update Post-Commit Hook
**Files to Modify**:
1. `.git/hooks/post-commit` - Replace GitLinkedInBridge with event queue push

**Test**:
```bash
# Make test commit
git add test.txt
git commit -m "TEST: Verify post-commit event push"

# Check logs
tail -f logs/ai_overseer.log
# Should see: "[AI-OVERSEER] Event pushed to queue"
```

### Phase 3: Update GitPushDAE
**Files to Modify**:
1. `modules/infrastructure/git_push_dae/src/git_push_dae.py`
   - Update `_execute_push()` to use event queue instead of GitLinkedInBridge

**Test**:
```bash
# Start GitPushDAE
python main.py --git

# Make changes, wait for autonomous commit
# Check logs
tail -f logs/git_push_dae.log
# Should see: "[GitPushDAE] Event pushed to AI Overseer queue"
```

### Phase 4: Launch AI Overseer Daemon
**Files to Create**:
1. `modules/ai_intelligence/ai_overseer/scripts/launch_event_daemon.py`

```python
#!/usr/bin/env python3
"""Launch AI Overseer Event Processing Daemon"""
import asyncio
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_overseer_event_daemon.log'),
        logging.StreamHandler()
    ]
)

async def main():
    overseer = AIIntelligenceOverseer()
    overseer.daemon_active = True

    print("[AI-OVERSEER] Event processing daemon starting...")
    print("[AI-OVERSEER] Listening for git commit events...")

    await overseer.start_event_processing_daemon()

if __name__ == '__main__':
    asyncio.run(main())
```

**Launch**:
```bash
python modules/ai_intelligence/ai_overseer/scripts/launch_event_daemon.py
```

---

## WSP Compliance

**WSP 91 (DAEMON Observability)**:
- ✅ Full logging in AI Overseer event daemon
- ✅ Decision traces for agentic analysis
- ✅ Health metrics for queue depth, processing time

**WSP 80 (Cube-Level DAE)**:
- ✅ Qwen orchestrates (event significance analysis)
- ✅ 0102 arbitrates (daemon launch and configuration)
- ✅ 012 observes (monitoring logs)

**WSP 27 (Universal DAE Architecture)**:
- ✅ Event-driven autonomous decisions
- ✅ No human intervention required

**WSP 96 (MCP Governance)**:
- ✅ Uses existing MCP integration event queue
- ✅ Rubik DAE "Community" server governs social media tools

---

## Benefits of This Architecture

1. **No Duplicate Systems**: Uses existing SocialMediaEventRouter, AI Overseer queue
2. **Works for ALL Commits**: Manual + autonomous both trigger events
3. **Agentic Decisions**: Qwen analyzes commit significance before posting
4. **Event-Driven**: Decouples git operations from social media posting
5. **Observable**: Full WSP 91 logging and decision traces
6. **Extensible**: Event queue can handle future events (code_milestone, deployment, etc.)
7. **Rate Limited**: AI Overseer can enforce rate limits across all commit types

---

## Next Steps

**User Decision Required**:
1. Approve Option 1 (Event-Driven via AI Overseer)?
2. Implement Phase 1 (Event Processing Daemon)?
3. Update post-commit hook to use event queue?
4. Launch AI Overseer daemon alongside existing daemons?

**Awaiting**: User approval to proceed with implementation.
