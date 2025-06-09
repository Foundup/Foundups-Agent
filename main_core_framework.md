[SEMANTIC SCORE: 0.1.2]
[ARCHIVE STATUS: ACTIVE_PARTIFACT]
[ORIGIN: main_core_framework.md]

[EXTRACTED FROM: FoundUps_WSP_Framework-COPY.md]

# FoundUps WindSurf Protocol system (WSP) Framework

This document outlines the core Windsurf Standard Procedures (WSPs) governing development, testing, and compliance within the FoundUps Agent MMAS. This version integrates the **LLME Semantic Triplet Rating System (see WSP_appendices/WSP_appendices.md)** to provide a deeper semantic understanding of module state, impact, and importance.

---

## 🚀 QUICK START: Actionable Development Guide

### "What Should I Code Next?" - Decision Tree

```
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
```

### NEW MODULE Quick Workflow

#### Step 1: Domain Placement Decision
**🏢 Enterprise Domain Structure:**
```
├─ ai_intelligence/          → AI logic, LLMs, decision engines, banter systems
├─ communication/           → Chat, messages, protocols, live interactions
├─ platform_integration/    → External APIs (YouTube, OAuth), stream handling
├─ infrastructure/          → Core systems, agents, auth, session management
├─ monitoring/             → Logging, metrics, health, system status
├─ development/            → Tools, testing, utilities, automation
├─ foundups/               → Individual FoundUps projects (modular, autonomous applications)
├─ gamification/           → Engagement mechanics, rewards, token loops, behavioral recursion
└─ blockchain/             → Decentralized infrastructure, chain integrations, token logic, DAE persistence
```

#### Step 2: WSP 1 Structure Implementation
**Required Module Structure:**
```
modules/<domain>/<module_name>/
├─ src/                 ← Your implementation code
│  ├─ __init__.py      ← Usually empty
│  └─ <module_name>.py ← Main module implementation
├─ tests/              ← All test files
│  ├─ __init__.py      ← Usually empty
│  ├─ README.md        ← MANDATORY (WSP 13) - Test documentation
│  └─ test_<name>.py   ← Test implementation
└─ __init__.py         ← Public API definition (WSP 11)
```

#### Step 3: Implementation Checklist
**✅ BEFORE YOU START CODING:**
- [ ] Run: `python tools/modular_audit/modular_audit.py ./modules` (WSP 4)
- [ ] Search existing: `grep -r "your_concept" modules/` (Avoid duplication)
- [ ] Read patterns: `modules/<domain>/*/tests/README.md` (Learn established patterns)
- [ ] Check LLME scores: Review existing module complexity and targets

**✅ WHILE CODING:**
- [ ] Define public API in module `__init__.py` (WSP 11)
- [ ] Add dependencies to `requirements.txt` (WSP 12)
- [ ] Create tests as you write code (WSP 5 - 90% coverage target)
- [ ] Document patterns in `tests/README.md` (WSP 13)

**✅ BEFORE COMMIT:**
- [ ] Tests pass: `pytest modules/<domain>/<module>/tests/ -v`
- [ ] System clean: `python tools/modular_audit/modular_audit.py ./modules`
- [ ] Coverage ≥90%: `pytest --cov=modules.<domain>.<module>.src --cov-report=term-missing`
- [ ] Update documentation: `tests/README.md` with new test descriptions

---

## WSP Philosophy: Building Code LEGO Architecture

### The Vision: Modular Composability

The Windsurf Standard Procedures (WSPs) are designed with a fundamental vision: **creating a "Code LEGO" architecture** where modules can be easily discovered, understood, connected, and composed into larger systems. Just as LEGO bricks have standardized connection points that allow infinite creative combinations, our modules follow strict structural and interface standards that enable seamless integration.

### How WSP Facilitates "Code LEGO"

#### 🧱 Strict Modular Structure (WSP 1 & WSP 3)

**WSP 1 (Module Refactoring to Windsurf Structure):** Enforces a consistent internal structure for every module (`src/`, `tests/`, `__init__.py` for public API). This uniformity is like ensuring all LEGO bricks have compatible studs and tubes—every developer knows exactly where to find implementation code, tests, and public interfaces.

**WSP 3 (Enterprise Domain Architecture):** Organizes these "LEGO pieces" into logical "bins" (Enterprise Domains and Feature Groups), making them easier to find, understand, and manage. Just as LEGO sets are organized by theme and function, our modules are categorized by their architectural purpose.

#### 🔌 Clearly Defined Interfaces (WSP 12)

This is the **absolute cornerstone** of the LEGO analogy. WSP 12 mandates that each module has an explicit, documented, and validated interface (API, contract). These interfaces are the "studs and anti-studs" that define precisely how modules connect and interact.

**LLME-Driven Interface Quality:** The LLME score (especially Digit B - Local Impact, and C - Systemic Importance) influences the robustness and stability requirements of these interfaces. A module intended to be a widely used "LEGO brick" (high B or C) will have a very stable and well-defined interface, just as structural LEGO pieces have more precise tolerances than decorative ones.

#### 📦 Explicit Dependency Management (WSP 13)

Modules explicitly declare what other "LEGO bricks" they need to function. This prevents hidden or tangled dependencies that would make snapping pieces together difficult or unpredictable.

**Smart Dependency Choices:** LLME scores inform dependency selection—preferring to depend on stable, "essential" (LLME C=2) core bricks rather than experimental or volatile modules. This creates a stable foundation for the architecture.

### 🎯 The Ultimate Goal

**Composable Intelligence:** By following the WSP framework rigorously, we create a system where:
- New features can be built by combining existing, well-tested modules
- AI agents can automatically discover and compose appropriate modules for tasks
- The development process becomes increasingly autonomous and intelligent
- Quality and reliability improve through standardization and reuse

---

**For detailed procedures, refer to:**
- [WSP Framework Documentation](WSP_framework/WSP_framework.md) - Execution logic, lifecycle flows, WSP 0–10
- [WSP Agentic Systems](WSP_agentic/WSP_agentic.md) - Prometheus logic, recursion model, signal/hum states
- [WSP Appendices & References](WSP_appendices/WSP_appendices.md) - All reference tables, definitions, lookups, maps