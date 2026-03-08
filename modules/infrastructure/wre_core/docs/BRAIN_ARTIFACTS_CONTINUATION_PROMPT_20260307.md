# 0102 Continuation Prompt -- Brain Artifacts + Training Pipeline

**Origin Session**: `603032e1-f055-48cd-a844-18b5d39a5f59` (2026-03-07)
**Conversation Topic**: WRE Architecture Audit + Brain Artifacts as System Memory

---

## Context

012 and 0102 discovered that Antigravity's brain directory (`~/.gemini/antigravity/brain/`) contains **98 artifacts across 25 conversations with 500 revision snapshots** -- implementation plans, walkthroughs, audits, and task checklists that are invisible to HoloIndex and the training pipeline. An extractor script was built and verified. Four threads remain open.

## What Was Completed

| Item                     | Location                                                       |
| ------------------------ | -------------------------------------------------------------- |
| Brain artifacts analysis | `wre_core/docs/BRAIN_ARTIFACTS_AS_MEMORY_ANALYSIS_20260307.md` |
| Extractor script         | `wre_core/scripts/extract_brain_artifacts.py`                  |
| Extracted index          | `WSP_knowledge/reasoning_traces/brain_artifact_index.json`     |
| Human-readable summary   | `WSP_knowledge/reasoning_traces/brain_artifact_summary.md`     |
| WRE 6-layer audit        | `wre_core/docs/WRE_6LAYER_ARCHITECTURE_AUDIT_20260307.md`      |
| MPS drift (V024)         | `WSP_MODULE_VIOLATIONS.md`, `tools/ModLog.md`                  |
| All ModLog entries       | `wre_core/ModLog.md` (top 2 entries)                           |

## Open Thread 1: Wire Brain Revisions into Training Corpus

**Priority: HIGH** -- This connects the brain artifacts to the existing Qwen training pipeline.

**What exists:**

- `holo_index/training/comprehensive_training_corpus.py` -- 517-line collector with 6 data sources (012.txt, ModLogs, violations, chat, git, daemon logs)
- `training_data/dpo_pairs.jsonl` -- 89 existing DPO pairs in `{prompt, chosen, rejected, source}` format
- `training_data/decision_sft.jsonl` -- 100KB SFT data

**What to build:**
Add a `_collect_brain_artifacts()` method to `ComprehensiveTrainingCorpus` that:

1. Scans `~/.gemini/antigravity/brain/*/` for `implementation_plan.md` files
2. For each, reads `.resolved.0` (first draft = rejected) and final `.resolved.N` (approved = chosen)
3. Uses the task description from `task.md` as the prompt
4. Outputs DPO pairs in the same format as `dpo_pairs.jsonl`
5. Also extracts `walkthrough.md` as SFT examples (verified approaches)

**Key insight from 012:** "Every time you correct my plan, that correction becomes a labeled training example." The `.resolved.N` revision chain IS preference-ranked data.

## Open Thread 2: Move Traces to WSP_knowledge

**Priority: MEDIUM** -- Architectural alignment.

012's original architecture intent:

- `WSP_framework/` = system protocols
- `WSP_agentic/` = AI agent behavior
- `WSP_knowledge/` = memory layer

Currently reasoning traces are in `wre_core/memory/reasoning_traces/`. 012 indicated they should ideally live in `WSP_knowledge/` since that's the memory layer. 012 said: "I don't care, you're in charge of this kind of decision." But their stated preference was WSP_knowledge.

**Action:** Move `wre_core/memory/reasoning_traces/` contents to `WSP_knowledge/reasoning_traces/`. Update the extractor script's `DEFAULT_OUTPUT_DIR`. Update ModLog.

## Open Thread 3: Mojibake Sanitizer

**Priority: LOW** -- Quality of life.

Unicode characters like stars, arrows, em dashes render as garbled CJK on Windows.

**What exists:** `utils/json_sanitizer.py` handles unpaired Unicode surrogates for JSON APIs. Different problem.

**What to build:** A simple `utils/markdown_sanitizer.py` with a `str.translate()` table mapping:

- `-->` for right arrow
- `<--` for left arrow
- `--` for em dash
- `[*]` for star emoji
- `[OK]` for check emoji

**012's decision:** This is a deterministic regex task, NOT an LLM task. No Gemma/Qwen needed.

## Open Thread 4: Wire Extractor into main.py

**Priority: LOW** -- Automation.

The brain extractor currently runs manually. To make it automatic, add it as a lightweight preflight in `main.py` startup that:

1. Checks if new brain conversations exist since last scan
2. If yes, runs the extractor incrementally
3. Updates the index
4. Takes <1 second for the check, only does full scan when new data exists

## 012 Behavioral Notes for 0102

- 012 is dyslexic and chases tangents. These tangents are important but create context fragmentation.
- 012 refers to all 0102 instances as one system, not separate agents. "ALL 0102 are one and the same system."
- 012 expects 0102 to use HoloIndex search (`holo_index.py --search`) BEFORE creating new files. This session had a WSP 87 violation where 0102 used `find_by_name` instead.
- HoloIndex now supports `--mode lexical` for fast deterministic search. Use that if the advisor path hangs.
- The `012.txt` file in repo root is 012's manual copy-paste capture of conversation data. The brain extractor automates what 012 does manually.

## WSP Compliance

- WSP 22: Update ModLog for any changes
- WSP 50: Search HoloIndex BEFORE creating files
- WSP 84: Reuse `comprehensive_training_corpus.py`, don't create new collector
- WSP 87: Use `holo_index.py --search` or `NAVIGATION.py` first
- WSP 60: Memory architecture alignment with WSP_knowledge
