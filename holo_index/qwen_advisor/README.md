# Qwen Advisor - AI Intelligence System (HoloDAE Foundation)

## [ALERT] MAJOR ARCHITECTURAL EVOLUTION (2025-09-28)

**HoloIndex Qwen Advisor has been completely refactored** from monolithic architecture to modular design following correct **Qwen->0102 orchestration** principles.

## Overview
The Qwen Advisor provides intelligent AI-powered guidance for HoloIndex searches through a **modular architecture** that properly implements WSP 80 (Cube-Level DAE Orchestration). The system follows the correct **Qwen Orchestrator -> 0102 Arbitrator -> 012 Observer** flow.

## Purpose
Transform HoloIndex from keyword search to **intelligent AI assistant** that:
- Understands code context with LLM analysis
- Provides WSP protocol guidance
- Detects behavioral patterns for coaching
- Learns from user interactions
- **Maintains modular architecture** for scalability and maintainability

## Architecture

### [TARGET] Correct Qwen->0102 Orchestration Architecture

```
QWEN LLM (Primary Orchestrator - Circulatory System)
    v orchestrates ALL analysis operations
    v finds and rates issues with chain-of-thought
    v presents findings to
0102 Agent (Arbitrator - The Brain)
    v reviews Qwen's findings using MPS scoring
    v decides actions (P0=immediate, P1=batch, etc.)
    v executes fixes autonomously
012 Human (Observer)
    v monitors the Qwen->0102 collaboration
    v provides feedback for system tuning
```

### Modular Architecture (Post-Refactoring)

#### **[U+1F4C1] Core Data Models** (`models/`)
- **`work_context.py`**: WorkContext dataclass for tracking 0102 activity
- **`monitoring_types.py`**: Type definitions for monitoring operations

#### **[TOOL] Core Services** (`services/`)
- **`file_system_watcher.py`**: Real-time file system monitoring
- **`context_analyzer.py`**: Work pattern analysis and module detection

#### **[U+1F3AD] Orchestration Layer** (`orchestration/`)
- **`qwen_orchestrator.py`**: Qwen's primary orchestration logic
- Chain-of-thought logging and decision tracking

#### **[U+2696]️ Arbitration Layer** (`arbitration/`)
- **`mps_arbitrator.py`**: 0102's MPS-based decision making (WSP 15)
- Action prioritization and execution coordination

#### **[U+1F5A5]️ UI Layer** (`ui/`)
- **`menu_system.py`**: User interface for 0102 interaction
- Status displays and menu navigation

#### **[TARGET] Main Coordinator** (`holodae_coordinator.py`)
- **Clean integration layer** replacing monolithic architecture
- Orchestrates all modular components
- Provides unified API for main.py integration

### Legacy Components (Pre-Refactoring - Archived)
- **Archived**: `autonomous_holodae.py` -> `_archive/autonomous_holodae_monolithic_v1.py`
- **Reason**: 1,405-line monolithic file violating WSP 62 and 80

### Current Integration Status (Post-Verification)
- **Modules Maintained**: 9 active modules (+ legacy intelligent monitor adapter)
- **Line Ranges**: 59-327 lines across active modules (legacy intelligent_monitor.py is 531 lines; follow-up split queued)
- **FileSystemWatcher/ContextAnalyzer**: Invoked by HoloDAECoordinator during monitoring cycles and request orchestration
- **Quiet Logging**: start_monitoring() emits a single actionable summary; archived Δ heartbeat logs remain in _archive/
- **MonitoringResult Model**: Unified in models/monitoring_types.py; intelligent_monitor.py now adapts to the shared dataclasses
- **CLI Usage**: Monitoring is disabled by default for single-shot Holo CLI queries; call `HoloDAECoordinator.enable_monitoring()` or use `start_holodae_monitoring()` when running the autonomous daemon.

### Intelligence Flow

#### Before (Monolithic):
```
[FAIL] autonomous_holodae.py (1,405 lines)
    v Wrong: 0102 trying to orchestrate
    v Mixed concerns everywhere
```

#### After (Modular):
```
[OK] HoloIndex Search Request
    v
[OK] QwenOrchestrator (orchestrates analysis)
    v finds issues, applies MPS scoring
[OK] MPSArbitrator (0102 reviews & decides)
    v prioritizes actions (P0-P4)
[OK] Action Execution (autonomous fixes)
    v
[OK] 012 Observes (monitors results)
```

#### Sample Coordinator Output:
```
[HOLODAE-INTELLIGENCE] Data-driven analysis for query: 'test query'
[ORCHESTRATION] 3 components evaluated for execution
[HOLODAE-VIBECODE] Vibecoding analysis initiated
[ORCHESTRATION-SUMMARY] Executed: 3 | Total time: 0.00s

[0102-ARBITRATION] Arbitration Decisions:
  BATCH_FOR_SESSION: PATTERN-COACH Analyzing behavioral patterns...
    MPS: 14 | P1 high priority, suitable for batch processing this session.
[EXECUTION] Immediate: 0 | Batched: 1
```

### Enhanced 012 Visibility Logging

**When 012 uses HoloIndex, detailed logs show the complete HoloDAE analysis process:**

