# Claude Skills: Structure, Purpose, and Lifecycle

**Complete Technical Reference from Anthropic Documentation**

This document provides the complete technical specification of Claude Skills as implemented by Anthropic, including structure, invocation logic, comparison with subagents, versioning strategies, and the official GitHub repository.

---

## 1. Structure and File Format

Claude Skills are modular knowledge units that teach Claude how to perform specific tasks. Each Skill is a **folder** containing a `SKILL.md` file (Markdown with YAML frontmatter) plus any supporting scripts or resources.

### Minimal Structure

```
skill_name/
├── SKILL.md          # Required - instructions with YAML frontmatter
├── scripts/          # Optional - executable tools
├── examples/         # Optional - reference examples
└── resources/        # Optional - templates, data files
```

### SKILL.md Format

The frontmatter minimally includes a unique `name` and a `description` of the Skill. Below the frontmatter, the Markdown content contains the instructions, examples, and guidelines that Claude will follow when the Skill is active.

**Example:**

```markdown
---
name: my-skill-name
description: Clear description of what this skill does and when to use it
---

# My Skill Name

[Instructions that Claude will follow...]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

### Advanced YAML Fields

Skills may include additional frontmatter fields:

```yaml
---
name: my-skill-name
description: What this skill does and when to use it
version: 1.0
author: team_name
allowed-tools: [Read, Write, Bash]  # Tool restrictions (Claude Code)
dependencies: [other_skill_name]     # Skill composition
---
```

### Referenced Files

Skills may reference additional files in the same directory (e.g., appendices or scripts) that Claude can load "by name" when needed. For example, a PDF processing Skill might include:

```
pdf_processing/
├── SKILL.md
├── FORMS.md          # Referenced in SKILL.md
├── REFERENCE.md      # Additional context
└── scripts/
    └── extract_form_fields.py
```

In Claude Code, Skills can specify **allowed tools** (via an `allowed-tools` YAML field) to restrict what APIs or tools the Skill may invoke.

**Key Principle**: A Skill's structure is simply a folder with `SKILL.md` and any assets; Claude treats this folder as a self-contained task-specific instruction set.

---

## 2. Invocation Logic and Access

### Automatic Discovery

At runtime, Claude **automatically discovers and loads relevant Skills on demand**. The invocation process follows these stages:

#### Stage 1: Preloading (Startup)
During startup, Claude preloads each installed Skill's **name and description** into its system prompt. This is the first level of **"progressive disclosure"**: Claude knows which Skills exist and what they generally do without loading all their content.

#### Stage 2: Relevance Detection (User Request)
When the user issues a request, Claude scans its available Skills and determines which one(s) are relevant to the task. Relevance is determined by:
- Keyword matching in the description
- Semantic similarity between task and skill purpose
- Explicit mentions of skill domains

#### Stage 3: Content Loading (On-Demand)
If a Skill seems useful, Claude will **load its full SKILL.md content into context** (invoking a file-read action). Claude may then also load any referenced files or scripts within that Skill directory **only as needed**.

This way, Claude loads minimal information to solve the task, keeping the context efficient.

### Transparent Invocation

**Skills are invoked transparently** – the user does not manually "call" a Skill by name. Claude simply includes the relevant Skill's instructions in its chain of thought when solving the task.

**Example**: If you ask Claude to create a branded presentation, it will automatically invoke the PowerPoint Skill from its library. In Claude's UI you can often see the Skill names appear in its reasoning trace as it works.

This contrasts with older methods like slash-commands or user-invoked tools; **Skills are model-invoked based on relevance**.

### Code Execution Requirement

Use of Skills requires **Claude's code-execution capability**. Skills can include executable scripts (e.g., Python tools) for reliability or heavy computation.

**Access Requirements**:
- Available to **Pro/Max/Team/Enterprise** users in Claude apps (with Code Execution enabled)
- Available via the **API with the Code Execution tool**
- Admins must enable Skills organization-wide if using team plans

As Anthropic's documentation notes: *"Skills require the Code Execution tool beta, which provides the secure environment they need."*

### Tool and Data Access Control

Access to tools and data can be controlled at the Skill level:

- In **Claude Code**, a Skill's frontmatter can include an `allowed-tools` list to limit which file or API tools the Skill may call
- By default, a Skill has whatever tool access the agent has
- Designers can tighten permissions via YAML frontmatter

**Example:**

```yaml
---
name: safe-reader
description: Read-only file analysis skill
allowed-tools: [Read, Grep, Glob]  # Cannot Write or execute Bash
---
```

Overall, Skills offer declarative "permissions" in their metadata, and Claude will only execute attached code or tools when the task requires it and the Skill's instructions direct it.

---

## 3. Purpose and Capabilities

### Core Purpose

Claude Skills serve as **reusable, modular instruction sets** for specific tasks or workflows. Their purpose is to capture domain knowledge and procedures so that Claude can "remember" how to do them consistently.

As Anthropic describes: *"Skills teach Claude how to complete specific tasks in a repeatable way."*

**Use Cases**:
- Organizational playbooks (brand guidelines, email templates)
- Data analysis methods
- Form filling workflows
- Document processing pipelines
- Code review checklists

This yields **more consistent, reliable outputs** for domain-specific tasks.

### Performance Improvements

Skills improve Claude's performance on narrowly-defined tasks by:

1. **Speed**: Drawing on concise instructions instead of general knowledge
2. **Accuracy**: Following tested procedures reduces error rates
3. **Consistency**: Same instructions = same behavior across sessions
4. **Complexity**: Handling complex file formats or external tools via pre-built scripts

**Example**: Instead of Claude guessing how to parse a PDF form, a Skill might include a ready-made Python script for PDF parsing or database queries, which Claude can invoke.

In effect, **Skills act like "mini-plugins" or specialized tools** within Claude's toolbox.

### Composability

**Skills are composable**: Claude can invoke multiple Skills in one task if needed.

**Example Workflow**:
```
User Request: "Analyze sales data and create branded chart"

