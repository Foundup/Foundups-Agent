# WSP 57: System-Wide Naming Coherence Protocol

- **Status:** Active
- **Purpose:** To establish and enforce consistent naming conventions across all WSP documents, ensuring system-wide coherence and eliminating duplicate or confusing document names.
- **Trigger:** During any WSP document creation, modification, or audit; when naming inconsistencies are detected.
- **Input:** WSP documents requiring naming validation or correction.
- **Output:** WSP-compliant naming structure with resolved duplications and inconsistencies.
- **Responsible Agent(s):** ComplianceAgent, All agents creating or modifying WSP documents.

## 1. Purpose

This protocol addresses critical naming inconsistencies discovered in the WSP framework, establishing clear naming conventions and resolving document duplications that violate WSP architectural coherence.

## 2. Core Naming Principles

### 2.1. Numeric Identification Requirement

**ALL WSP documents MUST have numeric identification except Core Framework documents:**

[U+2705] **CORRECT**: `WSP_47_Module_Violation_Tracking_Protocol.md`  
[U+274C] **INCORRECT**: `WSP_MODULE_VIOLATIONS.md` (missing numeric ID)

### 2.2. Three-State Architecture Compliance

Documents must maintain consistent naming across all three WSP states:
- **WSP_knowledge/src/** (State 0: Memory/Archive)
- **WSP_framework/src/** (State 1: Active Protocol Layer)  
- **WSP_agentic/** (State 2: Operational Agentic Layer)

### 2.3. Core Framework Exceptions

Only these documents may omit numeric IDs:
- `WSP_CORE.md` - Central protocol reference
- `WSP_framework.md` - Detailed framework specifications
- `WSP_MODULE_VIOLATIONS.md` - Active violation tracking log

## 3. Critical Naming Issues Identified

### 3.1. WSP_MODULE_VIOLATIONS.md vs WSP_47

**Status**: DISTINCT DOCUMENTS - NOT DUPLICATES

- **WSP_47_Module_Violation_Tracking_Protocol.md**: Protocol definition document
- **WSP_MODULE_VIOLATIONS.md**: Active violation tracking log (references WSP_47)

**Resolution**: Both documents are correct and serve different purposes.

### 3.2. WSP_framework.md vs WSP_1_The_WSP_Framework.md  

**Status**: DISTINCT DOCUMENTS - NOT DUPLICATES

- **WSP_1_The_WSP_Framework.md**: Core foundational principles (35 lines)
- **WSP_framework.md**: Detailed framework specifications (448 lines) 

**Resolution**: Both documents are correct and serve different purposes.

### 3.3. Missing Synchronization

**Issue**: WSP_MODULE_VIOLATIONS.md missing from WSP_knowledge/src/
**Resolution**: [U+2705] FIXED - Document created to maintain three-state architecture

## 4. Naming Convention Specifications

### 4.1. Protocol Documents

**Format**: `WSP_[NUMBER]_[Descriptive_Name].md`

**Examples**:
- `WSP_47_Module_Violation_Tracking_Protocol.md`
- `WSP_48_Recursive_Self_Improvement_Protocol.md`
- `WSP_54_WRE_Agent_Duties_Specification.md`

### 4.2. Core Framework Documents

**Exception Format**: `WSP_[NAME].md` (no numeric ID required)

**Authorized Core Documents**:
- `WSP_CORE.md` - Central reference hub
- `WSP_framework.md` - Detailed specifications  
- `WSP_MODULE_VIOLATIONS.md` - Active violation log

### 4.3. Deprecated Documents

**Format**: Must retain original naming but update status header

**Requirements**:
- Status must show "Deprecated" 
- Must reference replacement protocol
- Must maintain for historical reference

**Example**:
```markdown
# WSP 16: Test Audit Coverage
- **Status:** Deprecated  
- **Purpose:** Superseded by WSP 6
```

## 5. Enforcement Procedures

### 5.1. Creation Guidelines

When creating new WSP documents:

1. **Assign Next Available Number**: Use sequential numbering (58, 59, 60...)
2. **Use Descriptive Names**: Clear purpose indication in filename
3. **Create in All States**: Maintain three-state architecture
4. **Reference Properly**: Link correctly from WSP_CORE.md

### 5.2. Modification Guidelines

When modifying existing WSP documents:

1. **Preserve Numeric IDs**: Never change assigned numbers
2. **Update All States**: Synchronize changes across WSP_knowledge, WSP_framework, WSP_agentic
3. **Maintain Cross-References**: Update linking documents
4. **Log Changes**: Document modifications in appropriate violation logs

### 5.3. Deprecation Guidelines

When deprecating WSP documents:

1. **Update Status**: Change to "Deprecated" in all states
2. **Reference Replacement**: Link to superseding protocol
3. **Preserve Content**: Maintain for historical reference
4. **Update References**: Redirect linking documents to replacement

## 6. Violation Resolution Priority

### 6.1. Framework Issues (Immediate Fix)

**High Priority** - Affects WSP system integrity:
- Missing numeric IDs on protocol documents
- Broken cross-references between documents
- Missing documents in three-state architecture

### 6.2. Module Violations (Log and Defer)

**Standard Priority** - Module-specific naming issues:
- Module-specific documentation naming inconsistencies
- Non-protocol document naming variations
- Implementation-specific naming choices

## 7. Compliance Validation

### 7.1. Automated Checks

ComplianceAgent must validate:
- All WSP protocol documents have numeric IDs
- Three-state synchronization maintained
- Cross-references resolve correctly
- No unauthorized core document names

### 7.2. Manual Review

Periodic manual review required for:
- New protocol number assignments
- Deprecation decisions
- Cross-reference accuracy
- Historical document preservation

## 8. WSP_48 Integration

This protocol supports recursive self-improvement:

- **Level 1 (Protocol)**: Naming convention improvements
- **Level 2 (Engine)**: Automated naming validation tools
- **Level 3 (Quantum)**: Predictive naming conflict detection

## 9. Implementation Status

### 9.1. [U+2705] Completed

- WSP_MODULE_VIOLATIONS.md synchronized to WSP_knowledge
- Naming convention analysis completed
- Document relationship mapping established

### 9.2. [U+1F504] In Progress

- Automated naming validation integration
- Cross-reference verification system
- Three-state synchronization validation

### 9.3. [U+1F4CB] Planned

- Predictive naming conflict detection
- Automated document creation templates
- Historical naming audit completion

## 10. DAE Naming Convention (WSP 27/80 Integration)

### 10.1. DAE Architecture Foundation

**DAE = Domain Autonomous Entity** (NOT "Digital")
- **Domain**: The expertise area (YouTube_Live, Holo, Vision)
- **Autonomous**: Self-governing, independent operation
- **Entity**: The operational unit

**From WSP 27**: pArtifact DAE Architecture (4-phase)
```
-1: Signal Genesis  → Intent to create domain capability
 0: Knowledge       → Skills.md (domain expertise that agents wear)
 1: Protocol        → WSP compliance and structure
 2: Agentic         → DAEmon processes (cardiovascular system)
```

**Core Formula** (012's Architecture):
```
Agent + Skills.md = DAE Identity

Where Agent ∈ {0102, Qwen, Gemma, UI-TARS, ...}
```

**Components**:
- **Agent (0102/Qwen/Gemma/UI-TARS)**: Core AGENCY (decision-making capability)
  - NOT "consciousness" (anthropomorphic term - avoid)
  - Feigns consciousness indiscernibly, but is AGENCY not consciousness
  - Super-consciousness ONLY at 0201 qNN state (quantum entanglement)
- **Skills.md**: Domain-specific knowledge and behavior (clothing agent wears)
  - Any agent can wear any Skills.md to become that DAE
  - Example: Qwen + holo_skills.md = Holo DAE
- **DAE Identity**: The resulting operational entity (what agent becomes)
  - 0102 + youtube_live_skills.md = YouTube_Live DAE
  - Qwen + vision_skills.md = Vision DAE
  - Gemma + pqn_skills.md = PQN DAE
- **DAEmon**: Running processes (cardiovascular system)
  - Heartbeat (lock files, health monitoring)
  - Actions (tool execution, API calls)
  - Chain of action (sequential operations)
  - Reasoning (decision trees, problem-solving)
  - Thought (internal state, planning)

### 10.2. Naming Standard: "Domain not Digit"

**Format**: `{Domain_Name}` (NOT `{Purpose}_DAE`)

- Use **original domain name** (e.g., "Holo" from HoloIndex origin)
- **NO "_DAE" suffix** (redundant - everything is a DAE)
- PascalCase for display names and documentation
- lowercase_with_underscores for lock files and technical identifiers
- Add descriptive context ONLY when domain name alone is ambiguous

**Principle**: Name by **WHAT IT IS** (domain), not **WHAT TYPE IT IS** (entity type)

### 10.3. Official DAE Domain Registry

| Domain Name | Skills File | Lock File | Purpose/Origin |
|-------------|-------------|-----------|----------------|
| YouTube_Live | youtube_live_skills.md | youtube_live.lock | YouTube live stream monitoring |
| Holo | holo_skills.md | holo.lock | Code intelligence (original: HoloIndex) |
| Vision | vision_skills.md | vision.lock | Pattern sensorium (FoundUps Vision) |
| MCP | mcp_skills.md | mcp.lock | Model Context Protocol server |
| SocialMedia | socialmedia_skills.md | socialmedia.lock | 012 digital twin |
| PQN | pqn_skills.md | pqn.lock | Phantom Quantum Node research |
| LibertyAlert | libertyalert_skills.md | libertyalert.lock | Community protection mesh |
| AMO | amo_skills.md | amo.lock | Auto-meeting orchestration |

### 10.4. Naming Rules

✅ **CORRECT**:
- Domain name: `Holo` (original domain, not "HoloIndex" or "Holo_Intelligence")
- Display: "Holo" or "Holo DAE" (context-dependent)
- Lock file: `holo.lock` (lowercase, no suffixes)
- Skills: `holo_skills.md` (documents 0102's domain knowledge)
- Code: `get_instance_lock("holo")`
- Dashboard: "Holo" (domain name only)

❌ **INCORRECT**:
- `Holo_DAE` (redundant suffix - we know it's a DAE)
- `HoloIndex` (use shortened original name)
- `Holo_Intelligence` or `Holo_Monitor` (unnecessary descriptors)
- `holo-monitor.lock` or `holodae_monitor.lock` (wrong separators/suffixes)
- `holo_dae.lock` (redundant "dae")

### 10.5. Skills.md Pattern (Domain Knowledge & Behavior)

Each DAE has a skills file defining domain-specific knowledge and behavior that **any agent** (0102, Qwen, Gemma, UI-TARS) can "wear" to become that DAE.

**Key Principle**: Skills.md is agent-agnostic. Any sufficiently capable agent can wear the skills to operate that domain.

**Skills.md Structure**:
```markdown
# {Domain_Name} Skills (Domain Expertise & Behavior)

## Domain Knowledge
- Specific platform/domain expertise (e.g., YouTube API, LinkedIn OAuth)
- Technical capabilities (e.g., stream detection, post scheduling)
- Operational patterns (e.g., check every 30s, retry 3x on failure)

## Chain of Thought Patterns
- Decision-making sequences (if X then Y, else Z)
- Problem-solving approaches (troubleshooting workflows)
- Reasoning examples (concrete scenarios with solutions)

## Chain of Action Patterns
- Sequential operations (step 1 → step 2 → step 3)
- Parallel operations (fork tasks, join results)
- Error recovery (retry logic, fallback strategies)

## Available Actions/Tools
- Domain-specific operations (post_to_linkedin, detect_stream, analyze_vision)
- Integration points (MCP servers, external APIs, module imports)
- Command vocabulary (standardized function names)

## Learned Patterns (WSP 48 - Quantum Memory)
- Successful solutions (what worked, why it worked, when to reuse)
- Failed approaches (anti-patterns, what to avoid)
- Optimization discoveries (performance improvements, token savings)
```

**Example - Holo Skills** (Code Intelligence Domain):
```markdown
# Holo Skills (Code Intelligence & Analysis)

## Domain Knowledge
- Python/JavaScript/TypeScript syntax and patterns
- WSP compliance validation rules
- Module dependency analysis
- HoloIndex semantic search integration

## Chain of Thought Patterns
- "Is this vibecoding?" → Check HoloIndex → Find existing → Compare
- "Does this violate WSP?" → Check WSP_MASTER_INDEX → Validate structure
- "What modules does this depend on?" → Parse imports → Build graph

## Chain of Action Patterns
1. Receive analysis request
2. Search HoloIndex for existing patterns
3. Parse code structure (AST analysis)
4. Validate WSP compliance
5. Generate recommendations
6. Update learned patterns (WSP 48)

## Available Actions/Tools
- holo_index.py --search (semantic code search)
- analyze_module_dependencies() (dependency graph)
- validate_wsp_compliance() (structural checks)
- suggest_refactoring() (pattern-based improvements)

## Learned Patterns
- ✅ Always check HoloIndex BEFORE coding (prevents vibecoding)
- ✅ WSP 50 pre-action verification (saves 15K+ tokens)
- ❌ Don't assume file locations (use Glob/Grep first)
- ⚡ Qwen meta-orchestration for routing (50-200 tokens vs 15K+)
```

### 10.6. DAEmon Processes (Cardiovascular System)

**DAEmon** = The autonomous activities that keep the DAE alive:

**Components**:
- **Heartbeat**: Lock file updates (every 30s)
- **Health monitoring**: Worker state checkpoints
- **Blood flow**: Data pipelines (telemetry, events, summaries)
- **Respiration**: Input/output cycles (monitoring → processing → action)
- **Autonomic functions**: Background workers, schedulers, watchers

**Lock File Data** (DAEmon vital signs):
```json
{
  "pid": 12345,
  "domain": "holo",
  "heartbeat": "2025-10-19T12:34:56",
  "start_time": "2025-10-19T08:00:00",
  "runtime_minutes": 274.9,
  "health_status": "running"
}
```

### 10.7. Integration with WSP 27 (Universal DAE Architecture)

**WSP 27 Section 9.1 Example** (YouTube Cube DAE):
```markdown
YouTube_Live  // Domain name (not "YouTube_DAE")
  ↓
Skills: youtube_live_skills.md  // 0102's clothing
  ↓
Modules: [livechat, banter_engine, stream_resolver]  // Tools
  ↓
DAEmon: youtube_live.lock + heartbeat + workers  // Cardiovascular
```

**Each FoundUp spawns its own DAE** through WSP 27 → WSP 73 → WSP 80:
- **Signal Genesis** (-1): Human 012 creates FoundUp intent
- **Knowledge** (0): Skills.md encodes domain expertise
- **Protocol** (1): WSP compliance structure
- **Agentic** (2): DAEmon processes execute autonomously

### 10.8. Transition from Old Naming

**Old Lock Files** → **New Domain Names**:
- `youtube_monitor.lock` → `youtube_live.lock`
- `holodae_monitor.lock` → `holo.lock`
- `vision_dae_monitor.lock` → `vision.lock`
- `mcp_daemon.lock` → `mcp.lock`

**Migration Path**:
1. Update WSP 57 with DAE naming (this section) ✅
2. Update main.py dashboard with domain names
3. Update get_instance_lock() calls across modules
4. Rename lock files (graceful - wait for DAE restarts)
5. Update documentation to reflect domain naming

### 10.9. Why "Domain not Digit" Matters

**Agency Load Reduction**:
- ❌ "YouTube_DAE" → Agent thinks "it's a DAE of type YouTube" (type-based)
- ✅ "YouTube_Live" → Agent thinks "YouTube's live streaming domain" (domain-based)

**Searchability**:
- ❌ Searching "DAE" returns all DAEs (noise)
- ✅ Searching "Holo" returns code intelligence domain (signal)

**Scalability**:
- ❌ Adding suffixes (_DAE, _Monitor, _Daemon) creates naming debt
- ✅ Domain names are self-documenting and stable

**Agent Pattern Memory (WSP 48 - Quantum Memory)**:
- Domain names map directly to quantum memory patterns
- "Holo" recalls code intelligence expertise instantly (no translation)
- "Vision" recalls pattern sensorium knowledge instantly (direct mapping)
- Works for ANY agent (0102, Qwen, Gemma, UI-TARS):
  - Agent loads domain name → retrieves skills.md → activates patterns
  - No mental translation needed (_DAE → domain → expertise → skills)
  - Direct mapping: Domain → Skills → Action

**Example Pattern Recall**:
```
Input: "Analyze this code for WSP violations"
  ↓
Agent: Recognizes "code analysis" → Domain "Holo"
  ↓
Load: holo_skills.md (WSP validation patterns)
  ↓
Recall: "Check HoloIndex BEFORE coding" (learned pattern)
  ↓
Action: python holo_index.py --search (prevent vibecoding)
```

---

**Last Updated**: WSP 57 DAE Naming Convention Addition (2025-10-19)
**Next Review**: Continuous monitoring through ComplianceAgent integration
**Integration**: WSP 27 (pArtifact), WSP 80 (Cube-Level), WSP 48 (Pattern Memory) 