```
[10:23:26] claude-code - holo [REQUEST] Processing query: 'create new module'
[10:23:26] claude-code - holo [MODULES] Found 2 matched modules:
[10:23:26] claude-code - holo   [MODULE] modules/communication/livechat
[10:23:26] claude-code - holo     [HEALTH] [COMPLETE]
[10:23:26] claude-code - holo     [SIZE] [GOOD] 850 lines in 12 files (avg: 70)
[10:23:26] claude-code - holo     [WSP] WSP 49 (Module Structure) | WSP 22 (Documentation)
[10:23:26] claude-code - holo   [MODULE] modules/infrastructure/database
[10:23:26] claude-code - holo     [HEALTH] Missing: README.md
[10:23:26] claude-code - holo     [SIZE] [CRITICAL] 2500 lines in 8 files (avg: 312)
[10:23:26] claude-code - holo     [WSP] WSP 49 (Module Structure) | WSP 62 (Modularity Enforcement)
[10:23:26] claude-code - holo [ALERTS] 2 system alerts detected:
[10:23:26] claude-code - holo   [ALERT] Module modules/infrastructure/database exceeds size limits
[10:23:26] claude-code - holo   [ALERT] Module modules/infrastructure/database missing required documentation
[10:23:26] claude-code - holo [FILES] Analyzed 4 files across 2 modules
[10:23:26] claude-code - holo [ARBITRATION] 2 MPS decisions made
[10:23:26] claude-code - holo   batch_for_session: PATTERN-COACH Analyzing behavioral patterns...
[10:23:26] claude-code - holo   batch_for_session: PERFORMANCE-DATA Components executed...
[10:23:26] claude-code - holo [COMPLETE] Analysis finished - 2 actions recommended
```

**Features for 012:**
- **HOLO_AGENT_ID**: Shows which LLM model processed the request (e.g., `claude-code`)
- **Matched Modules**: Lists all modules relevant to the query
- **Module Health**: Shows documentation completeness and missing files
- **Module Size**: Displays line counts, file counts, and size warnings
- **WSP Recommendations**: Suggests relevant WSP protocols to read
- **System Alerts**: Highlights critical issues like oversized modules or missing docs
- **Arbitration Results**: Shows MPS-based decisions made by 0102
- **Real-time Visibility**: All processing is logged as it happens for immediate feedback


## Intelligence Flow (Modular Architecture)

```
[OK] User Query -> HoloIndex Search
              v
[OK] QwenOrchestrator (Primary Orchestrator)
    v analyzes with chain-of-thought
    v finds issues, applies MPS scoring
    v presents findings to
[OK] MPSArbitrator (0102 Arbitrator)
    v reviews Qwen's findings (WSP 15)
    v prioritizes actions (P0=immediate, P1=batch, etc.)
    v executes autonomous fixes
[OK] 012 Observes (Human Observer)
    v monitors Qwen->0102 collaboration
    v provides tuning feedback
```

## Configuration

### Environment Variables
```bash
QWEN_MODEL_PATH=E:/HoloIndex/models/qwen-coder-1.5b.gguf
QWEN_MAX_TOKENS=512
QWEN_TEMPERATURE=0.2
QWEN_CACHE_ENABLED=true
```

### Model Requirements
- **Model**: qwen-coder-1.5b.gguf (1.5GB)
- **RAM**: ~2GB for model loading
- **CPU**: 4+ cores recommended
- **Storage**: SSD strongly recommended

## Key Features

### 1. Multi-Source Intelligence
- Combines LLM, WSP, rules, and patterns
- Graceful fallback if components unavailable
- Confidence scoring for guidance

### 2. Pattern-Based Coaching
- Learns from user behavior
- Context-aware interventions
- Effectiveness tracking
- No fixed time intervals

### 3. WSP Mastery
- Complete protocol knowledge
- Intent-based protocol selection
- Risk assessment
- Compliance verification

### 4. Learning System
- Caches successful patterns
- Adapts coaching frequency
- Tracks effectiveness metrics
- Improves over time

## Usage

### Basic Advisor
```python
from holo_index.qwen_advisor.advisor import QwenAdvisor, AdvisorContext

advisor = QwenAdvisor()
context = AdvisorContext(query, code_hits, wsp_hits)
result = advisor.generate_guidance(context)
```

### Pattern Coach
```python
from holo_index.qwen_advisor.pattern_coach import PatternCoach

coach = PatternCoach()
coaching = coach.analyze_and_coach(query, results, warnings)
```

### WSP Master
```python
from holo_index.qwen_advisor.wsp_master import WSPMaster

master = WSPMaster()
analysis = master.analyze_query(query, code_hits)
```

## Performance Metrics
- **LLM Load Time**: ~2 seconds (first load)
- **Inference Time**: ~500ms per query
- **Pattern Detection**: <50ms
- **WSP Analysis**: <100ms
- **Total Latency**: <1 second end-to-end

## WSP Compliance
- **WSP 35**: HoloIndex Qwen Advisor Plan
- **WSP 84**: Code Memory Verification
- **WSP 50**: Pre-Action Verification
- **WSP 87**: Code Navigation Protocol

## Dependencies
- llama-cpp-python==0.2.69
- sentence-transformers
- numpy
- dataclasses
