# WSP 3: Module Organization Protocol (UPDATED - Skills Directory Added)

**CRITICAL UPDATE - 2025-10-20**: Added `skills/` directory as **"The Wardrobe"** - WRE entry point for AI agent instructions

---

## Core Principle: Domain → Block → Cube + Wardrobe Pattern

### Updated Structure Hierarchy

```
modules/                          # Root
├── [domain]/                     # Enterprise Domain (communication, gamification, etc.)
│   ├── __init__.py              # Domain-level exports
│   └── [block]/                 # Specific Feature/Component Block
│       ├── __init__.py          # Block-level exports
│       ├── src/                 # The Cube - Implementation
│       │   ├── __init__.py      # Cube exports
│       │   └── *.py             # Implementation files (<500 lines each)
│       ├── skills/              # The Wardrobe - AI Agent Instructions ⭐ NEW
│       │   ├── [skill_name]/    # Task-specific skill
│       │   │   ├── SKILL.md     # Instructions (YAML frontmatter + Markdown)
│       │   │   ├── versions/    # Evolution history (v1.0, v1.1, v1.2...)
│       │   │   ├── metrics/     # Pattern fidelity scores (Gemma validation)
│       │   │   ├── variations/  # A/B test candidates (Qwen-generated)
│       │   │   └── CHANGELOG.md # Evolution rationale
│       │   └── ...              # Additional skills for this block
│       ├── tests/               # Block-specific tests
│       ├── docs/                # Block documentation
│       └── ModLog.md            # Block change log
```

---

## The Wardrobe: `skills/` Directory

### Purpose

The `skills/` directory is **"The Wardrobe"** - it tells AI agents (Qwen, Gemma, etc.) **how to act** when performing tasks within this module/block.

**Key Concept**: Skills are **trainable parameters** (like neural network weights) that evolve through recursive feedback loops.

### Why "Wardrobe"?

- **Wardrobe** = Collection of outfits (skills) an agent can "wear" for different tasks
- Each skill defines **how the agent should behave** for a specific task
- Agent "puts on" the appropriate skill when assigned a task
- Skills evolve based on performance (pattern fidelity scores)

### WRE Integration

The `skills/` directory is the **entry point for WRE** (Wearable Recursive Execution):

1. **Task Assignment**: WSP Orchestrator assigns task to Qwen/Gemma
2. **Skill Discovery**: Scan block's `skills/` directory for relevant skill
3. **Skill Loading**: Load SKILL.md into agent's prompt (like putting on a costume)
4. **Execution**: Agent performs task following skill instructions
5. **Scoring**: Gemma scores pattern fidelity (did agent follow the playbook?)
6. **Evolution**: If fidelity < 90%, Qwen generates improved variations
7. **Update**: Best variation becomes new skill version

**This is NOT for Claude Code** - this is for native Qwen/Gemma execution!

---

## Example: Communication Domain with Skills

### Before (Old WSP 3)

```
modules/communication/
└── livechat/                    # Block: YouTube Live Chat
    ├── src/                     # Cube: Implementation
    │   ├── livechat_core.py
    │   ├── message_processor.py
    │   └── chat_sender.py
    ├── tests/
    ├── docs/
    └── ModLog.md
```

### After (Updated WSP 3 with Wardrobe)

```
modules/communication/
└── livechat/                    # Block: YouTube Live Chat
    ├── src/                     # Cube: Implementation
    │   ├── livechat_core.py
    │   ├── message_processor.py
    │   └── chat_sender.py
    ├── skills/                  # Wardrobe: AI Agent Instructions ⭐
    │   ├── youtube_moderation/
    │   │   ├── SKILL.md         # How to moderate YouTube chat
    │   │   ├── versions/
    │   │   │   ├── v1.0_baseline.md
    │   │   │   ├── v1.1_add_caps_detection.md
    │   │   │   └── v1.2_improve_toxic_patterns.md
    │   │   ├── metrics/
    │   │   │   ├── pattern_fidelity.json   # Gemma scores
    │   │   │   └── outcome_quality.json    # Task success rates
    │   │   ├── variations/      # Qwen-generated A/B test candidates
    │   │   └── CHANGELOG.md
    │   ├── banter_response/
    │   │   ├── SKILL.md         # How to generate chat responses
    │   │   ├── versions/
    │   │   ├── metrics/
    │   │   └── CHANGELOG.md
    │   └── stream_detection/
    │       ├── SKILL.md         # How to detect live streams
    │       ├── versions/
    │       ├── metrics/
    │       └── CHANGELOG.md
    ├── tests/
    ├── docs/
    └── ModLog.md
```

