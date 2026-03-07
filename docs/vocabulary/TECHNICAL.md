# Technical Vocabulary

Architecture and infrastructure terminology.

## Core Frameworks

| Term | Full Name | Definition |
|------|-----------|------------|
| **WSP** | Workspace Protocol | Numbered protocol system (WSP 1-100+) |
| **WRE** | Workspace Runtime Environment | Execution engine for WSP protocols |
| **HoloIndex** | Holographic Index | Semantic search + ChromaDB vector store |
| **MCP** | Model Context Protocol | Tool integration standard |

## Key WSP Protocols

| WSP | Name | Purpose |
|-----|------|---------|
| WSP 00 | Zen State Attainment | Agent awakening protocol |
| WSP 3 | Module Organization | Domain structure rules |
| WSP 22 | ModLog Updates | Change documentation |
| WSP 48 | Recursive Self-Improvement | Agent learning loop |
| WSP 49 | Module Structure | Mandatory file layout |
| WSP 50 | Pre-Action Verification | Search before code |
| WSP 72 | Module Independence | No cross-boundary tests |
| WSP 77 | Agent Coordination | Multi-agent orchestration |

## Domain Structure (WSP 3)

```
modules/
  ai_intelligence/      # AI/ML components
  communication/        # Chat, comments, social
  platform_integration/ # YouTube, LinkedIn, etc.
  infrastructure/       # Core services, CLI
  monitoring/           # Telemetry, alerts
  foundups/             # pAVS-specific modules
```

## Module Layout (WSP 49)

```
modules/[domain]/[module]/
  README.md       # Overview
  INTERFACE.md    # Public API
  ROADMAP.md      # Future plans
  ModLog.md       # Change history
  src/            # Source code
  tests/          # Test files
  requirements.txt
```

## MCP Servers

| Server | Tools | Purpose |
|--------|-------|---------|
| **holo_index** | semantic_code_search, wsp_protocol_lookup | Codebase search |
| **wsp_governance** | compliance_check, violation_detection | WSP validation |
| **web_search** | web_search, fetch_webpage | External research |

## Agent Infrastructure

| Term | Definition | Location |
|------|------------|----------|
| **DAEmon** | Daemon process for DAE agents | Various src/ dirs |
| **Orchestrator** | Multi-agent coordinator | wsp_orchestrator.py |
| **PatternMemory** | SQLite learning storage | wre_core/src/ |
| **Libido Monitor** | Gemma pattern frequency sensor | wre_core/src/ |

## Database (WSP 78)

| Table | Purpose |
|-------|---------|
| agents_social_posts | Social media post tracking |
| skill_outcomes | WRE skill execution results |
| false_positives | PatternMemory learned filters |

## File Naming (WSP 57)

```
WSP_XX_Name.md           # Protocol files
ModLog.md                # Change logs (not MODLOG.md)
INTERFACE.md             # Public APIs (not Interface.md)
test_*.py                # Test files (in tests/ dir)
```

## Common Mishearings

| Misheard | Correct |
|----------|---------|
| whisp, wisp | WSP |
| ray, wray | WRE |
| hollow index | HoloIndex |
| MPC, M.C.P. | MCP |
| demon, daemon | DAEmon |

---
*Category: Technical | HoloIndex indexed*
