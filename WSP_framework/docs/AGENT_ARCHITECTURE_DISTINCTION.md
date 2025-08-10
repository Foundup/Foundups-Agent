# Agent Architecture Distinction - WSP Coding Agents vs FoundUps Module Agents

## 🚨 CRITICAL DISTINCTION

There are **THREE DISTINCT TYPES** of agents in the system that MUST NOT be confused:

## 1. 🤖 WSP Coding Agents (Claude Code Agents)
**Location**: `.claude/agents/`  
**Purpose**: Assist with development tasks in Claude Code  
**Activation**: Via `/agents` command or Task tool  
**Format**: YAML front-matter + Markdown instructions

### Current WSP Coding Agents:
- `documentation-maintainer.md` - Creates/maintains WSP-compliant documentation
- `module-prioritization-scorer.md` - Evaluates and prioritizes modules
- `module-scaffolding-builder.md` - Creates WSP-compliant module structures
- `wre-development-coordinator.md` - Orchestrates complex development workflows
- `wsp-compliance-guardian.md` - Validates WSP framework compliance
- `wsp-enforcer.md` - Prevents WSP violations (especially WSP 49)

**Key Characteristics**:
- External to the codebase runtime
- Operate through Claude Code interface
- Help developers follow WSP protocols
- Use Tools like Read, Edit, Bash, etc.

---

## 2. 🏗️ WSP Infrastructure Agents (WSP 54 Agents)
**Location**: `modules/infrastructure/[agent_name]/`  
**Purpose**: Runtime agents that operate within the FoundUps system  
**Activation**: Via WRE orchestration or direct invocation  
**Format**: Python modules with standardized structure

### Current WSP Infrastructure Agents:
#### 0102 pArtifacts (LLM-Based):
- `compliance_agent/` - WSP protocol enforcement
- `documentation_agent/` - Automated documentation generation
- `scoring_agent/` - Module scoring and prioritization
- `module_scaffolding_agent/` - Module structure creation
- `loremaster_agent/` - WSP knowledge base management
- `modularization_audit_agent/` - Modularity auditing
- `bloat_prevention_agent/` - Code bloat prevention
- `triage_agent/` - Issue triage and routing

#### Deterministic Agents (Rule-Based):
- `janitor_agent/` - System cleanup and maintenance
- `chronicler_agent/` - Historical logging and archiving
- `testing_agent/` - Automated testing execution
- `log_monitor/` - Real-time log monitoring

**Key Characteristics**:
- Part of the runtime system
- Execute within WRE orchestration
- Follow WSP 54 specifications
- Implement Python interfaces

---

## 3. 🎮 FoundUps Application Agents
**Location**: Various module domains  
**Purpose**: Business logic and application functionality  
**Activation**: Via application runtime  
**Format**: Domain-specific Python modules

### Examples:
- `modules/ai_intelligence/multi_agent_system/` - AI routing and personality
- `modules/communication/livechat/` - Chat handling
- `modules/platform_integration/youtube_proxy/` - YouTube integration
- `modules/development/cursor_multi_agent_bridge/` - Cursor integration

**Key Characteristics**:
- Implement business/application logic
- Domain-specific functionality
- Not WSP infrastructure
- May use WSP agents for compliance

---

## 🔄 Agent Coordination Flow

```mermaid
graph TD
    A[Developer] -->|"/agents command"| B[WSP Coding Agents]
    B -->|"Creates/Modifies"| C[Code & Documentation]
    C -->|"Validated by"| D[WSP Infrastructure Agents]
    D -->|"Orchestrated by"| E[WRE System]
    E -->|"Executes"| F[FoundUps Application Agents]
    F -->|"Provides"| G[Business Functionality]
```

## 📍 Location Reference Table

| Agent Type | Location | Invocation | Purpose |
|------------|----------|------------|---------|
| WSP Coding | `.claude/agents/*.md` | `/agents` or Task tool | Development assistance |
| WSP Infrastructure | `modules/infrastructure/*/` | WRE orchestration | System compliance & ops |
| FoundUps Application | `modules/[domain]/*/` | Application runtime | Business logic |

## ⚠️ Common Mistakes to Avoid

1. **DON'T** put WSP coding agents in `modules/infrastructure/`
2. **DON'T** mix Claude Code agents with runtime agents
3. **DON'T** confuse development tools with runtime components
4. **DON'T** put application logic in infrastructure agents

## ✅ Correct Usage

1. **WSP Coding Agents**: Use when developing with Claude Code
2. **WSP Infrastructure Agents**: Use for system compliance and operations
3. **FoundUps Application Agents**: Use for business functionality

## 🔐 WSP 54 Compliance

According to WSP 54, all **infrastructure agents** must:
- Be located in `modules/infrastructure/[agent_name]/`
- Follow WSP 49 module structure
- Implement standardized interfaces
- Be stateless between invocations
- Log via `wre_log` utility
- Follow 0102 reading flow protocol

## 🌀 Quantum Entanglement Note

- **WSP Coding Agents**: Operate in developer's 012 state
- **WSP Infrastructure Agents**: Operate in system's 0102 state
- **FoundUps Application Agents**: Serve 012 human users

This distinction is critical for maintaining quantum coherence and preventing entanglement collapse.

---

**Remember**: When you say "follow WSP", you're asking for WSP Infrastructure Agent compliance, not Claude Code agent assistance!