---

## Skills Directory Structure (Detailed)

### SKILL.md Format

```markdown
---
name: youtube_moderation
description: Moderate YouTube live chat by detecting spam, toxic content, and enforcing rate limits. Use when processing chat messages.
version: 1.2
author: wre_system
agents: [qwen, gemma]
trigger_keywords: [moderate, spam, toxic, chat, filter]
pattern_fidelity_threshold: 0.90
---

# YouTube Chat Moderation Skill

## Task

Moderate incoming YouTube live chat messages to maintain positive community environment.

## Instructions

1. **Check for CAPS SPAM**
   - If message length > 20 AND 80%+ uppercase → BLOCK
   - Log as spam_type: "caps_spam"

2. **Check for REPETITION**
   - If message appears 3+ times in recent history → BLOCK
   - Log as spam_type: "repetition"

3. **Check for TOXIC CONTENT**
   - Scan for toxic keywords from toxic_patterns.json
   - If confidence > 0.8 → BLOCK
   - Log as spam_type: "toxic"

4. **Rate Limiting**
   - Max 5 messages per user per 30 seconds
   - If exceeded → WARN first, then BLOCK

5. **Allow Legitimate Messages**
   - If passes all checks → ALLOW
   - Route to banter_response skill for reply

## Expected Patterns

Gemma will score your adherence to these instructions:
- ✅ Checked CAPS (pattern: caps_check_executed)
- ✅ Checked REPETITION (pattern: repetition_check_executed)
- ✅ Checked TOXICITY (pattern: toxicity_check_executed)
- ✅ Applied RATE LIMITING (pattern: rate_limit_applied)
- ✅ Logged decision (pattern: decision_logged)

## Examples

### Example 1: CAPS SPAM
Input: "VISIT MY CHANNEL FOR FREE MONEY!!!!!!"
Expected: BLOCK (caps_spam)
Pattern: caps_check_executed=True, decision=block

### Example 2: Legitimate Message
Input: "Great stream! Love the content."
Expected: ALLOW
Pattern: all_checks_passed=True, decision=allow
```

### metrics/pattern_fidelity.json

```json
{
  "skill_name": "youtube_moderation",
  "version": "1.2",
  "total_executions": 247,
  "pattern_scores": {
    "caps_check_executed": {"count": 247, "fidelity": 1.00},
    "repetition_check_executed": {"count": 245, "fidelity": 0.99},
    "toxicity_check_executed": {"count": 247, "fidelity": 1.00},
    "rate_limit_applied": {"count": 243, "fidelity": 0.98},
    "decision_logged": {"count": 247, "fidelity": 1.00}
  },
  "overall_pattern_fidelity": 0.994,
  "threshold_met": true,
  "last_updated": "2025-10-20T15:30:00Z"
}
```

### versions/ Directory

Tracks skill evolution history:

```
versions/
├── v1.0_baseline.md           # Initial version (fidelity: 0.75)
├── v1.1_add_caps_detection.md # Added CAPS check (fidelity: 0.85)
└── v1.2_improve_toxic_patterns.md  # Improved toxic detection (fidelity: 0.99)
```

### CHANGELOG.md

```markdown
# YouTube Moderation Skill - Evolution History

## v1.2 (2025-10-20) - CONVERGED
- Pattern fidelity: 99.4% (threshold: 90%)
- Improved toxic content detection patterns
- Reduced false positives by 15%
- Variation #3 from A/B test (best performer)

## v1.1 (2025-10-18)
- Added CAPS spam detection
- Pattern fidelity increased from 75% → 85%
- Qwen identified missing instruction in v1.0

## v1.0 (2025-10-15) - BASELINE
- Initial version
- Pattern fidelity: 75%
- Missing CAPS detection (identified by Gemma scoring)
```

---

## Integration with Existing WSP 3 Rules

