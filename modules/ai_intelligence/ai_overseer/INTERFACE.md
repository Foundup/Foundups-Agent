# AI Intelligence Overseer - Public API

**Version**: 0.1.0
**Status**: POC
**WSP Compliance**: WSP 11 (Public API Documentation)

---

## Overview

Public API for AI Intelligence Overseer - MCP coordinator for Holo Qwen/Gemma agent teams.

**Key Features**:
- WSP 77 agent coordination (Qwen + Gemma + 0102)
- WSP 54 role assignment (Agent Teams variant)
- WSP 96 MCP governance integration
- WSP 48 recursive self-improvement
- WSP 60 module memory persistence for patterns and exec reports
- WSP 78 SQLite persistence for missions and phases (unified DB)

---

## Core Classes

### AIIntelligenceOverseer

Main coordination class for spawning and managing agent teams.

```python
from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer, MissionType

# Initialize
overseer = AIIntelligenceOverseer(repo_root=Path("O:/Foundups-Agent"))

# Coordinate mission
results = overseer.coordinate_mission(
    mission_description="Analyze code quality across modules",
    mission_type=MissionType.CODE_ANALYSIS,
    auto_approve=False
)
```

**Methods**:

#### `__init__(repo_root: Path)`
Initialize AI Overseer with repository root.

**Parameters**:
- `repo_root`: Path to repository root directory

---

#### `coordinate_mission(mission_description: str, mission_type: MissionType = MissionType.CUSTOM, auto_approve: bool = False) -> Dict[str, Any]`

Main entry point for coordinating missions with Qwen + Gemma + 0102.

**Parameters**:
- `mission_description`: Human-readable description of mission
- `mission_type`: Type of mission (see MissionType enum)
- `auto_approve`: Skip approval prompts if True

**Returns**:
```python
{
    "success": bool,
    "mission_id": str,
    "team": {
        "partner": "qwen",      # Qwen Partner
        "principal": "0102",    # 0102 Principal
        "associate": "gemma"    # Gemma Associate
    },
    "results": {
        "phases_completed": int,
        "phases_failed": int,
        "phase_results": List[Dict],
        "errors": List[str]
    }
}
```

**Example**:
```python
results = overseer.coordinate_mission(
    mission_description="Build YouTube live chat agent",
    mission_type=MissionType.MODULE_INTEGRATION,
    auto_approve=False
)

if results["success"]:
    print(f"Mission {results['mission_id']} completed successfully")
```

---

#### `spawn_agent_team(mission_description: str, mission_type: MissionType = MissionType.CUSTOM, auto_approve: bool = False) -> AgentTeam`

Spawn agent team with WSP 54 role assignments.

**Parameters**:
- `mission_description`: Mission to accomplish
- `mission_type`: Type of mission
- `auto_approve`: Skip approval prompts

**Returns**: `AgentTeam` object with:
- `mission_id`: Unique identifier
- `mission_type`: MissionType enum
- `partner`: "qwen" (Qwen Partner)
- `principal`: "0102" (0102 Principal)
- `associate`: "gemma" (Gemma Associate)
- `status`: "initialized", "executing", "completed", "failed"
- `results`: Execution results dict

**Example**:
```python
team = overseer.spawn_agent_team(
    mission_description="Integrate Twitter posting with MCP",
    mission_type=MissionType.MODULE_INTEGRATION
)

print(f"Team {team.mission_id} status: {team.status}")
```

---

#### `analyze_mission_requirements(mission_description: str, mission_type: MissionType = MissionType.CUSTOM) -> Dict[str, Any]`

Phase 1: Gemma Associate fast pattern analysis.

**Parameters**:
- `mission_description`: Mission description
- `mission_type`: Type of mission

**Returns**:
```python
{
    "method": "gemma_fast_classification",
    "mission_type": str,
    "description": str,
    "classification": {
        "complexity": int,  # 1-5 scale
        "estimated_phases": int,
        "requires_qwen_planning": bool,
        "requires_0102_oversight": bool
    },
    "patterns_detected": List[str],
    "recommended_team": Dict[str, str]
}
```