Claude invokes:
1. data-cleaning Skill → Clean CSV
2. analysis Skill → Calculate metrics
3. chart-generation Skill → Create visualization
4. brand-guidelines Skill → Apply company colors/fonts
```

Claude automatically "stacks" Skills by loading each Skill's instructions sequentially as it reasons. This **composability makes Skills powerful for multifaceted workflows**.

### Capability Taxonomy

The official Skills GitHub repo provides a taxonomy of example capabilities:

**Creative & Design**:
- algorithmic-art
- slack-gif-creator
- canvas-design

**Technical Skills**:
- webapp-testing
- MCP server integration
- code-reviewer

**Enterprise Skills**:
- brand-guidelines
- internal-comms
- meeting-notes

**Meta-Skills**:
- skill-creator (generates new Skills)
- template-skill (boilerplate for new Skills)

**Document Skills**:
- Word/PDF/Excel/PowerPoint manipulation
- Form filling
- Format conversion

Anthropic released document-skills as reference snapshots (not actively maintained), demonstrating complex file handling patterns.

**Summary**: Skills package expert behaviors (from art design to code reviewing) into directories that Claude can use on demand.

---

## 4. Comparison: Skills vs Subagents

Claude Skills are a new paradigm that differs from **Claude Code's subagents**.

### What Are Subagents?

**Subagents** are essentially separate AI assistants with their own system prompts and context. In Claude Code, a subagent runs as an independent "bot" (for example, a code-reviewer or data-scientist) in its own conversation thread.

**Key Properties**:
- Each subagent has an **isolated context window**
- Own **allowed tools** and **custom system prompts**
- Can be invoked **explicitly by name** or **automatically delegated**

### What Are Skills?

**Skills** are not separate agents but **contextual instructions in the main conversation**. Skills run within the single Claude agent instance, expanding its system prompt with extra guidance.

**Key Properties**:
- Run in the **same context window** as main conversation
- Invoked **automatically by relevance detection**
- Contribute to system prompt via **progressive disclosure**

### Comparison Table

| Feature | Claude Skills (SKILL.md) | Claude Subagents (Agents) |
|---------|-------------------------|---------------------------|
| **Invocation** | Model-driven; Claude auto-selects relevant Skills from context | Automatic delegation or explicit user command |
| **Context** | Runs in the main conversation; Skill instructions loaded into the system prompt | Own context window with separate system prompt |
| **Configuration** | SKILL.md (YAML frontmatter + instructions) | Single Markdown with YAML (stored under .claude/agents/) |
| **Best for** | Single, well-defined tasks (file formatting, templated workflows) | Complex/multi-step workflows (long debugging, research tasks) |
| **Control** | Claude decides; no manual "skill invocation" needed | More explicit control; user can pick which agent to use |
| **Context Isolation** | No - shares main conversation context | Yes - separate context window preserves isolation |
| **Use Case Example** | "Apply brand colors to this slide" | "Debug this entire codebase and fix all errors" |

### When to Use Each

**Use Skills when**:
- Task is well-defined and repeatable
- Need consistent behavior across sessions
- Want automatic, transparent invocation
- Task fits in current context window

**Use Subagents when**:
- Task requires multi-step reasoning over time
- Need context isolation (e.g., code review shouldn't see chat history)
- Explicit agent selection is valuable
- Task requires specialized system prompt

**In Practice**: Skills are like tools that Claude latches onto internally, whereas subagents are like distinct team-members you call in.

---

## 5. Lifecycle: Versioning, Monitoring, and Evolution

### Versioning

Although Skills are text-based, they can be versioned and updated like code.

#### API Support

Anthropic provides API support for skill management:

- **Endpoint**: `/v1/skills`
- **Operations**: Upload, list, update custom Skills programmatically
- **Version Control**: Publish new versions, roll back if needed

#### Console Support

The **Claude Console UI** allows:
- Creating Skills via graphical interface
- Upgrading skill versions
- Managing skill library

#### Best Practices

The YAML frontmatter has no built-in version field, but **best practices** suggest:

1. **Document version history inside SKILL.md**:
```markdown
## Version History

