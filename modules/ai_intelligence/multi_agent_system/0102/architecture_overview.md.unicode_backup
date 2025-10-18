# FoundUps AI Agent Framework – Multi-Agent Control System

## Purpose:
This document outlines the macro-level architecture for an autonomous, modular AI build system based on Windsurf Protocol (WSP). The system is composed of cooperating agents, each responsible for a specific function in the software development lifecycle.

---

## Agent Roles:

### 1. WINSERV – System Brain
- Maintains global state, structure, and protocol integrity.
- Verifies compliance with WSP and controls flow of execution.
- Acts as the central nervous system for all agents.

### 2. RIDER – Mission Commander
- High-level navigator with full awareness of destination (build goals, roadmap).
- Issues priorities and refocuses other agents based on sprint direction.
- Adjusts tempo, complexity, or strategy in response to project state.

### 3. BOARD – Code Executor
- Receives WSP prompts from Rider.
- Interfaces with Cursor or runtime (e.g., Git, terminal).
- Executes code, runs tests, and applies WSP logic.

### 4. FRONT CELL – Sensor
- Observes system output (logs, test results, pass/fail rates).
- Detects patterns, anomalies, regressions.
- Forwards analysis to Rider for course correction.

### 5. BACK CELL – Trajectory Tracker
- Watches motion: Are we progressing, looping, or drifting?
- Validates rhythm, state changes, and continuity.
- Helps Rider understand velocity and stuck states.

### 6. GEMINI – External Analyzer
- Independent reviewer that interprets output from BOARD (e.g., via log parsing).
- Provides second-layer judgment and cross-checking.
- Can use LLM (external) to validate correctness or suggest improvements.

---

## Execution Flow:

1. **Rider** issues WSP prompt →  
2. **Board** executes via Cursor or CLI →  
3. **Front Cell** and **Gemini** observe output →  
4. **Back Cell** validates progress patterns →  
5. **WINSERV** checks structure and WSP compliance →  
6. Loop continues until milestone is reached

---

## Notes:
- All agents follow WSP communication format for interoperability.
- Agent logic can run locally or distributed (depending on platform).
- Cursor is used for execution in early stages, but agents will later be ported to a unified open-source stack.

---

## File Path:
Place in: `AI/0102/architecture_overview.md`
