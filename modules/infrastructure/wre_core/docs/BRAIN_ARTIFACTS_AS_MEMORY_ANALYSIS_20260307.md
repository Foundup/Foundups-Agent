# Brain Artifacts as System Memory — First Principles Analysis

**Date**: 2026-03-07  
**Context**: 012 identified that `~/.gemini/antigravity/brain/` contains rich reasoning traces that are invisible to HoloIndex, WRE, and all training pipelines.

---

## What Exists (Inventory)

**29 conversation directories** containing:

| Artifact Type             | Example                                                   | What It Contains |
| ------------------------- | --------------------------------------------------------- | ---------------- |
| `implementation_plan.md`  | Design decisions, file change lists, verification plans   |
| `task.md`                 | Step-by-step checklists with `[x]`/`[/]`/`[ ]` progress   |
| `walkthrough.md`          | Proof of work — what was done, tested, validated          |
| `.resolved.N` files       | **Revision history** — every saved state of each artifact |
| `*.png`, `*.webp`         | Screenshots and browser recordings                        |
| `.metadata.json`          | Artifact type classification and summaries                |
| `.system_generated/logs/` | Full conversation logs with tool calls and reasoning      |

**One conversation** (OpenClaw Security audit) contains **71 files** — 15 task revisions, 5 plan revisions, 29 screenshots, interaction recordings.

## The Gap

```
CURRENT STATE:
  0102 writes artifacts → brain/ directory → session ends → data is orphaned
  Next 0102 session → starts from scratch → no recall unless explicitly navigated

DESIRED STATE:
  0102 writes artifacts → brain/ directory → extracted/indexed → available system-wide
  Next session → HoloIndex surfaces relevant past reasoning → WRE learns patterns
```

## Three Value Layers (First Principles)

### 1. Reasoning Traces = Training Data 🧠

The `.resolved.N` revision files are **labeled examples of iterative refinement**:

```
implementation_plan.md.resolved.0  → First draft (often wrong)
implementation_plan.md.resolved.1  → After 012 feedback
implementation_plan.md.resolved.2  → After code review
implementation_plan.md.resolved.3  → Final approved version
```

This is **preference-ranked data** — exactly what RLHF/DPO training needs. The last revision is the "chosen" response, earlier revisions are "rejected." For Qwen/Gemma fine-tuning:

- **Input**: task description + codebase context
- **Output progression**: draft → revision → correction → final
- **Signal**: 012 approval = positive label

Use cases:

- Fine-tune Qwen to write better implementation plans on first attempt
- Train AI Overseer to spot plans that will need revision (predict 012 feedback)
- Train IronClaw to recognize when an agent's reasoning is drifting (compare `.resolved.0` vs `.resolved.N`)

### 2. HoloIndex as Cross-Session Memory 🔍

HoloIndex scans the repo for code and docs. It currently does **not** scan:

- `~/.gemini/antigravity/brain/` (Antigravity artifacts)
- `~/.claude/` (Claude Code session data)

If HoloIndex added `brain/` as a secondary scan path:

**What becomes searchable**:

- Past audit findings (like today's 6-layer architecture audit)
- Implementation plans that were approved (proven-good architectural decisions)
- Walkthrough results (what was tested and how)
- Task checklists (which work items were completed across sessions)

**The typewriter analogy applies**: Past reasoning traces are "reasoning skills" — patterns for how to approach architectural audits, security reviews, module refactors. Current skills are "execution skills" (how to do an action). The brain artifacts would add "thinking skills" (how to reason about a problem).

**Practical approach**: Don't index everything. Extract and promote:

- `implementation_plan.md` (final `.resolved.N` only) → architecturally significant decisions
- `walkthrough.md` → verified approaches that worked
- Ignore `task.md` (ephemeral checklists with no lasting value)

### 3. WRE Pattern Extraction 🔄

The WRE recursive improvement loop currently learns from **execution outcomes**:

```
Skill executed → success/failure → pattern_memory.py records → WRE learns
```

The brain artifacts add a missing layer — **reasoning outcomes**:

```
Plan proposed → 012 revised (or approved) → reasoning quality signal
```

This could feed `recursive_improvement/src/learning.py`:

- Plans that needed 5 revisions = poor reasoning pattern (learn to avoid)
- Plans approved on first attempt = good reasoning pattern (learn to repeat)
- Tasks where 0102 backtracked mid-execution = missed precondition (learn to check)

## Integration Approaches

### Option A: Lightweight — Post-Session Extract Script

A DAE or scheduled script that:

1. Scans `brain/*/` after each session
2. Extracts final-state `implementation_plan.md` and `walkthrough.md`
3. Copies them into `WSP_knowledge/reasoning_traces/`
4. WRE indexes them with existing `holoindex_integration.py`

**Pros**: Minimal code changes, no HoloIndex modification  
**Cons**: Manual trigger or scheduler needed, doesn't capture revision history

### Option B: HoloIndex Secondary Scan Path

Add `~/.gemini/antigravity/brain/` as a read-only scan target in HoloIndex config:

1. HoloIndex discovers and indexes brain artifacts alongside code
2. Future `--search` queries surface past reasoning when relevant
3. Brain artifacts tagged with `source: antigravity_brain` for filtering

**Pros**: Automatic, searchable, no file duplication  
**Cons**: HoloIndex needs path configuration change, indexes ephemeral revisions unless filtered

### Option C: Full Pipeline — Extract → Transform → Train

1. Extract script pulls `.resolved.N` revisions and `metadata.json`
2. Transform into DPO/preference pairs (revision 0 vs final)
3. Feed into Qwen/Gemma fine-tuning pipeline
4. AI Overseer trains on "plan quality prediction" from revision count signal

**Pros**: Highest value — actual model improvement from real data  
**Cons**: Requires fine-tuning infrastructure, most implementation effort

## Recommendation

**Start with Option A** (extract script) to immediately capture value, with a path to Option B (HoloIndex scan) for cross-session retrieval. Option C (training pipeline) is the long-game goal but requires the data collection from A/B to be in place first.

The first-principles insight: **the reasoning traces are more valuable than the execution traces** because they contain 012's correction signal. WRE currently only learns from "did the action work?" — brain artifacts add "was the thinking right?"