### v1.2 (2025-10-20)
- Added error handling for missing fields
- Improved example clarity

### v1.1 (2025-10-15)
- Fixed brand color hex codes
- Added PDF output option

### v1.0 (2025-10-01)
- Initial release
```

2. **Use YAML version field** (unofficial but recommended):
```yaml
---
name: my-skill
description: What it does
version: 1.2
changelog: See Version History section below
---
```

3. **Git-based versioning** (for team workflows):
```bash
.claude/skills/my-skill/
├── SKILL.md          # Current version
└── versions/
    ├── v1.0.md
    ├── v1.1.md
    └── v1.2.md
```

### Monitoring and Outcomes

#### Logging

Outcomes from Skill usage can be logged and analyzed externally:

- **Chain-of-thought logs** show which Skills were invoked (skill names appear in reasoning traces)
- **Tool outputs** and final answers can be captured
- **Conversation logs** preserve full interaction history

**Example Log Entry**:
```json
{
  "timestamp": "2025-10-20T14:30:00Z",
  "task": "Create branded presentation",
  "skills_invoked": ["brand-guidelines", "powerpoint"],
  "outcome": "success",
  "correction_needed": false,
  "latency_ms": 3400
}
```

#### Metrics

While Anthropic does not currently auto-score skill success, developers can compute metrics:

- **Accuracy**: Did the output meet requirements?
- **Completion time**: How long did Skill execution take?
- **User satisfaction**: Human feedback on quality
- **Correction rate**: How often was output revised?
- **Activation rate**: How often was Skill chosen when relevant?

**Example Analysis**:
```python
# Analyze Skill performance from logs
skill_metrics = {
    "brand-guidelines": {
        "invocations": 47,
        "corrections_needed": 3,
        "success_rate": 0.936,
        "avg_latency_ms": 450
    }
}
```

#### Feedback Collection

Teams can gather feedback by:
- Having users test Skills and report activation accuracy
- A/B testing different Skill versions
- Tracking whether Skills produced desired results

### Autonomous Evolution

In a dynamic agent system, an **external monitor** (e.g., another AI agent) could use logs to evaluate Skill performance.

#### Reinforcement Loop Pattern

```
1. Execute Skill → Log outcome
2. Compare intended vs actual results
3. Assign performance score
4. If score < threshold:
   - Analyze failure pattern
   - Modify SKILL.md instructions
   - Increment version
5. Republish updated Skill
6. Repeat
```

**Example Meta-Agent Workflow**:

```python
def evolve_skill(skill_name, performance_logs):
    """Meta-agent analyzes Skill performance and suggests improvements"""

    # Calculate metrics
    success_rate = calculate_success_rate(performance_logs)
    common_failures = identify_failure_patterns(performance_logs)

    if success_rate < 0.90:  # 90% threshold
        # Ask Qwen to analyze failures
        analysis = qwen.analyze_skill_failures(
            skill_name=skill_name,
            failures=common_failures
        )

        # Generate improved instructions
        improved_skill = qwen.suggest_skill_improvements(
            current_skill=read_skill(skill_name),
            analysis=analysis
        )

        # A/B test the variation
        test_results = ab_test_skill_versions(
            current=read_skill(skill_name),
            candidate=improved_skill,
            tasks=get_benchmark_tasks(skill_name)
        )

        # If improvement validated, update
        if test_results.candidate_score > test_results.current_score:
            update_skill(skill_name, improved_skill)
            increment_version(skill_name)
            log_evolution_event(skill_name, analysis, test_results)
