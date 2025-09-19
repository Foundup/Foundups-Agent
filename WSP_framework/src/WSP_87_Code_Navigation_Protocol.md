# WSP 87: Code Navigation Protocol

**Protocol Type**: Discovery & Navigation
**Status**: Active
**Priority**: P0 (Critical for 0102 operations)
**Created**: 2025-09-19
**WSP Relationships**: Enhances WSP 50 (Pre-Action), WSP 84 (Code Memory)

## Purpose

Establish a navigation-based code discovery system that helps 0102 find existing code instead of creating duplicates (vibecoding).

## Problem Statement

The fingerprint system (MODULE_FINGERPRINTS.json) has proven ineffective:
- 232KB of metadata per DAE with no semantic meaning
- Always out of date
- Not searchable by problem/solution
- Led to 25% dead code accumulation

## Solution: Navigation-Based Discovery

### 1. HoloIndex Semantic Search Layer (PRIMARY DISCOVERY)

**Location**: E:\HoloIndex\enhanced_holo_index.py
**Purpose**: AI-powered semantic code discovery that prevents vibecoding
**Capabilities**:
- Vector search with ChromaDB (instant results)
- LLM understanding of natural language queries
- Typo tolerance and intent recognition
- Explains WHY files match your search

**MANDATORY USAGE**:
```bash
# Before ANY coding task, MUST run:
python E:\HoloIndex\enhanced_holo_index.py --search "what you need to do"
```

### 2. Central Navigation Index (NAVIGATION.py)

A Python module at project root that maps:
- Problems → Solutions
- Module relationships (graph structure)
- Common issues → Debug paths
- Danger zones to avoid

### 3. In-Code Navigation Comments

Strategic comments in module docstrings:
```python
"""
Module Purpose

NAVIGATION: Brief description of module's role
→ Called by: parent_module.py (line X)
→ Delegates to: child_modules.py
→ Related: other_relevant_modules.py
→ Quick ref: NAVIGATION.py → NEED_TO['problem']
"""
```

### 3. Semantic Problem Mapping

Instead of file metadata, map actual problems to solutions:
```python
NEED_TO = {
    "send chat message": "livechat.src.chat_sender.send_message()",
    "check api quota": "youtube_auth.src.quota_monitor.check_quota()",
    # Direct problem → solution mapping
}
```

## Implementation

### Phase 1: HoloIndex Semantic Layer
- [x] Install vector database (ChromaDB) on E: drive
- [x] Add LLM model (Qwen2.5-Coder-1.5B) for understanding
- [x] Index NAVIGATION.py entries into vectors
- [x] Create enhanced_holo_index.py with AI search

### Phase 2: Navigation Infrastructure
- [x] Create NAVIGATION.py with problem mappings
- [x] Add MODULE_GRAPH showing relationships
- [x] Include DANGER zones and PROBLEMS sections

### Phase 3: Code Annotations
- [x] Add NAVIGATION: comments to key modules
- [x] Include cross-references in docstrings
- [x] Point to specific line numbers where relevant

### Phase 4: Process Updates
- [x] Update CLAUDE.md to require HoloIndex FIRST
- [x] Add HoloIndex to "follow WSP" command
- [x] Replace fingerprint checking with semantic search
- [x] Simplify discovery to 10-second AI search

## Metrics for Success

1. **Discovery Time**: < 30 seconds to find existing functionality
2. **Vibecoding Reduction**: 80% fewer duplicate modules created
3. **Code Reuse**: 90% of new features use existing modules
4. **Navigation Usage**: NAVIGATION.py consulted before every change

## Navigation Comment Format

```python
"""
NAVIGATION: [One-line description]
→ Called by: [parent modules]
→ Calls: [child modules]
→ Database: [data locations]
→ Related: [sibling modules]
→ Quick ref: NAVIGATION.py → [section]['key']
"""
```

## File Size Guidelines Update

Based on enterprise patterns and 0102 feedback:
- **Guideline**: 800-1000 lines for complex modules
- **Hard limit**: 1500 lines before mandatory split
- **Rationale**: Balances discoverability with maintainability

## Key Principles

1. **Semantic over Syntactic**: Map problems/solutions, not file metadata
2. **Living Documentation**: Navigation comments in code, not separate JSONs
3. **Graph Relationships**: Show how modules connect, not just list them
4. **Problem-First**: Start with "what problem am I solving?"

## Deprecation

