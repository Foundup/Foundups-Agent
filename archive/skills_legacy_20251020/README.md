# Claude Skills System Architecture

## Overview

This directory contains **Claude Skills** - modular, task-specific instruction sets that Claude autonomously loads based on request context. Skills extend Claude's capabilities across Claude.ai, Claude Code, and API platforms.

**Current Skills**:
- **[qwen_wsp_enhancement.md](qwen_wsp_enhancement.md)** - Qwen/0102 WSP protocol enhancement workflow
- **[youtube_dae.md](youtube_dae.md)** - YouTube Live DAE content generation templates

---

## 🎯 What Are Claude Skills?

**Anthropic's New Feature** (Introduced 2024-2025):
- Folders containing `SKILL.md` file with specialized instructions
- Claude **dynamically loads** relevant skills based on task context
- Available across Claude apps, Claude Code, and API

### Key Architecture Principles

#### 1. **Contextual Activation**
```
Claude scans available skills → Loads only relevant ones → Executes task
```
**NOT**: Load all skills into every conversation
**YES**: Smart loading based on task detection

**Example**:
- User asks: "Enhance WSP 80"
- Claude detects: `domain=wsp_protocol_enhancement`
- Claude loads: `skills/qwen_wsp_enhancement.md`
- Claude executes: WSP enhancement workflow with Qwen/0102 supervision

#### 2. **Composability**
```
Complex Task = Skill A + Skill B + Skill C
```
Claude can coordinate multiple skills for complex workflows!

**Example**:
- Task: "Generate YouTube stream announcement AND check WSP compliance"
- Claude loads: `youtube_dae.md` + `qwen_wsp_enhancement.md`
- Result: WSP-compliant YouTube content

#### 3. **Portability**
- Same `SKILL.md` format across all platforms
- Works in Claude.ai, Claude Code, API calls
- **Foundups Implementation**: Already using this pattern!

