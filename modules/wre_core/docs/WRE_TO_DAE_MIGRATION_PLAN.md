# WRE to DAE Migration Plan

## Executive Summary
Migrate WRE (Windsurf Recursive Engine) from old agent system to new DAE (Decentralized Autonomous Entity) pattern memory architecture.

**Impact**: 93% token reduction (460K → 30K), 100-1000x faster operations
**Risk**: Medium - Requires careful orchestration to maintain backward compatibility

## Current State Analysis

### Agent Dependencies in WRE
The WRE currently imports and uses 7+ legacy agents across 14 files:

1. **orchestrator.py** (Primary Integration Point)
   - JanitorAgent → Maintenance DAE
   - LoremasterAgent → Knowledge DAE  
   - ChroniclerAgent → Infrastructure DAE
   - ComplianceAgent → Compliance DAE
   - TestingAgent → Compliance DAE
   - ScoringAgent → Knowledge DAE
   - DocumentationAgent → Documentation DAE

2. **Additional Agent Usage**
   - AgentActivationModule (agent_activation)
   - ModuleScaffoldingAgent (referenced but not directly imported)

### Files Requiring Refactoring
- `modules/wre_core/src/components/orchestration/orchestrator.py`
- `modules/wre_core/src/components/orchestration/agentic_orchestrator.py`
- `modules/wre_core/src/components/core/engine_core.py`
- `modules/wre_core/src/components/core/component_manager.py`
- `modules/wre_core/src/wre_pp_orchestrator.py`
- 9 other files with agent references

## Migration Strategy

### Phase 1: Create DAE Adapter Layer (Backward Compatibility)
Create adapter classes that maintain old agent interfaces while using DAE pattern memory underneath.

```python
# modules/wre_core/src/adapters/agent_to_dae_adapter.py
class JanitorAgent:
    """Adapter: Old JanitorAgent interface → Maintenance DAE"""
    def __init__(self):
        from modules.infrastructure.maintenance_operations_dae.src.maintenance_dae import MaintenanceOperationsDAE
        self.dae = MaintenanceOperationsDAE()
    
    def clean_workspace(self):
        return self.dae.recall_pattern("cleanup_automation")
```

### Phase 2: Agent-to-DAE Mapping

| Old Agent | DAE Replacement | Pattern Type |
|-----------|----------------|--------------|
| JanitorAgent | Maintenance DAE | cleanup_automation |
| LoremasterAgent | Knowledge DAE | wsp_knowledge, documentation |
| ChroniclerAgent | Infrastructure DAE | event_logging |
| ComplianceAgent | Compliance DAE | wsp_validation |
| TestingAgent | Compliance DAE | test_execution |
| ScoringAgent | Knowledge DAE | scoring_algorithms |
| DocumentationAgent | Documentation DAE | template_generation |
| ModuleScaffoldingAgent | Infrastructure DAE | module_scaffolding |

### Phase 3: Incremental Refactoring

#### Step 1: Update Imports (Non-Breaking)
```python
# OLD
from modules.infrastructure.janitor_agent.src.janitor_agent import JanitorAgent

# INTERMEDIATE (with adapter)
from modules.wre_core.src.adapters.agent_to_dae_adapter import JanitorAgent

# FINAL (direct DAE)
from modules.infrastructure.maintenance_operations_dae.src.maintenance_dae import MaintenanceOperationsDAE as JanitorAgent
```

#### Step 2: Refactor Agent Calls to Pattern Recalls
```python
# OLD: Computational approach
janitor = JanitorAgent()
result = janitor.clean_workspace()  # 15-25K tokens

# NEW: Pattern memory approach  
maintenance_dae = MaintenanceOperationsDAE()
result = maintenance_dae.recall_pattern("cleanup_automation")  # 50-200 tokens
```

#### Step 3: Update Health Check System
Replace `check_agent_health()` with DAE cube status check:
```python
def check_dae_health() -> Dict[str, bool]:
    """Check if all DAE cubes are operational"""
    dae_cubes = [
        ("Infrastructure", InfrastructureOrchestrationDAE),
        ("Compliance", ComplianceQualityDAE),
        ("Knowledge", KnowledgeLearningDAE),
        ("Maintenance", MaintenanceOperationsDAE),
        ("Documentation", DocumentationRegistryDAE)
    ]
    # Pattern-based health check (instant)
```

### Phase 4: Remove Legacy Code

1. Delete old agent directories after migration confirmed:
   - `modules/infrastructure/janitor_agent/`
   - `modules/infrastructure/loremaster_agent/`
   - `modules/infrastructure/chronicler_agent/`
   - `modules/infrastructure/compliance_agent/`
   - `modules/infrastructure/testing_agent/`
   - `modules/infrastructure/scoring_agent/`
   - `modules/infrastructure/documentation_agent/`

2. Remove agent activation logic (DAEs are always active)

## Implementation Timeline

### Week 1: Setup & Adapters
- [ ] Create adapter layer in `wre_core/src/adapters/`
- [ ] Test adapters with existing WRE functionality
- [ ] Document adapter patterns

### Week 2: Core Migration
- [ ] Migrate orchestrator.py to use adapters
- [ ] Update agentic_orchestrator.py
- [ ] Refactor engine_core.py

### Week 3: Complete Migration
- [ ] Update remaining 11 files
- [ ] Remove adapter layer (direct DAE usage)
- [ ] Performance testing

### Week 4: Cleanup
- [ ] Delete old agent implementations
- [ ] Update all documentation
- [ ] Final validation

## Success Metrics

1. **Token Reduction**: Achieve 90%+ reduction in WRE operations
2. **Speed**: 100x faster agent operations (pattern recall vs computation)
3. **Compatibility**: Zero breaking changes for WRE consumers
4. **Test Coverage**: Maintain 90%+ test coverage

## Risk Mitigation

1. **Backward Compatibility**: Use adapter pattern for gradual migration
2. **Testing**: Comprehensive test suite before each phase
3. **Rollback Plan**: Keep old agents until migration validated
4. **Documentation**: Update as we go, not at end

## WSP Compliance

- **WSP 50**: Pre-action verification at each step
- **WSP 64**: Violation prevention through adapters
- **WSP 49**: Maintain proper module structure
- **WSP 22**: Update ModLogs throughout migration
- **WSP 80**: Follow DAE architecture patterns

## Next Steps

1. Review and approve migration plan
2. Create adapter layer (Phase 1)
3. Begin incremental migration
4. Monitor and adjust based on results

---

*This migration follows WSP protocols and maintains system integrity while achieving 93% token reduction through DAE pattern memory architecture.*