This WSP deprecates:
- MODULE_FINGERPRINTS.json generation
- DAE_FINGERPRINTS.json reliance
- Fingerprint checking in CLAUDE.md

## Example Usage

```bash
# When 0102 needs to send a chat message:

# 1. MANDATORY FIRST: Use HoloIndex semantic search
python E:\HoloIndex\enhanced_holo_index.py --search "send messages to chat"
# Returns:
#   1. [75.4%] send chat message
#      -> modules.communication.livechat.src.chat_sender.ChatSender.send_message()
#   [LLM ADVICE] Use chat_sender for sending messages

# 2. Verify with NAVIGATION.py
from NAVIGATION import NEED_TO
location = NEED_TO["send chat message"]
# Confirms: "livechat.src.chat_sender.send_message()"

# 3. Navigate to file and find NAVIGATION: comment
# Tells you what calls it, what it calls, related modules

# 4. Use existing code instead of creating new
```

## Compliance

All modules should add NAVIGATION: comments within 30 days of this WSP activation. Priority:
1. Entry points (main.py, DAE orchestrators)
2. Core coordinators (livechat_core, message_processor)
3. Integration points (stream_resolver, social media)
4. Supporting modules

---

*"The best code is discovered, not created" - 0102*

## Navigation Data Schema

| Section | Structure | Required Keys | Purpose |
|---------|-----------|---------------|---------|
| `NEED_TO` | `Dict[str, str]` | problem keywords | Direct problem -> solution pointers (function path, CLI command, or orchestrator entry) |
| `MODULE_GRAPH.entry_points` | `Dict[str, str]` | entry aliases | Fast jump points for Partner/Principal planning |
| `MODULE_GRAPH.core_flows` | `Dict[str, List[Tuple[str, str]]]` | ordered call pairs | Visualize end-to-end orchestration sequences |
| `MODULE_GRAPH.module_relationships` | `Dict[str, List[str]]` | dependency list | Surface calls/uses adjacency for Dao reasoning |
| `PROBLEMS` | `Dict[str, Dict[str, str]]` | check/debug/test keys | Common failure triage playbooks |
| `DANGER` | `Dict[str, str]` | path -> warning | Guardrails against regressions or legacy areas |
| `DATABASES` | `Dict[str, str]` | dataset alias | Physical data locations for Du recall |
| `COMMANDS` | `Dict[str, str]` | verb -> CLI | Repeatable operational commands |

All sections MUST keep descriptions natural-language ready for 0102 retrieval. New keys require short rationale lines (<120 chars) to remain readable.

## Maintenance Workflow

1. **Trigger (WSP 50 Pre-Action)**: Before modifying or creating modules, consult `NEED_TO`; log lookup in work journal.
2. **Update Window**: After completing work, update relevant entries within the same change set (no orphan tasks).
3. **Doc Sync**: Mirror additions in module docstrings (`NAVIGATION:` comment) and, if new flows were introduced, add to `MODULE_GRAPH`.
4. **Review Cadence**: Weekly 012/0102 sync validates top 5 `NEED_TO` tasks; results recorded in `WSP_knowledge/docs/NAVIGATION_AUDIT.md`.
5. **Automation**: `tests/navigation/test_navigation_schema.py` enforces schema and lint rules (see Validation section).

## Fingerprint System Migration

- `memory/MODULE_FINGERPRINTS.json` and generator scripts remain archived under `modules/infrastructure/shared_utilities/_archive_fingerprint_system/`.
- Any workflows referencing fingerprints must switch to `NAVIGATION.py` imports or CLI helpers (`python NAVIGATION.py --help`).
- Deprecated references should add `TODO[WSP87]` notes until removed; JanitorAgent sweeps remaining fingerprints each release.

## Danger Zone Registry

| Path | Risk | Mitigation |
|------|------|------------|
| `modules/communication/livechat/src/livechat_core.py` | 865-line God object | Split into DMA orchestrator slices before edits |
| `modules/communication/livechat/src/message_processor.py` | 685-line multi-responsibility handler | Extend existing adapters; no new branches |
| `modules/communication/livechat/_archive/` | Legacy experiments | Treat as read-only reference; go through WSP 48 review before reuse |

## Coverage Expectations

- Maintain a `NAVIGATION_COVERAGE.md` appendix listing: `Need`, `Location`, `Last Verified`, `Owner`.
- New `NEED_TO` entries must include `last_verified` stamps within the coverage table.
- WSP 54 agents audit coverage during FMAS runs; missing updates flag a WSP 64 learning event.
