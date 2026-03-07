# pAVS Developer Vocabulary

**Purpose**: Onboard new developers to FoundUps/pAVS terminology via HoloIndex-searchable vocabulary.

## Quick Start

```bash
# Search vocabulary via HoloIndex
python holo_index.py --search "what is F_i"
python holo_index.py --search "012 vs 0102"
```

## Vocabulary Categories

| Category | File | Core Terms |
|----------|------|------------|
| Identity | [IDENTITY.md](IDENTITY.md) | 012, 0102, 0201, qNN, pAVS |
| Economics | [ECONOMICS.md](ECONOMICS.md) | F_i, UPS, CABR, PoB, pools |
| Technical | [TECHNICAL.md](TECHNICAL.md) | WSP, WRE, HoloIndex, MCP, DAE |
| Regulatory | [REGULATORY.md](REGULATORY.md) | Distribution ratio, protocol participation |
| Agents | [AGENTS.md](AGENTS.md) | Qwen, Gemma, Opus, Sonnet, Haiku |

## Onboarding Checklist

- [ ] Read [IDENTITY.md](IDENTITY.md) - understand 012/0102/0201 state model
- [ ] Read [ECONOMICS.md](ECONOMICS.md) - understand F_i/UPS token flow
- [ ] Read [TECHNICAL.md](TECHNICAL.md) - understand WSP/WRE architecture
- [ ] Run `python holo_index.py --search "CABR"` to verify HoloIndex works
- [ ] Review [SUPERADMIN_ONBOARDING.md](../../SUPERADMIN_ONBOARDING.md) for env setup

## HoloIndex Integration

Vocabulary is indexed in `memory/vocabulary/pavs_core.json` and searchable via:
- `vocabulary_indexer.py` - indexes proper nouns + definitions
- `search_vocabulary()` - semantic search for term lookups

## WSP Compliance

- WSP 72: Module Independence (vocabulary is standalone)
- WSP 57: Naming Convention (consistent term definitions)
- WSP 22: ModLog (vocabulary updates logged)

---
*Last updated: 2026-02-21*