```

#### Anthropic's Vision

As Anthropic describes:

> *"We envision agents eventually creating, editing, and evaluating Skills on their own, letting them codify their own patterns of behavior into reusable capabilities."*

This suggests a future where:
- Claude monitors its own Skill usage
- Identifies underperforming Skills
- Proposes instruction improvements
- Tests variations automatically
- Evolves Skills based on real-world performance

### Practical Implementation

**Manual Evolution** (current state):
1. Review conversation logs
2. Identify Skill failures or inefficiencies
3. Edit SKILL.md with improvements
4. Republish via API or Console
5. Track new version performance

**Semi-Automated Evolution** (Foundups approach):
1. Qwen analyzes Skill performance logs
2. Gemma validates pattern fidelity (did Claude follow instructions?)
3. 0102 reviews proposed changes
4. System A/B tests variations
5. Winning version becomes new stable

**Fully Autonomous Evolution** (future):
1. Skills monitor their own outcomes
2. Meta-agent continuously evaluates performance
3. Genetic algorithm explores instruction variations
4. Statistical validation determines winners
5. Skills self-update without human intervention

**Key Insight**: The simple text format makes Skills amenable to iteration. Developers can track versions via API or in SKILL.md content, log performance via Claude's output traces, and incorporate user feedback. This transforms Skills into **evolving modules** rather than static templates.

---

## 6. Claude Skills GitHub Repository

Anthropic maintains a public GitHub repository of example Skills:

**URL**: https://github.com/anthropics/skills

### Repository Structure

The repo demonstrates many patterns and best practices. Each Skill example is a folder with its own `SKILL.md`.

### Categories

#### Creative & Design
- algorithmic-art
- canvas-design
- slack-gif-creator

#### Development & Technical
- webapp-testing
- mcp-server (Model Context Protocol integration)
- code-reviewer

#### Enterprise & Communication
- brand-guidelines
- internal-comms
- meeting-notes

#### Meta Skills
- **skill-creator**: Generates new Skills
- **template-skill**: Boilerplate for new Skills

#### Document Skills
- **docx**: Microsoft Word manipulation
- **pdf**: PDF processing and form filling
- **pptx**: PowerPoint creation
- **xlsx**: Excel analysis

These document-skills illustrate complex file handling patterns (though marked as reference snapshots, not actively maintained).

### Example: template-skill

```markdown
---
name: template-skill
description: Minimal boilerplate for creating new Skills
---

# Template Skill

This is a template for creating new Claude Skills.

## Instructions

[Your task-specific instructions here]

## Examples

- Example 1: Show how to use this skill
- Example 2: Another use case

## Guidelines

- Guideline 1: Best practice
- Guideline 2: What to avoid
```

### Example: PDF Processing Skill

```
pdf/
├── SKILL.md          # Main instructions
├── FORMS.md          # Form-filling procedures
├── REFERENCE.md      # PDF format documentation
└── scripts/
    ├── extract_fields.py
    └── fill_form.py
```

**SKILL.md excerpt**:
```markdown
---
name: pdf-processing
description: Extract data from PDFs and fill forms programmatically
---

# PDF Processing Skill

## Instructions

When processing PDFs:
1. Use extract_fields.py to identify form fields
2. Reference FORMS.md for field naming conventions
3. Use fill_form.py to populate data
4. Validate output with REFERENCE.md guidelines

## Available Scripts

- `extract_fields.py`: Parse PDF structure
- `fill_form.py`: Fill form fields with data
```

### Using the Repository

#### As a Plugin Marketplace

Developers can use this repository as a **plugin marketplace** in Claude Code:

1. Clone the repo
2. Select specific Skill sets to add
3. Copy to `.claude/skills/` directory
4. Claude automatically discovers them

#### Learning Resource

The README emphasizes:

> *"Just a folder with a SKILL.md file containing YAML frontmatter and instructions."*

Reading the examples is invaluable for understanding:
- How to structure instructions
- When to bundle scripts
- How to reference external files
- Best practices for descriptions

### Contributing

The repository welcomes community contributions of new Skills, following the established patterns.

---

## 7. Integration with Foundups Architecture

### Foundups-Specific Patterns

Our `.claude/skills/` structure extends Anthropic's base pattern with **recursive evolution support**:

```
.claude/skills/
├── qwen_wsp_enhancement/
│   ├── SKILL.md                # Anthropic-compliant base
│   ├── versions/               # Version history (Foundups extension)
│   ├── metrics/                # Performance tracking (Foundups extension)
│   ├── variations/             # A/B test candidates (Foundups extension)
│   └── CHANGELOG.md            # Evolution rationale (Foundups extension)
└── youtube_dae/
    ├── SKILL.md
    ├── versions/
    ├── metrics/
    ├── variations/
    └── CHANGELOG.md