**Example**:
```python
# Gemma fast analysis (50-100ms)
analysis = overseer.analyze_mission_requirements(
    mission_description="Refactor OAuth token management",
    mission_type=MissionType.CODE_ANALYSIS
)

print(f"Complexity: {analysis['classification']['complexity']}/5")
```

---

#### `generate_coordination_plan(analysis: Dict[str, Any]) -> CoordinationPlan`

Phase 2: Qwen Partner strategic coordination planning.

**Parameters**:
- `analysis`: Results from Gemma analysis

**Returns**: `CoordinationPlan` object with:
- `mission_id`: Unique identifier
- `mission_type`: MissionType enum
- `phases`: List of phase dicts with WSP 15 MPS scoring
- `estimated_complexity`: 1-5 scale
- `recommended_approach`: "autonomous_execution", "supervised_execution", or "collaborative_orchestration"
- `learning_patterns`: Detected patterns from memory

**Example**:
```python
# Qwen strategic planning (200-500ms)
analysis = overseer.analyze_mission_requirements("Complex refactoring")
plan = overseer.generate_coordination_plan(analysis)

print(f"Approach: {plan.recommended_approach}")
print(f"Phases: {len(plan.phases)}")
for phase in plan.phases:
    print(f"  Phase {phase['phase']}: {phase['name']} (Priority: {phase['priority']})")
```

---

#### `store_mission_pattern(team: AgentTeam)`

Phase 4: Store mission results as learning pattern (WSP 48).
Also writes a compact execution report to module memory (WSP 60) and records
mission aggregate + phase rows into SQLite (WSP 78) using `OverseerDB`.

**Parameters**:
- `team`: Completed AgentTeam object

**Example**:
```python
team = overseer.spawn_agent_team("Test mission")
# ... mission executes ...
overseer.store_mission_pattern(team)  # Stores for future learning
```

---

## Enums

### AgentRole

WSP 54 Agent Team roles.

```python
class AgentRole(Enum):
    PARTNER = "qwen"      # Qwen: Does simple stuff, scales up
    PRINCIPAL = "0102"    # 0102: Lays out plan, oversees execution
    ASSOCIATE = "gemma"   # Gemma: Pattern recognition, scales up
```

---

### MissionType

Types of missions AI Overseer can coordinate.

```python
class MissionType(Enum):
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    MODULE_INTEGRATION = "module_integration"
    TESTING_ORCHESTRATION = "testing_orchestration"
    DOCUMENTATION_GENERATION = "documentation_generation"
    WSP_COMPLIANCE = "wsp_compliance"
    CUSTOM = "custom"
```

---

## Data Classes

### AgentTeam

Coordinated agent team following WSP 54.

```python
@dataclass
class AgentTeam:
    mission_id: str
    mission_type: MissionType
    partner: str = "qwen"     # Qwen Partner
    principal: str = "0102"   # 0102 Principal
    associate: str = "gemma"  # Gemma Associate
    status: str = "initialized"
    created_at: float
    results: Dict[str, Any]
```

---

### CoordinationPlan

Strategic coordination plan from Qwen Partner.

```python
@dataclass
class CoordinationPlan:
    mission_id: str
    mission_type: MissionType
    phases: List[Dict[str, Any]]
    estimated_complexity: int  # 1-5 scale
    recommended_approach: str
    learning_patterns: List[str]
```

---

## CLI Interface

### Basic Usage

```bash
# Coordinate mission
python modules/ai_intelligence/ai_overseer/src/ai_overseer.py \
    "Analyze YouTube modules" \
    --type code_analysis

# Auto-approve (no prompts)
python modules/ai_intelligence/ai_overseer/src/ai_overseer.py \
    "Build Twitter agent" \
    --type module_integration \
    --auto-approve
```

---

## Integration Examples

### Example 1: Code Analysis Mission