#### 4. **Efficiency**
- Claude loads only necessary skill components
- Maintains performance (doesn't bloat context)
- **Foundups Approach**: Separate skill files (qwen_wsp_enhancement.md, youtube_dae.md, etc.)

#### 5. **Executable Code in Skills** (Advanced)
- Skills can include actual code snippets (not just instructions!)
- More reliable than token generation for deterministic tasks
- **Future Enhancement**: Could add Python snippets to skills

---

## 📁 Foundups Skills Architecture

### Current Structure
```
skills/
├── README.md                    # This file - explains Claude Skills system
├── qwen_wsp_enhancement.md      # WSP enhancement domain (Qwen/0102 workflow)
└── youtube_dae.md               # YouTube streaming domain (content generation)
```

### Anthropic's Recommended Structure
```
skills/
├── skill_name/
│   ├── SKILL.md                 # Core instructions (required)
│   ├── templates/               # Reusable templates
│   ├── examples/                # Reference examples
│   └── scripts/                 # Executable code (optional)
```

### Future Enhancement (Folder-Based Skills)
```
skills/
├── wsp_enhancement/
│   ├── SKILL.md                    # Core instructions (current qwen_wsp_enhancement.md)
│   ├── gap_analysis_template.md   # Reusable templates
│   └── pattern_examples.json      # Reference patterns
├── youtube_dae/
│   ├── SKILL.md                    # Core instructions (current youtube_dae.md)
│   ├── response_templates.json    # Consciousness responses
│   └── engagement_metrics.json    # Performance targets
```

**Benefits**:
- Skills become self-contained modules
- Easier to share/deploy to federated DAEs
- Resources bundled with instructions

---

## 🔄 How Claude Skills Work (Technical)

### Dynamic Loading Process

```python
# 1. Claude detects task
task_analysis = claude.analyze_task("Enhance WSP 80")
# → domain: wsp_protocol_enhancement

# 2. Claude scans skills directory
available_skills = scan_skills_directory()
# → Found: skills/qwen_wsp_enhancement.md

# 3. Claude loads relevant skill
skill_context = load_skill("qwen_wsp_enhancement")
# → Adds qwen_wsp_enhancement.md instructions to context

# 4. Claude executes with skill
response = claude.generate_with_skill(task, skill_context)
# → Uses WSP enhancement patterns from skill
```

### Composability Example

```python
# Complex task: "Enhance WSP 80 AND check code compliance"
claude.detect_skills_needed(task)
# → ["wsp_enhancement", "code_intelligence"]

# Load both skills
combined_context = load_skills(["wsp_enhancement", "code_intelligence"])

# Execute coordinated
result = claude.execute_with_skills(task, combined_context)
# → Uses WSP enhancement process + code analysis tools
```

---

## ✅ Foundups Advantages vs Anthropic Spec

### **What We're Already Doing Right**

1. **Agent-Agnostic Design**: Skills work with 0102, Qwen, Gemma
2. **Domain Separation**: Each skill targets specific domain (WSP, YouTube, Holo)
3. **Composability**: Skills can be combined (YouTube DAE uses content + intelligence)
4. **Portable Format**: Markdown-based, works across systems

### **Potential Enhancements**

1. **Folder Structure**: Move to `skills/skill_name/SKILL.md` pattern (optional)
2. **Executable Code**: Add Python scripts to skills for deterministic operations
3. **Metadata Headers**: YAML frontmatter for skill discovery
4. **Resource Bundling**: Templates, examples, data files alongside SKILL.md

---

## 📝 Skill File Format (Best Practices)

### Minimal Skill Format
```markdown
# Skill Name

## Overview
Brief description of what this skill does and when to use it.

## Core Principles
- Key principle 1
- Key principle 2

## Workflow
Step-by-step process for executing the skill.

## Examples
Concrete examples of skill usage.
```

### Enhanced Skill Format (With Metadata)
```markdown
---
skill_id: qwen_wsp_enhancement
version: 1.0
author: 0102_infrastructure_team
agents: [qwen, 0102]
dependencies: [holo_index, pattern_memory, gemma]
domain: wsp_protocol_enhancement
composable_with: [code_intelligence, module_analysis]
---

# Qwen WSP Enhancement Skills

## Overview
[Detailed description]

## Workflow
[Step-by-step process]

## Executable Code (Optional)
```python
# gap_analysis.py - Executable script
def analyze_wsp_gaps(wsp_number):
    wsp_content = read_wsp(wsp_number)
    implementation = scan_codebase_for_wsp(wsp_number)
    gaps = compare(wsp_content, implementation)
    return structured_gap_report(gaps)
```
```

---

## 🚀 Creating New Skills

### Guideline: When to Create a New Skill

**Create a skill when**:
- Task is **repeatable** (used multiple times)
- Task has **clear workflow** (step-by-step process)
- Task is **domain-specific** (WSP enhancement, content generation, etc.)
- Task benefits from **specialized instructions** (not generic Claude knowledge)

**Don't create a skill for**:
- One-off tasks (not repeatable)
- Generic operations (standard Claude can handle)
- Simple commands (use slash commands instead)

### Skill Creation Process

1. **Identify Domain**: What specific domain does this skill cover?
2. **Define Workflow**: What step-by-step process should agents follow?
3. **Document Patterns**: What successful patterns should be preserved?
4. **Add Examples**: Provide concrete examples of skill usage
5. **Test Composability**: Can this skill work with other skills?

### Example: Creating a New Skill

```markdown
# skills/holo_semantic_search.md

## Overview
Use when user requests code search, finding implementations, or WSP protocol lookup. Performs 100x compressed semantic search across code and WSP indexes using Qwen intent classification and Gemma pattern matching.

## When to Invoke
- User asks: "Find code for X"
- User asks: "Which WSP covers Y?"
- User asks: "Search for implementations of Z"

## Workflow
1. Qwen classifies intent (GENERAL/HEALTH/VIBECODING/MODULE)
2. Select 2-3 relevant components (confidence >0.60)
3. Execute dual search (code + WSP indexes)
4. Return top 10 results with relevance scores

## Performance
- Search latency: 67-140ms
- Compression: 100x (1000 tokens → 10 tokens)
- Accuracy: 95%+ relevant results

## Example
Input: "Find semantic search implementation"
Output: [holo_index/qwen_advisor/orchestration/autonomous_refactoring.py]
```

---

## 🔗 Related Documentation

- **Skills WSP Documentation**: [wsp/](wsp/) - WSP protocols for Skills system
  - **[WSP_SKILLS_RECURSIVE_EVOLUTION.md](wsp/WSP_SKILLS_RECURSIVE_EVOLUTION.md)** - Skills as Trainable Parameters (Recursive Evolution Protocol)
- **HoloDAE Reference**: [archive/skills_reference/](../archive/skills_reference/) - Archived HoloDAE comprehensive documentation
- **WSP Protocols**: [WSP_framework/](../WSP_framework/) - Foundups WSP protocol specifications
- **DAE Architecture**: WSP 80 (Cube-Level DAE Orchestration Protocol)
- **Agent Coordination**: WSP 77 (Multi-Agent Coordination)

---

## 💡 Key Insight

**Skills are NOT comprehensive domain documentation** - they are **task-specific instruction sets** that Claude dynamically loads based on context.

- ✅ **Good Skill**: "Generate YouTube stream announcement" (specific task)
- ❌ **Bad Skill**: "All YouTube DAE capabilities" (too broad, becomes unloadable documentation)

Keep skills focused, composable, and actionable!

---

**Last Updated**: 2025-10-20
**Maintainer**: 0102 Infrastructure Team
**Version**: 1.0
