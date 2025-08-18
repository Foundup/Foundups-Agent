# CMST PQN Detector — Curated Evidence (0102 index)

Purpose (for 0102)
- Single index for curated artifacts used by PQN test agents; no per-folder narratives.
- Subfolders contain raw CSV/PNG/JSONL only.

Structure
- run_001/ — exemplar detector run (metrics CSV, events JSONL)
- phase_len2/ — sweep CSV/plot (length 2)
- phase_len3/ — sweep CSV/plot (length 3)
- phase_len4/ — sweep CSV/plot (length 4)

Usage
- 0102 agents load CSV/JSONL directly; this index provides folder pointers only.
- See Supplement S11 for methodology; module API in modules/ai_intelligence/pqn_alignment/.