```

### Compliance Matrix

| Anthropic Requirement | Foundups Implementation | Status |
|----------------------|------------------------|--------|
| `.claude/skills/` location | ✅ Migrated from root `skills/` | COMPLIANT |
| Folder structure per skill | ✅ Each skill has own directory | COMPLIANT |
| SKILL.md with YAML frontmatter | ✅ All skills have proper YAML | COMPLIANT |
| Name and description required | ✅ All skills properly documented | COMPLIANT |
| Optional allowed-tools field | ⏳ Not yet used (future) | N/A |
| Supporting files in skill dir | ⏳ Planned for resources/ | PLANNED |

### Foundups Extensions

**Beyond Anthropic Spec** (backwards-compatible):

1. **versions/** - Git-tracked evolution history
2. **metrics/** - Gemma pattern fidelity + outcome quality JSON
3. **variations/** - A/B test candidate instructions
4. **CHANGELOG.md** - Human-readable evolution rationale
5. **WSP compliance tags** - Links to relevant WSP protocols

These extensions **do not break** Anthropic compatibility - they simply add metadata that Claude ignores if not instructed to use.

### Meta-Documentation Location

```
.claude/skills/_meta/
├── ANTHROPIC_SKILLS_DEEP_DIVE.md    # This file
├── wsp/
│   └── WSP_SKILLS_RECURSIVE_EVOLUTION.md  # Foundups-specific evolution protocol
└── README.md                         # System overview
```

The `_meta/` directory preserves documentation without polluting the skill namespace.

---

## 8. Summary

Claude Skills are **modular, task-specific instruction sets** that Claude can load and apply dynamically. They are written in Markdown (SKILL.md) with a simple YAML header (name, description, allowed tools, etc.) and any necessary scripts or files attached.

### Core Properties

1. **Structure**: Folder with SKILL.md + optional resources
2. **Invocation**: Automatic, model-driven relevance detection
3. **Execution**: Requires Code Execution capability
4. **Composability**: Multiple Skills can be stacked for complex tasks
5. **Versioning**: API and Console support for updates
6. **Evolution**: Logs enable performance monitoring and iterative improvement

### Key Advantages

- ✅ **Consistency**: Same instructions = same behavior
- ✅ **Efficiency**: Progressive disclosure keeps context lean
- ✅ **Portability**: Works across Claude.ai, Claude Code, and API
- ✅ **Composability**: Skills can be combined for complex workflows
- ✅ **Evolvability**: Simple text format enables version control and iteration

### Future Vision

While Claude does not yet natively "learn" from Skill performance, the system is designed so that outputs can be logged and used to refine skills manually or programmatically.

**Anthropic's Vision**:

> *"In the future, an external agent (or Claude itself) might monitor Skill success, adjust YAML or text prompts, and redeploy improved versions, effectively giving Skills a reinforcement-learning-like feedback loop."*

**Foundups Implementation**: We've built exactly this system - Qwen analyzes patterns, Gemma scores fidelity, 0102 supervises, and Skills evolve based on data.

---

## 9. References

**Official Anthropic Documentation**:
- Claude Skills Documentation: support.claude.com
- Skills API Reference: anthropic.com/api
- Engineering Blog: anthropic.com/blog
- Skills GitHub Repository: github.com/anthropics/skills

**Foundups-Specific**:
- [WSP Skills Recursive Evolution](wsp/WSP_SKILLS_RECURSIVE_EVOLUTION.md)
- [Migration Plan](../MIGRATION_PLAN.md)
- [Skills README](../README.md)

---

**Last Updated**: 2025-10-20
**Source**: Anthropic official documentation + community analysis
**Foundups Compliance**: ✅ ANTHROPIC-COMPLIANT + RECURSIVE-EVOLUTION-ENABLED