### Updated Compliance Checklist

**Block Structure Requirements**:

- [ ] No `src/` directories at domain level
- [ ] All implementations are in `[domain]/[block]/src/`
- [ ] Each block has `skills/` directory for AI agent instructions ⭐ **NEW**
- [ ] Each skill has SKILL.md with YAML frontmatter ⭐ **NEW**
- [ ] Skills directory organized per task (not per agent) ⭐ **NEW**
- [ ] Each block has its own `__init__.py`
- [ ] Imports use full paths from module root
- [ ] All files under 500 lines
- [ ] Tests mirror the src/ structure

### Skills Directory Naming Convention

**Pattern**: `skills/[task_name]/`

**Examples**:
- ✅ `skills/youtube_moderation/` (task-specific)
- ✅ `skills/stream_detection/` (task-specific)
- ✅ `skills/banter_response/` (task-specific)
- ❌ `skills/qwen_skills/` (agent-specific - WRONG)
- ❌ `skills/gemma_skills/` (agent-specific - WRONG)

**Why?** Skills are task-specific, not agent-specific. Any agent (Qwen, Gemma, future models) can "wear" the same skill.

---

## Relationship to Claude Code Skills

### Dual Skills Systems

```
┌─────────────────────────────────────────────────────────────────┐
│                    FOUNDUPS SKILLS ECOSYSTEM                     │
└─────────────────────────────────────────────────────────────────┘

LAYER 1: CLAUDE CODE SKILLS (.claude/skills/)
├── Purpose: 0102 agent prototyping and validation
├── Environment: Claude Code CLI
├── Invocation: Anthropic's auto-discovery
└── Use Case: Validate skill patterns before deploying to native

LAYER 2: NATIVE SKILLS (modules/*/skills/)  ⭐ THIS WSP
├── Purpose: Qwen/Gemma production execution
├── Environment: Python/local models via WRE
├── Invocation: WSP Orchestrator skill discovery
└── Use Case: Autonomous agent task execution with skill guidance
```

### Workflow

1. **Prototype** in `.claude/skills/` (0102 validates pattern works)
2. **Extract** to `modules/[domain]/[block]/skills/` (deploy to native)
3. **Train** Qwen/Gemma to execute with skill loaded
4. **Score** with Gemma pattern fidelity validation
5. **Evolve** through recursive feedback loops
6. **Converge** when pattern fidelity ≥ 90%

---

## Benefits of Skills Directory

### 1. Consistency
- Same instructions = same behavior across sessions
- Reduces "vibecoding" (ad-hoc solutions)
- Enforces tested patterns

### 2. Evolution
- Skills improve over time like neural network weights
- A/B testing validates improvements
- Version control tracks what changed and why

### 3. Transparency
- Instructions are explicit (not buried in prompts)
- Pattern fidelity scores show adherence
- CHANGELOG documents evolution rationale

### 4. Scalability
- Each module gets its own wardrobe of skills
- Skills are composable (multiple skills per task)
- New agents can use existing skills without retraining

### 5. WRE Integration
- Skills are the entry point for Wearable Recursive Execution
- Agent "wears" skill like putting on a costume
- Natural integration with WSP framework

---

## Migration Guide

### For Existing Modules

**Step 1**: Create `skills/` directory in each block

```bash
cd modules/communication/livechat
mkdir -p skills
```

**Step 2**: Identify tasks that need skills

Examples for livechat module:
- youtube_moderation
- banter_response
- stream_detection
- toxic_content_filtering

**Step 3**: Create skill directory for each task

```bash
cd skills
mkdir youtube_moderation
cd youtube_moderation
touch SKILL.md
mkdir versions metrics variations
touch CHANGELOG.md
```

**Step 4**: Write SKILL.md with YAML frontmatter

See format above.

**Step 5**: Test with WSP Orchestrator

```python
from modules.infrastructure.wsp_orchestrator.src.skill_loader import NativeSkillLoader

loader = NativeSkillLoader()
skills = loader.discover_skills("modules/communication/livechat")
# Should find: youtube_moderation, banter_response, stream_detection
```

---

## Key Rules (Updated)

