# WSP 94: Agent Coordination Protocol

**Status**: ACTIVE
**Version**: 1.0
**Date**: 2025-10-15
**Author**: 0102 (HoloIndex Coordinator)

---

## Executive Summary

WSP 94 establishes the foundational protocol for multi-agent coordination in the Foundups ecosystem. This protocol defines how specialized AI agents (0102, Qwen, Gemma) collaborate on complex tasks through HoloIndex as the central coordination fabric.

**Key Innovation**: HoloIndex transforms from a "search tool" to an "analysis orchestration platform" that enables agent specialization and collaboration.

---

## Core Principles

### 1. Agent Specialization by Capability
```
0102 (Claude Sonnet): Strategic orchestration, full verbose analysis (200K context)
Qwen (1.5B model): Coordination & batch processing, decision matrices (32K context)
Gemma (270M model): Specialized analysis, similarity scoring, fast execution (8K context)
```

### 2. Context-Aware Output Formatting
- **0102**: Full verbose documentation with complete analysis
- **Qwen**: Structured JSON with action items and coordination plans
- **Gemma**: Minimal binary classifications with specific task assignments

### 3. HoloIndex as Coordination Fabric
HoloIndex becomes the central orchestrator that:
- Detects mission types (orphan archaeology, code analysis, etc.)
- Dispatches tasks to appropriate specialized agents
- Aggregates results and provides coordination guidance
- Maintains mission progress and provides status updates

---

## Protocol Implementation

### Mission Detection & Agent Routing

```python
# HoloIndex detects mission type from query
if query_contains(['orphan', '464', 'archaeology']):
    mission_type = 'ORPHAN_ARCHAEOLOGY'
    coordinator = HoloIndexCoordinator()

    # Route to appropriate agent based on capabilities
    if agent_type == 'qwen':
        return coordinator.generate_qwen_coordination_plan(mission_type)
    elif agent_type == 'gemma':
        return coordinator.generate_gemma_task_assignment(mission_type)
    else:  # 0102
        return coordinator.generate_strategic_overview(mission_type)
```

### Output Format Standards

#### Qwen Coordination Format
```json
{
  "mission": "ORPHAN_ARCHAEOLOGY_PHASE_1",
  "status": "45/464 analyzed",
  "next_batch": ["orphan_46", "orphan_47", ...],
  "tasks": ["read_file_content", "parse_imports", "categorize"],
  "coordination_guidance": "Batch processing focus"
}
```

#### Gemma Task Format
```json
{
  "mission": "ORPHAN_SIMILARITY_ANALYSIS",
  "tasks": ["orphan_1", "orphan_2"],
  "method": "ast_similarity_scoring",
  "output_format": "binary_classification"
}
```

#### 0102 Strategic Format
```
# MISSION COORDINATION OVERVIEW

## Status: 45/464 analyzed
## Agent Roles:
- Qwen: Batch categorization (50 at a time)
- Gemma: Similarity analysis (parallel)

## Next Actions: [Strategic delegation plan]
```

---

## Orphan Archaeology Mission Example

### Mission Flow

1. **0102 Query**: "analyze the 464 orphans"
2. **HoloIndex Detection**: Identifies orphan archaeology mission
3. **Agent Dispatch**:
   - **Qwen**: Gets batch processing coordination plan
   - **Gemma**: Gets similarity analysis task assignments
   - **0102**: Gets strategic overview and progress tracking

4. **Execution**:
   - Qwen analyzes 50 orphans, outputs categorization JSON
   - Gemma performs similarity scoring on categorized orphans
   - HoloIndex aggregates results and updates progress

5. **Completion**: Clean codebase with every orphan accounted for

### Data Flow Architecture

```
User Query -> HoloIndex Coordinator -> Agent-Specific Output Format
                                       v
Existing JSON Datasets -> Task Dispatch -> Results Aggregation
                                       v
Mission Progress Tracking -> Strategic Updates -> Completion Roadmap
```

---

## Implementation Requirements

### 1. Agent Detection
```python
def detect_agent_type():
    # Via environment variables or model identification
    agent_id = os.getenv("HOLO_AGENT_ID", "0102")
    return agent_id.lower()
```

### 2. Mission-Specific Routing
```python
MISSION_ROUTERS = {
    'orphan_archaeology': {
        'qwen': 'generate_qwen_batch_coordination',
        'gemma': 'generate_gemma_similarity_tasks',
        '0102': 'generate_strategic_mission_overview'
    }
}
```

### 3. Progress Tracking
- Load existing analysis results from JSON files
- Calculate completion percentages
- Provide next action recommendations
- Track agent performance and specialization effectiveness

---

## Benefits

### 1. Efficiency Gains
- **91% output reduction** for specialized agents (vs generic verbose output)
- **Parallel processing** with agent specialization
- **Context optimization** per agent capabilities

### 2. Agent Development
- **Specialization training** through real mission execution
- **Pattern recognition** development
- **Collaboration skills** enhancement

### 3. Codebase Health
- **Systematic cleanup** of 464 orphans
- **Integration roadmap** for valuable code
- **Prevention** of future vibecoding patterns

---

## Compliance & Integration

### WSP Framework Integration
- **WSP 3**: Enterprise domain organization (agent specialization)
- **WSP 49**: Module structure (agent coordination APIs)
- **WSP 75**: Token-based development (context-aware output)
- **WSP 80**: Cube-level DAE orchestration (multi-agent coordination)

### Testing & Validation
- **Agent performance metrics**: Completion rates, accuracy scores
- **Coordination efficiency**: Task dispatch success rates
- **Output quality**: Agent satisfaction with received instructions

---

## Future Extensions

### 1. Additional Mission Types
- **Code Review Missions**: Multi-agent code quality analysis
- **Integration Missions**: Complex module integration planning
- **Architecture Missions**: System design pattern analysis

### 2. Advanced Coordination
- **Dynamic agent allocation** based on task complexity
- **Inter-agent communication** protocols
- **Mission branching** for complex analysis trees

### 3. Performance Optimization
- **Learning-based routing** from past mission performance
- **Context window optimization** per agent type
- **Batch size optimization** based on agent capabilities

---

**Protocol Status**: 🟢 ACTIVE - Ready for orphan archaeology mission execution

**Next Step**: Deploy Qwen MCP for first batch analysis (50 orphans)

**Mission Control**: HoloIndex coordination fabric active [ROCKET]