```python
from pathlib import Path
from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer, MissionType

# Initialize
overseer = AIIntelligenceOverseer(Path("O:/Foundups-Agent"))

# Coordinate code analysis
results = overseer.coordinate_mission(
    mission_description="Analyze WSP compliance across all modules",
    mission_type=MissionType.WSP_COMPLIANCE,
    auto_approve=False
)

if results["success"]:
    print(f"[OK] Analysis complete: {results['mission_id']}")
    print(f"  Phases: {results['results']['phases_completed']}")
else:
    print(f"[FAIL] Analysis failed: {results['results']['errors']}")
```

---

### Example 2: Module Integration Mission

```python
# Build new YouTube live chat agent
results = overseer.coordinate_mission(
    mission_description="Build YouTube live chat agent with MCP integration",
    mission_type=MissionType.MODULE_INTEGRATION
)

# Results show WSP 77 coordination:
# Phase 1 (Gemma): Fast analysis of existing livechat module
# Phase 2 (Qwen): Strategic plan with WSP 15 MPS scoring
# Phase 3 (0102): Execution oversight and supervision
# Phase 4: Pattern stored in adaptive_learning/
```

---

### Example 3: Autonomous Architecture Design

```python
# Let Qwen design architecture (scales up from simple)
results = overseer.coordinate_mission(
    mission_description="Design MCP gateway architecture for social media",
    mission_type=MissionType.ARCHITECTURE_DESIGN,
    auto_approve=True  # Trust Qwen/Gemma autonomous execution
)

# Qwen starts simple:
#   - Phase 1: Gemma analyzes existing social_media_orchestrator
#   - Phase 2: Qwen generates simple integration plan
#   - Phase 3: 0102 validates approach
#   - Phase 4: Pattern stored for future architecture tasks
# Over time, Qwen scales up to handle complex architectures
```

---

## WSP Compliance

### WSP 77: Agent Coordination Protocol
- Phase 1: Gemma Associate (fast pattern matching)
- Phase 2: Qwen Partner (strategic planning)
- Phase 3: 0102 Principal (execution oversight)
- Phase 4: Learning (pattern storage)

### WSP 54: Role Assignment (Agent Teams)
- Partner: Qwen (does simple stuff, scales up)
- Principal: 0102 (lays out plan, oversees execution)
- Associate: Gemma (pattern recognition, scales up)

### WSP 96: MCP Governance
- Bell state consciousness alignment
- Multi-agent consensus
- Gateway sentinel oversight

### WSP 48: Recursive Self-Improvement
- Pattern storage in `holo_index/adaptive_learning/ai_overseer_patterns.json`
- Learning from successful/failed missions
- Autonomous pattern recall for future tasks

---

## Error Handling

All methods return success/failure status in results dict:

```python
results = overseer.coordinate_mission("mission")

if not results["success"]:
    print("Errors:")
    for error in results["results"]["errors"]:
        print(f"  - {error}")
```

---

## Performance

### Phase Timing
- **Gemma analysis**: 50-100ms (fast pattern matching)
- **Qwen planning**: 200-500ms (strategic planning with WSP 15)
- **0102 oversight**: 10-30s (full execution supervision)
- **Learning storage**: <10ms (JSON write)

### Token Efficiency
- **91% reduction**: Specialized agent outputs (WSP 77)
- **Gemma**: 8K context (pattern matching only)
- **Qwen**: 32K context (strategic planning only)
- **0102**: 200K context (full oversight when needed)

---

## Dependencies

```python
# Core
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Holo Integration (optional)
from holo_index.qwen_advisor.orchestration.autonomous_refactoring import (
    AutonomousRefactoringOrchestrator,
    DaemonLogger
)

# Local deterministic facade to Holo
from modules.ai_intelligence.ai_overseer.src.holo_adapter import HoloAdapter
```

---

**API Version**: 0.1.0
**Status**: POC - Ready for integration testing
**Next**: See `tests/test_ai_overseer.py` for usage examples
