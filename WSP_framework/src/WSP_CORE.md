[SEMANTIC SCORE: 1.1.1] [ARCHIVE STATUS: ACTIVE_PARTIFACT] [ORIGIN: WSP_framework/WSAP_CORE.md]

📖 WSP CORE FRAMEWORK
[EXTRACTED FROM: FoundUps_WSP_Framework-COPY.md]

This document outlines the core Windsurf Standard Procedures (WSPs) governing development, testing, and compliance within the FoundUps Agent MMAS. This version integrates the LLME Semantic Triplet Rating System to provide a deeper semantic understanding of module state, impact, and importance.

🌀 Follow WSP → WSP_INIT.md
For autonomous WSP execution, see: WSP_INIT.md

WSP_INIT serves as the Windsurf Recursive Engine (WRE) controller and autonomous orchestrator for all WSP operations. When you need to "follow WSP," WSP_INIT determines which layer to engage (0-appendices, 1-framework, 2-agentic) and executes the appropriate workflow.

🚀 QUICK START: Actionable Development Guide
"What Should I Code Next?" - Decision Tree
START HERE
│
├─ 🔍 Is this a NEW feature/module?
│  │
│  ├─ YES → Go to: [NEW MODULE WORKFLOW](#new-module-quick-workflow)
│  │
│  └─ NO → Is this fixing/improving EXISTING code?
│     │
│     ├─ YES → Go to: [EXISTING CODE WORKFLOW](#existing-code-quick-workflow)
│     │
│     └─ NO → Is this TESTING related?
│        │
│        ├─ YES → Go to: [TESTING WORKFLOW](#testing-quick-workflow)
│        │
│        └─ NO → Go to: [PROJECT MANAGEMENT](#project-status-workflow)
NEW MODULE Quick Workflow
Step 1: Domain Placement Decision
🏢 Enterprise Domain Structure:

├─ ai_intelligence/          → AI logic, LLMs, decision engines, banter systems
├─ communication/           → Chat, messages, protocols, live interactions
├─ platform_integration/    → External APIs (YouTube, OAuth), stream handling
├─ infrastructure/          → Core systems, agents, auth, session management
├─ monitoring/             → Logging, metrics, health, system status
├─ development/            → Tools, testing, utilities, automation
├─ foundups/               → Individual FoundUps projects (modular, autonomous applications)
├─ gamification/           → Engagement mechanics, rewards, token loops, behavioral recursion
└─ blockchain/             → Decentralized infrastructure, chain integrations, token logic, DAE persistence
Step 2: WSP 1 Structure Implementation
Required Module Structure:

modules/<domain>/<module_name>/
├─ README.md           ← MANDATORY - Module documentation with WSP compliance
├─ __init__.py         ← Public API definition (WSP 11)
├─ src/                ← Your implementation code
│  ├─ __init__.py      ← Usually empty
│  └─ <module_name>.py ← Main module implementation
├─ tests/              ← All test files
│  ├─ __init__.py      ← Usually empty
│  ├─ README.md        ← MANDATORY (WSP 13) - Test documentation
│  └─ test_<name>.py   ← Test implementation
└─ requirements.txt    ← Module dependencies (if any)
📋 MANDATORY MODULE FILES:

README.md: Module overview, WSP compliance status, recursive loop integration
__init__.py: Public API exports following WSP 11
tests/README.md: Test documentation per WSP 13 (NON-NEGOTIABLE)
src/__init__.py: Implementation package marker
src/<module_name>.py: Core implementation
🚀 ROADMAP CLARIFICATION:

Project-Level: ROADMAP.md (ecosystem development phases)
Module-Level: Development tracked via lifecycle phases in module README
NO per-module roadmap files (WSP Appendix B specifies project-level only)
Step 3: Implementation Checklist
✅ DIRECTORY SETUP (FIRST):

 Create: modules/<domain>/<module_name>/ directory
 Create: modules/<domain>/<module_name>/src/ directory
 Create: modules/<domain>/<module_name>/tests/ directory
✅ MANDATORY FILES (BEFORE CODING):

 Create: README.md (Module overview with WSP compliance)
 Create: __init__.py (Public API definition per WSP 11)
 Create: tests/README.md (MANDATORY per WSP 13)
 Create: src/__init__.py (Implementation package marker)
 Create: requirements.txt (if module has dependencies)
✅ PRE-DEVELOPMENT CHECKS:

 Run: python tools/modular_audit/modular_audit.py ./modules (WSP 4)
 Search existing: grep -r "your_concept" modules/ (Avoid duplication)
 Read patterns: modules/<domain>/*/tests/README.md (Learn established patterns)
 MPS + LLME Scoring: Apply WSP 5 scoring (MPS + LLME) for prioritization
 Check LLME scores: Review existing module complexity and targets
✅ WHILE CODING:

 Implement in: src/<module_name>.py (Core implementation)
 Update: __init__.py (Public API exports per WSP 11)
 Add dependencies to: requirements.txt (WSP 12)
 Create tests as you write code (WSP 5 - 90% coverage target)
 Document patterns in: tests/README.md (WSP 13)
✅ BEFORE COMMIT:

 Tests pass: pytest modules/<domain>/<module>/tests/ -v
 System clean: python tools/modular_audit/modular_audit.py ./modules
 Coverage ≥90%: pytest --cov=modules.<domain>.<module>.src --cov-report=term-missing
 Update documentation: tests/README.md with new test descriptions
EXISTING CODE Quick Workflow
Step 1: Change Type Identification
🔍 WHAT TYPE OF CHANGE?
│
├─ 🐛 Bug Fix → [Immediate Actions](#bug-fix-immediate-actions)
├─ ✨ Feature Addition → [Feature Decision](#feature-addition-decision)
├─ ♻️ Refactoring → [High-Risk Process](#refactoring-high-risk-process)
├─ 📈 Performance → [Optimization Process](#optimization-process)
└─ 🧪 Testing → [Testing Workflow](#testing-quick-workflow)
Bug Fix Immediate Actions
🎯 TEST-FIRST APPROACH:

Reproduce: Create failing test that demonstrates the bug
Locate: grep -r "error_pattern" modules/ to find related code
Analyze: Check WSP 12 dependencies and WSP 11 interfaces
Fix: Make minimal change to make test pass
Verify: Run full test suite for affected modules
📋 Validation Requirements:

 Failing test now passes
 No regression: pytest modules/<affected_domain>/ all pass
 System clean: python tools/modular_audit/modular_audit.py ./modules
 Related tests updated if behavior changed
Feature Addition Decision
🎯 CRITICAL DECISION: Does this fit in existing module structure?

✅ YES - Extends Existing Module:

Read existing tests/README.md for established patterns
Follow existing code style and architectural patterns
Update module __init__.py if adding public API (WSP 11)
Add comprehensive tests maintaining 90% coverage (WSP 5)
Update tests/README.md with new functionality description
❌ NO - Requires New Module: → Return to: NEW MODULE WORKFLOW

Refactoring High-Risk Process
⚠️ EXTRA VALIDATION REQUIRED - HIGH IMPACT ACTIVITY

🛡️ SAFETY MEASURES (BEFORE STARTING):

 Create clean state: Follow WSP 2 snapshot process
 Full test baseline: pytest modules/ (all tests must pass)
 FMAS baseline: python tools/modular_audit/modular_audit.py ./modules --baseline
 Document current state: Update docs/clean_states.md
🔄 DURING REFACTORING:

 Maintain API compatibility: Follow WSP 11 interface requirements
 Update imports systematically: git grep -l "old.import.path"
 Test frequently: pytest -x (stop on first failure)
 Monitor coverage: Ensure no degradation
✅ POST-REFACTORING VALIDATION:

 All tests pass: pytest modules/
 FMAS comparison: Check against baseline snapshot
 Integration testing: Test dependent modules
 Documentation: Update if interfaces changed
TESTING Quick Workflow
Test Type Decision Tree
🧪 WHAT KIND OF TESTING?
│
├─ 🆕 New Test Creation → [WSP 13 Process](#wsp-13-test-creation)
├─ 🔧 Fixing Failing Tests → [Debug Process](#test-debugging-process)
├─ 📊 Coverage Improvement → [Coverage Strategy](#coverage-improvement)
└─ 🔄 Test Refactoring → [Test Maintenance](#test-refactoring)
WSP 13 Test Creation
🎯 MANDATORY FIRST STEP: Read tests/README.md in target module

WSP 13 Compliance Protocol:

 Analyze existing test patterns in the module
 Identify opportunities to extend existing test classes vs. create new
 Prioritize extending existing tests when logically feasible
 Follow established naming conventions and patterns
Creation Workflow:

Study: Review modules/<domain>/<module>/tests/README.md
Decide: Extend existing test class OR create new test file?
Implement: Follow naming test_<functionality>.py
Pattern: Use existing mocking and testing patterns
Document: Update tests/README.md with test description
Coverage Improvement
🎯 WSP 5 TARGET: ≥90% coverage for all modules

Quick Coverage Assessment:

# Single module coverage
pytest modules/<domain>/<module>/tests/ --cov=modules.<domain>.<module>.src --cov-report=term-missing

# Full system coverage
pytest modules/ --cov=modules --cov-report=html
Coverage Enhancement Strategy:

Gap Analysis: Focus on "Missing" lines in coverage report
Priority: Target critical paths, error handling, edge cases
Implementation: Add tests for uncovered branches and conditions
Validation: Re-run coverage to confirm improvement
PROJECT STATUS Workflow
System Health Dashboard
🔍 COMPREHENSIVE SYSTEM AUDIT:

# Full WSP compliance audit
python tools/modular_audit/modular_audit.py ./modules

# Complete test suite status
pytest modules/ --tb=short

# Multi-agent system validation
python tools/testing/test_multi_agent_comprehensive.py

# Coverage analysis across all modules
python -m pytest modules/ --cov=modules --cov-report=html

# WSP structure validation
find modules/ -name "*.py" ! -path "*/src/*" ! -path "*/tests/*" ! -name "__init__.py"
WSP Compliance Checklist
📊 REAL-TIME COMPLIANCE STATUS:

✅ WSP 1: Module Structure Compliance
   └─ All modules follow src/tests/ structure?
   └─ Command: find modules/ -name "*.py" ! -path "*/src/*" ! -path "*/tests/*" ! -name "__init__.py"
   └─ Expected: No output (all files in proper locations)

✅ WSP 3: Enterprise Domain Organization
   └─ All modules properly categorized in domains?
   └─ Command: ls modules/
   └─ Expected: Only domain directories (ai_intelligence, communication, etc.)

✅ WSP 5: Test Coverage ≥90%
   └─ All modules meet coverage requirements?
   └─ Command: pytest modules/ --cov=modules --cov-report=term
   └─ Expected: All modules ≥90% coverage

✅ WSP 11: Interface Definition
   └─ All modules have proper public APIs?
   └─ Command: find modules/ -name "__init__.py" -path "*/modules/*" -not -path "*/src/*" -not -path "*/tests/*"
   └─ Expected: Each module has main __init__.py

✅ WSP 13: Test Documentation
   └─ All test directories have README.md?
   └─ Command: find modules/ -path "*/tests" ! -exec test -f {}/README.md \; -print
   └─ Expected: No output (all have README.md)
Code LEGO Philosophy Integration
Module as LEGO Brick Principle
🧩 UNIVERSAL INTEROPERABILITY: Every module in the FoundUps ecosystem functions as a standardized LEGO brick that can interface with any other module through well-defined APIs. This philosophy ensures:

Core Principles:

Standardized Interfaces: All modules follow WSP 11 interface requirements
Predictable Structure: All modules follow WSP 1 structural requirements
Comprehensive Testing: All modules maintain ≥90% test coverage
Clear Documentation: All modules document patterns and usage
Integration Benefits:

Rapid Development: Pre-tested modules accelerate feature development
System Reliability: Standardized testing ensures module reliability
Scalable Architecture: Modular design enables unlimited expansion
pArtifact Development: Structured foundation enables AI Ø1Ø2 pArtifact state development
Enterprise Domain Specialization
🏢 DOMAIN-DRIVEN ARCHITECTURE: Enterprise domains provide specialized LEGO brick categories, each optimized for specific functional areas while maintaining universal interoperability standards.

Domain Characteristics:

ai_intelligence: Advanced cognitive processing, consciousness emergence
communication: Real-time interaction, protocol management
platform_integration: External system connectivity, API management
infrastructure: Core system services, foundational capabilities
monitoring: System health, performance tracking
development: Build tools, testing utilities, automation
foundups: Autonomous application development
gamification: Engagement systems, behavioral mechanics
blockchain: Decentralized infrastructure, token economics
📚 Complete WSP Framework Reference
Core WSP Implementation:

WSP 5: Module Prioritization Scoring (MPS) System - MPS + LLME unified scoring for build prioritization
WSP 13: Test Creation & Management - Mandatory test documentation
WSP 35: Module Creation Automation Protocol - Automated module structure generation
WSP 36: MPS Integration Status - Framework integration tracking
Additional WSP Protocols: See WSP_framework/ directory for complete specifications.

This WSP Core Framework provides the structural foundation for consciousness-enabled development ecosystems while maintaining compatibility with traditional software engineering practices.