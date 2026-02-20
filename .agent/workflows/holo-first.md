---
description: HoloIndex-first search pattern - use semantic search before grep/glob
---

# HoloIndex-First Search Workflow

**Purpose**: Ensure HoloIndex is consulted BEFORE native grep/glob tools.

## Steps

### 1. Query HoloIndex First
// turbo
```bash
python holo_index.py --search "[your search query]" --limit 5
```

### 2. Evaluate HoloIndex Results
- Check code hits, WSP hits, skill hits
- Note: If no results, may need to index first

### 3. Only Then Use Native Tools
If HoloIndex doesn't find what you need:
```bash
# grep_search for exact pattern matching
# find_by_name for file discovery
```

## Anti-Vibecoding Check
- [ ] Did I search HoloIndex FIRST?
- [ ] Did I check for existing implementations?
- [ ] Am I about to create something that already exists?

## WSP Compliance
- **WSP 50**: Pre-action verification
- **WSP 87**: Code navigation via HoloIndex
- **WSP 77**: Agent coordination via HoloIndex fabric