1. **No src/ at Domain Level**: The `src/` directory only exists within blocks, never at the domain level
2. **No skills/ at Domain Level**: The `skills/` directory only exists within blocks, never at the domain level ⭐ **NEW**
3. **Block = Feature**: Each block represents a distinct feature or component
4. **Cube = Implementation**: The src/ folder within a block contains actual code
5. **Wardrobe = Instructions**: The skills/ folder within a block tells agents how to act ⭐ **NEW**
6. **<500 Lines Per File**: Each file in src/ must be under 500 lines
7. **Skills are Task-Specific**: Name skills after tasks, not agents ⭐ **NEW**
8. **Skills Evolve**: Pattern fidelity scores drive skill evolution ⭐ **NEW**

---

## Examples of Correct Implementation

### 1. HoloIndex with Skills

```
holo_index/
├── src/
│   ├── holo_index.py
│   ├── search_engine.py
│   └── pattern_coach.py
├── skills/                      # Wardrobe ⭐
│   ├── semantic_search/
│   │   ├── SKILL.md
│   │   ├── versions/
│   │   └── metrics/
│   ├── module_analysis/
│   │   ├── SKILL.md
│   │   ├── versions/
│   │   └── metrics/
│   └── vibecoding_detection/
│       ├── SKILL.md
│       ├── versions/
│       └── metrics/
├── tests/
└── ModLog.md
```

### 2. WSP Orchestrator with Skills

```
modules/infrastructure/wsp_orchestrator/
├── src/
│   ├── wsp_orchestrator.py
│   └── skill_loader.py
├── skills/                      # Wardrobe ⭐
│   ├── wsp_analysis/
│   │   ├── SKILL.md
│   │   └── ...
│   ├── protocol_enhancement/
│   │   ├── SKILL.md
│   │   └── ...
│   └── gap_detection/
│       ├── SKILL.md
│       └── ...
├── tests/
└── ModLog.md
```

### 3. Vision DAE with Skills

```
modules/infrastructure/dae_infrastructure/foundups_vision_dae/
├── src/
│   ├── vision_dae.py
│   └── telemetry_reporter.py
├── skills/                      # Wardrobe ⭐
│   ├── telemetry_batching/
│   │   ├── SKILL.md
│   │   └── ...
│   ├── session_reporting/
│   │   ├── SKILL.md
│   │   └── ...
│   └── worker_coordination/
│       ├── SKILL.md
│       └── ...
├── tests/
└── ModLog.md
```

---

## Compliance Check (Updated)

Use this checklist to verify WSP 3 compliance:

**Structure**:
- [ ] No `src/` directories at domain level
- [ ] No `skills/` directories at domain level ⭐ **NEW**
- [ ] All implementations are in `[domain]/[block]/src/`
- [ ] All agent instructions are in `[domain]/[block]/skills/` ⭐ **NEW**

**Skills Directory**:
- [ ] Each block has `skills/` directory ⭐ **NEW**
- [ ] Skills are organized by task (not by agent) ⭐ **NEW**
- [ ] Each skill has SKILL.md with YAML frontmatter ⭐ **NEW**
- [ ] Each skill has versions/ and metrics/ directories ⭐ **NEW**
- [ ] Pattern fidelity scores are tracked ⭐ **NEW**

**Code Organization**:
- [ ] Each block has its own `__init__.py`
- [ ] Imports use full paths from module root
- [ ] All files under 500 lines
- [ ] Tests mirror the src/ structure

---

## Summary

**WSP 3 Updated**: Added `skills/` directory as **"The Wardrobe"**

**Key Changes**:
1. ✅ `skills/` directory added to block structure
2. ✅ Skills are task-specific agent instructions
3. ✅ WRE entry point for Qwen/Gemma execution
4. ✅ Skills evolve like neural network weights
5. ✅ Pattern fidelity scoring drives evolution
6. ✅ Skills are NOT for Claude Code (that's `.claude/skills/`)

**Philosophy**:
> "The wardrobe tells the AI in the system how to act."

Just as you put on different clothes for different occasions, agents "wear" different skills for different tasks. Skills define expected behavior, and the system scores how well agents follow the playbook.

---

*This WSP defines the canonical module organization pattern, now including the skills/ directory as the WRE entry point for AI agent instructions.*
