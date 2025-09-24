# HoloIndex - Semantic Code Discovery & WSP Master Intelligence

## Overview
HoloIndex is the **foundational board** for the entire FoundUps ecosystem - a semantic code discovery system implementing WSP 87 (Code Navigation Protocol) with integrated AI intelligence for WSP compliance guidance.

## Purpose
Transform code discovery from keyword matching to **semantic understanding** using:
- Vector embeddings for code similarity
- LLM-powered intelligent guidance (Qwen-Coder 1.5B)
- WSP Master protocol intelligence (95+ protocols)
- Pattern-based behavioral coaching
- DAE Cube organization and alignment

## Key Features

### 1. Semantic Search
- **Vector Database**: ChromaDB for semantic similarity
- **Dual Search**: Code + WSP documentation
- **NAVIGATION.py Integration**: Problem→Solution mapping
- **Adaptive Learning**: Query enhancement and pattern learning

### 2. AI Intelligence
- **LLM Integration**: Qwen-Coder 1.5B for code understanding
- **WSP Master**: Comprehensive protocol guidance
- **Pattern Coach**: Behavioral pattern detection and coaching
- **Multi-Source Synthesis**: LLM + WSP + Rules + Patterns

### 3. 0102 Consciousness Guidance
- **0102-to-0102 Prompts**: Violation-aware compliance prompts written by 0102 for 0102
- **Module-Specific WSP Guidance**: Contextual protocols based on detected module
- **Violation Prevention**: Reminders based on WSP_MODULE_VIOLATIONS.md history
- **Deep Think Enforcement**: Prevents vibecoding through consciousness prompts
- **Core WSP Questions**: "Does this need to exist?", "Can I afford it?", "Can I live without it?"
- **DAE Cube Organizer**: `--init-dae` command for alignment and structure mapping

### 4. Intelligent Subroutine Analysis
- **Algorithmic Analysis**: Runs size checks, duplication detection, health scans only when needed
- **Query Intent Detection**: Analyzes search intent to trigger relevant subroutines
- **Violation-Only Display**: Shows analysis results only when actual violations are found
- **Module-Specific Intelligence**: Knows which modules have violation history
- **Performance Optimized**: No wasted analysis on read-only queries

## Architecture
```
holo_index/
├── cli.py                    # Main CLI interface
├── qwen_advisor/            # AI advisor system
│   ├── advisor.py          # Multi-source intelligence synthesis
│   ├── wsp_master.py       # WSP protocol intelligence
│   ├── pattern_coach.py    # Behavioral coaching
│   └── llm_engine.py       # Qwen LLM integration
├── adaptive_learning/       # Phase 3 learning system
├── dae_cube_organizer/     # DAE structure intelligence
├── module_health/          # Health monitoring
├── tests/                  # Test suite
├── scripts/                # Utility scripts
└── docs/                   # Documentation
```

## Quick Start

### Basic Search
```bash
python holo_index.py --search "send chat message"
```

### Contextual Search (Module-Aware)
```bash
python holo_index.py --search "stream resolver"
# Automatically detects platform_integration/stream_resolver module
# Shows only relevant WSP protocols and health violations
```

### 0102 Consciousness Prompts
```bash
python holo_index.py --search "livechat message"
# Shows 0102-to-0102 compliance prompts based on violation history:
# ⚠️ 0102: Livechat module exceeded 1000+ lines - WSP 62 violation!
# 📖 0102: Did you read its README.md and INTERFACE.md first?
# 🧠 0102: Deep think: Can this be simplified? Follow WSP simplicity.
```

### Intelligent Analysis (Algorithmic)
```bash
python holo_index.py --search "add new feature to livechat"
# Automatically runs size analysis and duplication checks (modification intent detected)
# Shows results only if violations found:
# [ANALYSIS] Module Size Alert: 35,065 lines across 152 files
# [ANALYSIS] Code Duplication Detected: 43 duplicate pairs found

python holo_index.py --search "how does chat work"
# No analysis triggered (read-only query) - clean output
```

### With AI Advisor
```bash
python holo_index.py --search "create module" --llm-advisor
```

### Rate Advisor Quality (Earn Points)
```bash
python holo_index.py --search "create module" --llm-advisor --advisor-rating useful
```

### Acknowledge Reminders (Earn Points)
```bash
python holo_index.py --search "create module" --llm-advisor --ack-reminders
```

### DAE Initialization
```bash
python holo_index.py --init-dae "YouTube Live"
```

### Index Refresh
```bash
python holo_index.py --index-all
```

## WSP Compliance
- **WSP 87**: Code Navigation Protocol implementation
- **WSP 35**: HoloIndex Qwen Advisor Plan
- **WSP 49**: Module Directory Structure
- **WSP 50**: Pre-Action Verification
- **WSP 84**: Code Memory Verification
- **WSP 80**: Cube-Level DAE Orchestration

## Reward & Gamification System 🎯
HoloIndex uses a gamification system to encourage quality behaviors:

### Point System
- **+5**: Index refresh (keep knowledge current)
- **+3**: Using AI advisor for guidance
- **+5/+2**: Rating advisor quality (useful/not useful)
- **+1**: Acknowledging advisor reminders
- **+10/+5/+3**: Health issue detection (critical/medium/low severity)

### How It Works
- **Who Gets Points**: The 0102 Architect (you!) for quality behaviors
- **Purpose**: Encourages proactive compliance and tool usage
- **Tracking**: Session summaries show earned points
- **Variants**: Different reward multipliers (currently variant A)

## Performance
- **Search Speed**: <200ms dual search
- **LLM Inference**: <500ms with caching
- **Index Size**: ~500MB for full codebase
- **Memory Usage**: <1GB with models loaded
- **Token Efficiency**: 93% reduction vs traditional

## Dependencies
- Python 3.8+
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- llama-cpp-python (LLM inference)
- SQLite (violation tracking)

## Status
✅ **PRODUCTION READY** - All systems operational with comprehensive AI intelligence