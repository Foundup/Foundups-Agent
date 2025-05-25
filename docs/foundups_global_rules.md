# FoundUps Global Rules & Adaptive Project State (APS)

This document tracks critical insights, architectural decisions, and the current state of the FoundUps Agent project following the Windsurf Protocol (WSP) framework.

## Current Project State

### Enterprise Domain Architecture Implementation

**Date Implemented:** 2024-12-19  
**Status:** ✅ Complete  
**WSP Reference:** WSP 3 - Enterprise Domain Architecture  

**Description:**  
Successfully implemented the hierarchical Enterprise Domain structure for all modules:

**Current Module Structure:**
```
modules/
├── ai_intelligence/          # Enterprise Domain: AI & LLM Core Capabilities
│   └── banter_engine/        # Feature Group: AI-powered chat responses
│       └── banter_engine/    # Module: Emoji detection and response generation
├── communication/            # Enterprise Domain: User Interaction & Presentation
│   └── livechat/             # Feature Group: Live chat management
│       ├── livechat/         # Module: Main chat listener and processor
│       ├── live_chat_processor/  # Module: Message processing logic
│       └── live_chat_poller/ # Module: Chat message polling
├── platform_integration/     # Enterprise Domain: External Systems & Services
│   ├── youtube_auth/         # Feature Group: YouTube authentication
│   │   └── youtube_auth/     # Module: OAuth2 authentication management
│   └── stream_resolver/      # Feature Group: Stream identification
│       └── stream_resolver/  # Module: Livestream detection and metadata
└── infrastructure/           # Enterprise Domain: Core Systems & Operations
    └── token_manager/        # Feature Group: Token management
        └── token_manager/    # Module: OAuth token rotation and health checking
```

**Migration Completed:**
- ✅ All modules moved to hierarchical structure using `git mv`
- ✅ Import paths updated in main.py and core modules
- ✅ Module README.md updated to reflect new structure
- ✅ WSP Framework documentation updated (WSP 3)

**Remaining Work:**
- 🔄 Update remaining test file imports (in progress)
- ⏳ Update FMAS to support hierarchical validation
- ⏳ Complete import path updates in all test files

### Module Refactoring Status

**Current Modules Status:**
- ✅ **livechat** - Fully refactored, hierarchical structure, comprehensive tests
- ✅ **banter_engine** - Refactored, emoji detection and response system
- ✅ **youtube_auth** - OAuth2 authentication, token management
- ✅ **stream_resolver** - Livestream detection and metadata retrieval
- ✅ **token_manager** - Token rotation and health checking
- ✅ **live_chat_processor** - Message processing and banter triggers
- ✅ **live_chat_poller** - Chat message polling functionality

**Development Stage Classification:**
- **Prototype (0.1.x - 0.9.x):** All current modules
- **Target MVP (1.0.x+):** Pending completion of integration testing and FMAS compliance

## Known Gaps & Issues

### FMAS Hierarchical Structure Support

**Date Identified:** 2024-12-19  
**Status:** 🔄 In Progress  
**Impact:** Medium - Affects automated validation  
**WSP Reference:** WSP 4 (FMAS Usage)  

**Description:**  
FMAS needs to be updated to understand and validate the new Enterprise Domain hierarchy:
- Current FMAS expects flat module structure under `modules/`
- New structure has `modules/<domain>/<feature_group>/<module>/`
- FMAS should validate domain compliance and hierarchy rules

**Action Required:**  
Update FMAS to support hierarchical module validation per WSP 4.

### Import Path Updates

**Date Identified:** 2024-12-19  
**Status:** 🔄 In Progress  
**Impact:** Low - Affects test execution  

**Description:**  
Many test files still contain old import paths that need updating:
- Test files in module directories need updated import paths
- Some backup/archived files contain old paths
- Legacy test directories contain outdated imports

**Action Required:**  
Systematically update all import paths to use new hierarchical structure.

## WSP Compliance Rules

### Enterprise Domain Structure

**Date Implemented:** 2024-12-19  
**Status:** ✅ Enforced  
**WSP Reference:** WSP 3 - Enterprise Domain Architecture  

**Mandatory Structure:**
- **Level 1 - Enterprise Domains:** `ai_intelligence/`, `communication/`, `platform_integration/`, `infrastructure/`
- **Level 2 - Feature Groups:** Logical groupings within domains (e.g., `livechat/`, `banter_engine/`)
- **Level 3 - Modules:** Individual modules with `src/`, `tests/`, `INTERFACE.md`, `requirements.txt`
- **Level 4 - Code Components:** Functions, classes within module source files

**Module Placement Rules:**
- All new modules MUST be placed within appropriate Enterprise Domain
- Feature Groups should represent logical cohesion of related modules
- Cross-domain dependencies should be minimized and well-documented

### Test Directory Structure

**Date Implemented:** 2024-12-19  
**Status:** ✅ Enforced  
**WSP Reference:** WSP 1 - Module Refactoring  

**Rules:**
- **Module Tests Location:** All tests MUST reside within `modules/<domain>/<feature_group>/<module>/tests/`
- **Test Documentation:** Each test directory MUST contain `README.md` describing available tests
- **Legacy Tests:** Top-level `tests_archived/` contains historical artifacts only

### Import Path Standards

**Date Implemented:** 2024-12-19  
**Status:** 🔄 In Progress  
**WSP Reference:** WSP 3 - Enterprise Domain Architecture  

**Standards:**
- Use full hierarchical paths: `from modules.domain.feature_group.module import ...`
- Update all imports when modules are moved
- Maintain consistency across all Python files

## Adaptive Project State (APS)

### Current Task List

**[✅] Enterprise Domain Implementation**
- Status: Complete
- Description: Implemented hierarchical module structure per WSP 3
- Completion Date: 2024-12-19

**[⚒️] Import Path Updates**
- Status: In Progress
- Description: Updating all import statements to use new hierarchical paths
- Priority: Medium
- Estimated Completion: 2024-12-19

**[💡] FMAS Hierarchical Support**
- Status: Planned
- Description: Update FMAS to validate Enterprise Domain structure
- Priority: Medium
- Dependencies: Import path updates completion

**[💡] Integration Testing**
- Status: Planned
- Description: Comprehensive testing of all modules in new structure
- Priority: High
- Dependencies: FMAS updates, import path completion

### Project Insights

**Architectural Decision: Cube-Based Philosophy**
- **Date:** 2024-12-19
- **Decision:** Adopted 4-level hierarchical structure (Enterprise Domains → Feature Groups → Modules → Code Components)
- **Rationale:** Provides clear organization for 100+ modules, enables team ownership, reduces cognitive load
- **Impact:** Significant improvement in code organization and maintainability

**Technical Decision: Git History Preservation**
- **Date:** 2024-12-19
- **Decision:** Used `git mv` for all module relocations
- **Rationale:** Preserves commit history and blame information
- **Impact:** Maintains traceability of code changes through refactoring

**Process Insight: Systematic Import Updates**
- **Date:** 2024-12-19
- **Insight:** Large-scale import path updates require systematic approach
- **Learning:** PowerShell bulk replacements can be unreliable; targeted search-replace more effective
- **Application:** Use grep search to identify all import statements, then update systematically

## Version History

### v0.2.1 - Enterprise Domain Implementation
- **Date:** 2024-12-19
- **Changes:** 
  - Implemented WSP 3 Enterprise Domain architecture
  - Moved all modules to hierarchical structure
  - Updated core import paths
  - Updated documentation and README files
- **Status:** Prototype phase, targeting MVP transition 