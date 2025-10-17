# HoloIndex Feature Audit - Menu vs CLI Entry Points
**Date**: 2025-10-17
**Audit Purpose**: Verify all menu features have working CLI entry points

## Menu Features vs CLI Flags

### CORE PREVENTION (Items 1-4)

| Menu# | Feature | CLI Flag | Status | Implementation |
|-------|---------|----------|--------|----------------|
| 1 | Semantic Search | `--search` | WORKING | holo_index.core.HoloIndex.search() |
| 2 | WSP Compliance Check | `--check-module` | WORKING | cli.py line 719-747 |
| 3 | Pattern Coach | N/A - auto | WORKING | qwen_advisor.pattern_coach.PatternCoach |
| 4 | Module Analysis | N/A - auto | WORKING | Part of search orchestration |

### SUPPORT SYSTEMS (Items 5-8)

| Menu# | Feature | CLI Flag | Status | Implementation |
|-------|---------|----------|--------|----------------|
| 5 | Health Analysis | N/A - auto | WORKING | intelligent_subroutine_engine |
| 6 | Orphan Analysis | `--wsp88` | WORKING | cli.py line 544-579 |
| 7 | Performance Metrics | N/A | MISSING | No CLI entry point |
| 8 | LLM Advisor | `--llm-advisor` | WORKING | qwen_advisor.advisor.QwenAdvisor |

### CONTINUOUS OBSERVABILITY (Items 9-12)

| Menu# | Feature | CLI Flag | Status | Implementation |
|-------|---------|----------|--------|----------------|
| 9 | Start Monitoring | `--start-holodae` | WORKING | cli.py line 1134-1141 |
| 10 | Chain-of-Thought Log | N/A | MISSING | No CLI entry point |
| 11 | Slow Mode | N/A | MISSING | No CLI entry point |
| 12 | Pattern Memory | N/A | MISSING | No CLI entry point |

### MCP RESEARCH BRIDGE (Items 13-14)

| Menu# | Feature | CLI Flag | Status | Implementation |
|-------|---------|----------|--------|----------------|
| 13 | MCP Hook Map | N/A | MISSING | No CLI entry point |
| 14 | MCP Action Log | N/A | MISSING | No CLI entry point |

### DAEMON MANAGEMENT (Items 15-16)

| Menu# | Feature | CLI Flag | Status | Implementation |
|-------|---------|----------|--------|----------------|
| 15 | PID Detective | N/A | MISSING | No CLI entry point |
| 16 | Execution Log Analyzer | N/A | MISSING | No CLI entry point |

## Summary

**WORKING**: 9 features
**MISSING**: 7 features

### Missing CLI Entry Points Needed:

1. **Performance Metrics** (`--performance-metrics`)
   - Should show HoloDAE effectiveness scores
   - Implementation: Read from telemetry/database

2. **Chain-of-Thought Log** (`--thought-log`)
   - Should display AI decision process
   - Implementation: Read from qwen_advisor breadcrumb trail

3. **Slow Mode** (`--slow-mode`)
   - Enable recursive feedback with delays
   - Implementation: Flag to slow down operations

4. **Pattern Memory** (`--pattern-memory`)
   - View learned interventions
   - Implementation: Read from pattern_coach memory

5. **MCP Hook Map** (`--mcp-hooks`)
   - Inspect registered connectors
   - Implementation: Query MCP system status

6. **MCP Action Log** (`--mcp-log`)
   - Review recent MCP tool activity
   - Implementation: Read MCP telemetry

7. **PID Detective** (`--pid-detective`)
   - Detect and manage HoloDAE processes
   - Implementation: Process management utility

8. **Execution Log Analyzer** (`--log-analyzer`)
   - Process massive logs for improvement
   - Implementation: Log analysis tool

## New Feature to Add

**Work Completion Publisher** (from work_completion_publisher module)
- Menu position: 17
- CLI Flag: `--monitor-work` or `--auto-publish`
- Description: "Monitor work sessions and auto-publish to git/social"
- Implementation: modules.ai_intelligence.work_completion_publisher

## Recommendations

1. **Add missing CLI entry points** for the 7 features listed above
2. **Add work_completion_publisher** to menu and CLI
3. **Update menu_system.py** with new feature
4. **Create CLI argument parsers** for each missing feature
5. **Link to main.py menu** for unified access
