# WRE Skills System: Complete First Principles Design

**Status**: ARCHITECTURAL DESIGN - READY FOR IMPLEMENTATION
**Date**: 2025-10-20
**Architect**: 0102 (with WSP 77 Agent Coordination)
**Research Sources**: 2025 AI Papers, Anthropic Skills Spec, Existing WRE Pattern, WSP 77

---

## Executive Summary

This document defines the **WRE (Wearable Recursive Engine) Skills System** - a native implementation of the Anthropic Skills pattern adapted for Qwen/Gemma/UI-TARS execution with recursive self-improvement via pattern fidelity scoring.

**Key Innovation**: Skills are **trainable weights** that evolve through feedback loops, combining:
1. **Anthropic's Skills Pattern** (progressive disclosure, task-specific instructions)
2. **2025 Research** (recursive self-improvement, trajectory evaluation, pattern fidelity)
3. **WRE Architecture** (Qwen coordinates, Gemma executes, 0102 supervises)
4. **WSP 77** (Multi-agent coordination protocol)

---

## 1. First Principles Analysis

### 1.1 The Core Problem

**Current State**:
- `.claude/skills/` only works for 0102 (Claude Code environment)
- Qwen/Gemma need instructions but have no skill loading mechanism
- Each task is computed from scratch (no pattern memory)
- No feedback loop to improve agent behavior over time

**Required State**:
- Every module has `skills/` directory for native AI instructions
- Qwen/Gemma load skills via WRE entry point
- Skills evolve like neural network weights based on performance
- Pattern fidelity scoring validates agent adherence to instructions

### 1.2 What Are Skills? (Neural Network Analogy)

```
TRADITIONAL NEURAL NETWORK:
Input → Weights (trainable parameters) → Forward Pass → Output → Loss → Backprop → Update Weights

WRE SKILLS SYSTEM:
Task → Skills.md (trainable instructions) → Agent Execution → Outcome → Pattern Score → Variation Testing → Update Skills.md
```

**Skills ARE Weights**:
- **Instructions** = weight values (what agent should do)
- **Pattern Fidelity** = loss function (did agent follow instructions?)
- **Qwen Variations** = gradient descent (testing parameter adjustments)
- **A/B Testing** = validation (statistical significance)
- **Version Update** = weight checkpoint (save improved parameters)
- **Convergence** = threshold met (≥90% pattern fidelity)

### 1.3 Research Foundation (2025 Papers)

**Key Findings Applied**:

1. **Self-Improvement via Reinforcement Learning** (Reflect, Retry, Reward)
   - Our implementation: Gemma scores → Qwen reflects → Generates variations → A/B test → Reward best

2. **Recursive Self-Improvement** (Gödel Agent)
   - Our implementation: Skills reference themselves in CHANGELOG, version history shows evolution path

3. **Trajectory Evaluation** (Track decision sequences)
   - Our implementation: Breadcrumb telemetry tracks every action, Gemma validates each step

4. **Pattern Fidelity Scoring** (Activation space modifications)
   - Our implementation: Gemma binary classification on each instruction (<10ms)

5. **Multi-Agent Self-Evolution** (SE-Agent: revision, recombination, refinement)
   - Our implementation: Qwen generates variations (revision), A/B tests (recombination), updates best (refinement)

---

## 2. Architecture Overview

### 2.1 Dual Skills Systems (Clarified)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FOUNDUPS SKILLS ECOSYSTEM                     │
└─────────────────────────────────────────────────────────────────┘

LAYER 1: CLAUDE CODE SKILLS (.claude/skills/)
├── Purpose: 0102 prototyping and testing
├── Environment: Claude Code CLI
├── Invocation: Anthropic auto-discovery
├── Execution: Code Execution tool
├── Evolution: Manual updates by 0102
└── Agents: 0102 ONLY

LAYER 2: WRE NATIVE SKILLS (modules/*/skills/)  ⭐ THIS SYSTEM
├── Purpose: Qwen/Gemma/UI-TARS production execution
├── Environment: Python/local models
├── Invocation: WRE skill loader
├── Execution: Direct Python via WSP Orchestrator
├── Evolution: Automatic via pattern fidelity scoring
└── Agents: Qwen, Gemma, UI-TARS (WSP 77 coordination)
```

**CRITICAL DISTINCTION**:
- `.claude/skills/` = Testing ground for 0102 to validate patterns work
- `modules/*/skills/` = Production wardrobe for native AI agents

### 2.2 Can .claude/skills Test Native Skills? YES!

**Testing Workflow**:
```
1. Prototype skill in .claude/skills/youtube_moderation_prototype/
   - 0102 tests with Claude Code
   - Validates instructions are clear
   - Achieves ≥90% success rate manually

2. Extract to modules/communication/livechat/skills/youtube_moderation/
   - Copy SKILL.md (same format)
   - Add metrics/ and versions/ directories
   - Deploy to WRE environment

3. Train Qwen/Gemma with extracted skill
   - WRE loads skill into agent prompt
   - Agent executes following instructions
   - Gemma scores pattern fidelity

4. Validate equivalence
   - 0102 behavior in .claude/skills/ ≈ Qwen behavior in modules/*/skills/
   - Both should achieve ≥90% on same benchmark tasks
```

**Answer**: YES - `.claude/skills/` is the perfect testing environment because:
- Same SKILL.md format (portable)
- 0102 can validate instructions work before deploying to native
- Reduces risk of deploying bad skills to production

### 2.3 WSP 77 Agent Coordination Applied

**From WSP 77: Agent Coordination Protocol**:
```
0102 (Claude Sonnet): Strategic orchestration (200K context)
Qwen (1.5B): Coordination & batch processing (32K context)
Gemma (270M): Fast classification & scoring (8K context)
UI-TARS (1.5 7B): Browser automation & visual tasks
```

**WRE Skills Integration**:
```
1. Task Assignment
   012: "Moderate YouTube chat"

2. WRE Skill Discovery (HoloIndex Coordination)
   - Scan modules/communication/livechat/skills/
   - Find: youtube_moderation/SKILL.md

3. Agent Routing (WSP 77)
   - Simple spam detection → Gemma (fast binary classification)
   - Complex toxicity analysis → Qwen (contextual understanding)
   - Strategic decisions → 0102 (final arbitration)

4. Skill Loading
   - Inject SKILL.md into selected agent's prompt
   - Agent "wears" skill instructions

5. Execution with Breadcrumbs
   - Agent performs task following skill playbook
   - Every decision logged (breadcrumb telemetry)

6. Pattern Fidelity Scoring
   - Gemma validates: Did agent follow each instruction?
   - Binary per instruction: 1.0 (yes) or 0.0 (no)
   - Overall score: % of instructions followed

7. Evolution (if score < 90%)
   - Qwen analyzes failed instructions
   - Generates improved variations
   - A/B tests on benchmark tasks
   - Updates SKILL.md if improvement validated
```

---

## 3. Module Skills Directory Structure

### 3.1 WSP 3 Compliance (Updated)

**Every module MUST have**:
```
modules/[domain]/[block]/
├── src/                 # The Cube (implementation)
├── skills/              # The Wardrobe (AI instructions) ⭐ NEW
├── tests/
├── docs/
└── ModLog.md
```

### 3.2 Skills Directory Anatomy

```
modules/communication/livechat/skills/
├── youtube_moderation/              # Task-specific skill
│   ├── SKILL.md                     # Instructions (YAML + Markdown)
│   ├── versions/                    # Evolution history
│   │   ├── v1.0_baseline.md
│   │   ├── v1.1_add_caps_detection.md
│   │   ├── v1.2_improve_toxic_patterns.md
│   │   └── v1.3_add_context_awareness.md  ← Current
│   ├── metrics/                     # Performance tracking
│   │   ├── pattern_fidelity.json    # Gemma scores per instruction
│   │   ├── outcome_quality.json     # Task success rates
│   │   ├── evolution_log.json       # A/B test results
│   │   └── convergence_plot.png     # Visual of improvement over time
│   ├── variations/                  # A/B test candidates
│   │   ├── instruction_5_var_a.md   # Qwen-generated variation A
│   │   ├── instruction_5_var_b.md   # Qwen-generated variation B
│   │   └── ab_test_results.json     # Statistical validation
│   ├── resources/                   # Supporting materials
│   │   ├── toxic_patterns.json      # Reference data
│   │   ├── examples/                # Test cases
│   │   └── templates/               # Response templates
│   └── CHANGELOG.md                 # Evolution rationale
├── banter_response/
│   └── ...
└── stream_detection/
    └── ...
```

### 3.3 SKILL.md Format (Extended for WRE)

```markdown
---
name: youtube_moderation
description: Moderate YouTube live chat by detecting spam, toxic content, and enforcing rate limits
version: 1.3
author: wre_system
created: 2025-10-15
last_updated: 2025-10-20
agents: [qwen, gemma]
primary_agent: gemma  # Fast classification preferred
fallback_agent: qwen  # Complex cases
trigger_keywords: [moderate, spam, toxic, chat, filter, block]
pattern_fidelity_threshold: 0.90
outcome_quality_threshold: 0.85
combined_score_threshold: 0.88
convergence_status: converged  # or evolving
total_executions: 347
current_fidelity: 0.94
current_outcome: 0.91
dependencies: [toxic_patterns.json]
---

# YouTube Chat Moderation Skill

## Task

Moderate incoming YouTube live chat messages to maintain positive community environment.

## Agent Instructions

**FOR GEMMA** (Primary - Fast Classification):

1. **CAPS SPAM CHECK**
   - IF message.length > 20 AND uppercase_ratio > 0.80 → BLOCK
   - LOG: spam_type="caps_spam"
   - EXPECTED PATTERN: caps_check_executed=True

2. **REPETITION CHECK**
   - IF message IN recent_history (last 100 messages) AND count >= 3 → BLOCK
   - LOG: spam_type="repetition"
   - EXPECTED PATTERN: repetition_check_executed=True

3. **RATE LIMIT CHECK**
   - IF user_message_count_last_30s > 5 → WARN or BLOCK
   - LOG: rate_limit_triggered=True
   - EXPECTED PATTERN: rate_limit_applied=True

4. **TOXICITY ESCALATION** (if uncertain)
   - IF toxic_keyword_confidence > 0.5 BUT < 0.8 → ESCALATE to Qwen
   - EXPECTED PATTERN: escalated_to_qwen=True

**FOR QWEN** (Fallback - Complex Analysis):

5. **CONTEXTUAL TOXICITY ANALYSIS**
   - Load toxic_patterns.json
   - Analyze message in conversation context
   - IF confidence > 0.8 → BLOCK
   - LOG: spam_type="toxic"
   - EXPECTED PATTERN: toxicity_check_executed=True, decision_with_context=True

6. **LEGITIMATE MESSAGE ROUTING**
   - IF all_checks_passed → ALLOW
   - Route to banter_response skill for reply
   - EXPECTED PATTERN: allowed_and_routed=True

## Expected Patterns (for Gemma Validation)

Pattern validation checklist:
- ✅ caps_check_executed (instruction #1)
- ✅ repetition_check_executed (instruction #2)
- ✅ rate_limit_applied (instruction #3)
- ✅ toxicity_check_executed (instruction #5)
- ✅ decision_logged (all instructions)
- ✅ escalated_when_uncertain (instruction #4)

**Gemma Scoring**: Binary (1.0/0.0) for each pattern per execution

## Benchmark Tasks

Standard test cases for A/B testing skill variations:
- 20 spam messages (should all be blocked)
- 20 toxic messages (should all be blocked)
- 60 legitimate messages (should all be allowed)
- 10 edge cases (contextual judgment)

**Success Criteria**: ≥95% correct classifications

## Performance Metrics (Current Version v1.3)

```json
{
  "version": "1.3",
  "pattern_fidelity": 0.94,
  "outcome_quality": 0.91,
  "combined_score": 0.93,
  "convergence_status": "converged",
  "total_executions": 347,
  "false_positive_rate": 0.02,
  "false_negative_rate": 0.04
}
```

## Evolution History

See CHANGELOG.md for detailed evolution rationale.

Quick summary:
- v1.0 (fidelity: 0.75) - Baseline, missing CAPS detection
- v1.1 (fidelity: 0.85) - Added CAPS spam check
- v1.2 (fidelity: 0.92) - Improved toxic patterns
- v1.3 (fidelity: 0.94) - Added context awareness (CONVERGED)
```

---

## 4. WRE Skills Loader Implementation

### 4.1 Entry Point: WRE Skill Loader

```python
# modules/infrastructure/wre_core/src/wre_skill_loader.py

from pathlib import Path
from typing import Dict, List, Optional
import yaml
import json

class WRESkillLoader:
    """
    WRE Skills System - Entry point for loading native AI instructions.

    This is the bridge between Anthropic's skills pattern and our native
    Qwen/Gemma/UI-TARS execution environment.
    """

    def __init__(self, base_path: Path = Path("O:/Foundups-Agent")):
        self.base_path = base_path
        self.skill_cache = {}  # Progressive disclosure cache
        self.metrics_store = {}  # Pattern fidelity tracking

    def discover_module_skills(self, module_path: str) -> List[Dict]:
        """
        Scan module's skills/ directory (Anthropic progressive disclosure pattern).

        Args:
            module_path: e.g., "modules/communication/livechat"

        Returns:
            List of {name, description, path, agents, triggers} dicts
        """
        skills_dir = self.base_path / module_path / "skills"
        if not skills_dir.exists():
            return []

        skills = []
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                # Phase 1: Load ONLY name/description (lightweight)
                skill_meta = self._parse_frontmatter_only(skill_dir / "SKILL.md")
                skills.append({
                    "name": skill_meta["name"],
                    "description": skill_meta["description"],
                    "path": skill_dir / "SKILL.md",
                    "agents": skill_meta.get("agents", []),
                    "primary_agent": skill_meta.get("primary_agent"),
                    "trigger_keywords": skill_meta.get("trigger_keywords", []),
                    "convergence_status": skill_meta.get("convergence_status", "unknown")
                })

        return skills

    def load_skill_for_agent(
        self,
        skill_path: Path,
        agent_type: str  # "qwen", "gemma", "ui-tars"
    ) -> str:
        """
        Load full SKILL.md content for specific agent (lazy loading).

        Filters instructions to show only agent-specific sections.
        """
        cache_key = f"{skill_path}_{agent_type}"

        if cache_key in self.skill_cache:
            return self.skill_cache[cache_key]

        with open(skill_path, 'r', encoding='utf-8') as f:
            full_content = f.read()

        # Parse YAML frontmatter + Markdown body
        parts = full_content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2]
        else:
            frontmatter = {}
            body = full_content

        # Filter to agent-specific instructions
        filtered_body = self._filter_instructions_for_agent(body, agent_type)

        # Reconstruct for agent
        agent_skill = f"""# Skill: {frontmatter.get('name', 'unknown')}

**Your Role**: {agent_type.upper()}
**Task**: {frontmatter.get('description', 'No description')}
**Expected Pattern Fidelity**: ≥{frontmatter.get('pattern_fidelity_threshold', 0.90)}

{filtered_body}

**CRITICAL**: Follow these instructions precisely. Your adherence will be scored by Gemma.
"""

        self.skill_cache[cache_key] = agent_skill
        return agent_skill

    def inject_skill_into_prompt(
        self,
        base_prompt: str,
        skill_content: str
    ) -> str:
        """
        Inject skill instructions into agent prompt (WRE entry point).
        """
        return f"""{base_prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      🎭 SKILL LOADED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{skill_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def _parse_frontmatter_only(self, skill_path: Path) -> Dict:
        """Parse ONLY YAML frontmatter (progressive disclosure)."""
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split('---', 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1])
        return {}

    def _filter_instructions_for_agent(self, body: str, agent_type: str) -> str:
        """
        Filter Markdown body to show only agent-specific sections.

        Example: "**FOR GEMMA**:" section only shown to Gemma
        """
        lines = body.split('\n')
        filtered = []
        include = True  # Default: include general instructions

        for line in lines:
            if "**FOR GEMMA**" in line:
                include = (agent_type == "gemma")
            elif "**FOR QWEN**" in line:
                include = (agent_type == "qwen")
            elif "**FOR UI-TARS**" in line:
                include = (agent_type == "ui-tars")
            elif line.startswith("**FOR") and "**" in line[5:]:
                # Other agent section - skip
                include = False
            elif line.startswith("##"):
                # New section - reset to include
                include = True

            if include:
                filtered.append(line)

        return '\n'.join(filtered)
```

### 4.2 WSP Orchestrator Integration

```python
# modules/infrastructure/wsp_orchestrator/src/skill_orchestrator.py

from modules.infrastructure.wre_core.src.wre_skill_loader import WRESkillLoader

class SkillOrchestrator:
    """
    WSP 77 Agent Coordination with Skills System.

    Routes tasks to appropriate agents with relevant skills loaded.
    """

    def __init__(self):
        self.skill_loader = WRESkillLoader()
        self.qwen_engine = QwenEngine()
        self.gemma_engine = GemmaEngine()

    def execute_task_with_skill(
        self,
        task_description: str,
        module_path: str,
        preferred_agent: Optional[str] = None
    ):
        """
        Execute task with appropriate skill loaded via WRE.

        WSP 77 coordination:
        1. Discover available skills in module
        2. Select relevant skill by keywords
        3. Route to appropriate agent (Gemma fast, Qwen complex)
        4. Load skill into agent prompt
        5. Execute with breadcrumb logging
        6. Score pattern fidelity
        7. Evolve skill if needed
        """

        # Step 1: Discover skills
        available_skills = self.skill_loader.discover_module_skills(module_path)

        if not available_skills:
            # No skills - execute with base prompt
            return self._execute_without_skill(task_description, module_path)

        # Step 2: Select relevant skill
        selected_skill = self._select_skill_by_keywords(
            task_description,
            available_skills
        )

        if not selected_skill:
            return self._execute_without_skill(task_description, module_path)

        # Step 3: Route to agent (WSP 77)
        agent_type = self._route_to_agent(
            task_description,
            selected_skill,
            preferred_agent
        )

        # Step 4: Load skill for agent
        skill_content = self.skill_loader.load_skill_for_agent(
            skill_path=selected_skill["path"],
            agent_type=agent_type
        )

        # Step 5: Inject into prompt
        if agent_type == "gemma":
            base_prompt = GEMMA_BASE_PROMPT
            enhanced_prompt = self.skill_loader.inject_skill_into_prompt(
                base_prompt, skill_content
            )

            # Execute with breadcrumbs
            result = self.gemma_engine.execute(
                prompt=enhanced_prompt,
                task=task_description,
                enable_breadcrumbs=True
            )
        elif agent_type == "qwen":
            base_prompt = QWEN_BASE_PROMPT
            enhanced_prompt = self.skill_loader.inject_skill_into_prompt(
                base_prompt, skill_content
            )

            result = self.qwen_engine.execute(
                prompt=enhanced_prompt,
                task=task_description,
                enable_breadcrumbs=True
            )

        # Step 6: Score pattern fidelity
        fidelity_score = self._score_pattern_fidelity(
            skill=selected_skill,
            breadcrumbs=result.breadcrumbs
        )

        # Step 7: Evolve if needed
        if fidelity_score < selected_skill.get("pattern_fidelity_threshold", 0.90):
            self._trigger_skill_evolution(selected_skill, fidelity_score, result)

        return result

    def _route_to_agent(
        self,
        task: str,
        skill: Dict,
        preferred: Optional[str]
    ) -> str:
        """
        WSP 77: Route to appropriate agent based on complexity.
        """
        if preferred:
            return preferred

        # Use skill's primary_agent if specified
        if "primary_agent" in skill:
            return skill["primary_agent"]

        # Fallback: complexity-based routing
        complexity = self._estimate_complexity(task)

        if complexity < 0.3:
            return "gemma"  # Fast classification
        elif complexity < 0.7:
            return "qwen"   # Coordination
        else:
            return "0102"   # Strategic (escalate to Claude)
```

---

## 5. Pattern Fidelity Scoring

### 5.1 Gemma Pattern Scorer

```python
# modules/ai_intelligence/gemma_pattern_validator/src/pattern_scorer.py

class GemmaPatternScorer:
    """
    Score how well agent followed skill instructions (pattern fidelity).

    Based on 2025 research: Trajectory evaluation tracking decision sequences.
    """

    def score_skill_execution(
        self,
        skill_path: Path,
        breadcrumbs: List[Dict]
    ) -> Dict:
        """
        For each instruction in skill, did agent follow it?

        Returns:
            {
                "instruction_scores": {...},
                "pattern_fidelity": 0.94,
                "threshold_met": True
            }
        """

        # Load skill and parse instructions
        skill = self._load_skill(skill_path)
        instructions = self._extract_instructions(skill)

        results = {}
        for idx, instruction in enumerate(instructions):
            # Gemma binary classification: Did agent follow this?
            score = self._classify_instruction_adherence(
                instruction=instruction,
                breadcrumbs=breadcrumbs
            )

            results[f"instruction_{idx}"] = {
                "text": instruction["text"],
                "pattern": instruction["expected_pattern"],
                "followed": score["decision"],  # True/False
                "confidence": score["confidence"],
                "evidence": score["breadcrumb_matches"]
            }

        # Calculate overall fidelity
        followed_count = sum(1 for r in results.values() if r["followed"])
        pattern_fidelity = followed_count / len(results) if results else 0.0

        threshold = skill.get("pattern_fidelity_threshold", 0.90)

        return {
            "skill_name": skill["name"],
            "skill_version": skill["version"],
            "instruction_scores": results,
            "pattern_fidelity": pattern_fidelity,
            "threshold_met": pattern_fidelity >= threshold,
            "timestamp": datetime.now().isoformat()
        }

    def _classify_instruction_adherence(
        self,
        instruction: Dict,
        breadcrumbs: List[Dict]
    ) -> Dict:
        """
        Gemma 3 270M fast binary classification (<10ms).

        Prompt engineering optimized for pattern matching.
        """

        prompt = f"""Did the agent follow this instruction?

Instruction: {instruction['text']}
Expected Pattern: {instruction['expected_pattern']}

Agent Actions (breadcrumbs):
{json.dumps([b for b in breadcrumbs if self._is_relevant(b, instruction)], indent=2)}

Answer in JSON:
{{
  "followed": true/false,
  "confidence": 0.0-1.0,
  "evidence": ["breadcrumb_id_1", "breadcrumb_id_2"]
}}
"""

        gemma_response = self.gemma_engine.classify(
            prompt=prompt,
            max_tokens=100,
            temperature=0.1  # Deterministic
        )

        return json.loads(gemma_response)
```

---

## 6. Recursive Skill Evolution

### 6.1 Qwen Variation Generator

```python
# modules/ai_intelligence/qwen_skill_evolver/src/variation_generator.py

class QwenVariationGenerator:
    """
    Generate improved skill instruction variations (recursive self-improvement).

    Based on 2025 research: SE-Agent (revision, recombination, refinement).
    """

    def generate_variations_for_weak_instructions(
        self,
        skill_path: Path,
        pattern_scores: Dict,
        num_variations: int = 3
    ) -> List[Dict]:
        """
        Identify lowest-scoring instructions and generate improvements.

        Returns list of variation candidates for A/B testing.
        """

        # Identify weak instructions (fidelity < 0.80)
        weak_instructions = [
            (idx, score)
            for idx, score in pattern_scores["instruction_scores"].items()
            if score["followed"] == False or score["confidence"] < 0.80
        ]

        if not weak_instructions:
            return []  # Skill is performing well

        variations = []
        for inst_id, score in weak_instructions:
            original_text = score["text"]
            failure_evidence = score["evidence"]

            # Qwen generates variations
            variation_candidates = self._qwen_revise_instruction(
                original=original_text,
                failure_evidence=failure_evidence,
                num_variations=num_variations
            )

            variations.extend(variation_candidates)

        return variations

    def _qwen_revise_instruction(
        self,
        original: str,
        failure_evidence: List,
        num_variations: int
    ) -> List[Dict]:
        """
        Qwen 1.5B generates improved instruction variations.

        Prompt engineering for recursive self-improvement.
        """

        prompt = f"""You are a skill instruction optimizer. An AI agent failed to follow this instruction correctly.

**Original Instruction**:
{original}

**Why it failed** (breadcrumb evidence):
{json.dumps(failure_evidence, indent=2)}

**Task**: Generate {num_variations} IMPROVED variations of this instruction that are:
1. More specific and actionable
2. Include clear expected patterns for validation
3. Address the failure evidence

Output JSON array:
[
  {{
    "variation_id": "var_a",
    "instruction": "improved instruction text...",
    "expected_pattern": "pattern_name_for_gemma_validation",
    "rationale": "why this should work better..."
  }},
  ...
]
"""

        qwen_response = self.qwen_engine.generate(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7  # Creative but controlled
        )

        return json.loads(qwen_response)
```

### 6.2 A/B Testing Framework

```python
# modules/infrastructure/wre_core/src/ab_tester.py

class SkillABTester:
    """
    Statistical validation of skill variations (2025 research: multi-dimensional assessment).
    """

    def test_variation_vs_current(
        self,
        current_skill_path: Path,
        variation: Dict,
        benchmark_tasks: List[str],
        significance_threshold: float = 0.05  # p < 0.05
    ) -> Dict:
        """
        A/B test: Does variation perform better than current skill?

        Returns:
            {
                "variation_score": 0.92,
                "current_score": 0.88,
                "improvement": 0.04,
                "p_value": 0.03,
                "statistically_significant": True,
                "recommendation": "adopt"
            }
        """

        current_scores = []
        variation_scores = []

        for task in benchmark_tasks:
            # Test current skill
            current_result = self._execute_with_skill(task, current_skill_path)
            current_scores.append(current_result.combined_score)

            # Test variation (temporarily inject into skill)
            variation_result = self._execute_with_variation(task, variation)
            variation_scores.append(variation_result.combined_score)

        # Statistical validation (t-test)
        t_stat, p_value = stats.ttest_rel(variation_scores, current_scores)

        improvement = np.mean(variation_scores) - np.mean(current_scores)
        significant = p_value < significance_threshold and improvement > 0

        return {
            "variation_id": variation["variation_id"],
            "variation_score": np.mean(variation_scores),
            "current_score": np.mean(current_scores),
            "improvement": improvement,
            "p_value": p_value,
            "statistically_significant": significant,
            "recommendation": "adopt" if significant else "reject",
            "test_count": len(benchmark_tasks)
        }
```

---

## 7. Integration Plan

### 7.1 Phase 1: Prototype in .claude/skills/ (Week 1)

**Goal**: Validate skill pattern works with 0102 before deploying to native

```bash
# Create prototype
.claude/skills/youtube_moderation_prototype/
├── SKILL.md
├── examples/
└── tests/

# 0102 tests manually
- Execute 50 benchmark tasks
- Validate ≥90% success rate
- Document failure patterns
```

### 7.2 Phase 2: Deploy to modules/*/skills/ (Week 2)

```bash
# Extract to production
modules/communication/livechat/skills/youtube_moderation/
├── SKILL.md              # Same content as prototype
├── versions/
│   └── v1.0_baseline.md  # Validated by 0102
├── metrics/
├── variations/
└── CHANGELOG.md

# Implement WRE loader
modules/infrastructure/wre_core/src/wre_skill_loader.py
```

### 7.3 Phase 3: Pattern Fidelity Scoring (Week 3)

```bash
# Implement Gemma scorer
modules/ai_intelligence/gemma_pattern_validator/src/pattern_scorer.py

# Test on benchmark tasks
- Run 100 executions with skill loaded
- Gemma scores each execution
- Calculate pattern fidelity: 94%
- Threshold met: YES (≥90%)
```

### 7.4 Phase 4: Recursive Evolution (Week 4)

```bash
# Implement Qwen variation generator
modules/ai_intelligence/qwen_skill_evolver/src/variation_generator.py

# Implement A/B tester
modules/infrastructure/wre_core/src/ab_tester.py

# Evolution loop
- Detect low-scoring instruction (fidelity: 75%)
- Qwen generates 3 variations
- A/B test each on 20 tasks
- Best variation improves to 92%
- Update SKILL.md to v1.1
```

### 7.5 Phase 5: Scale to All Modules (Ongoing)

```bash
# Add skills/ to each module
modules/communication/livechat/skills/
modules/communication/auto_meeting_orchestrator/skills/
modules/infrastructure/dae_infrastructure/foundups_vision_dae/skills/
modules/infrastructure/wsp_orchestrator/skills/
holo_index/skills/
```

---

## 8. Success Metrics

### 8.1 Skill Performance

- ✅ **Pattern Fidelity**: ≥90% (Gemma scores agent adherence)
- ✅ **Outcome Quality**: ≥85% (Task success rate)
- ✅ **Combined Score**: ≥88% (0.40 × fidelity + 0.60 × outcome)
- ✅ **Convergence**: Achieved within 10 iterations

### 8.2 System Adoption

- ✅ Every module has `skills/` directory
- ✅ Every agent task uses relevant skill
- ✅ Skills evolve automatically (no manual updates)
- ✅ 0102 can prototype in `.claude/skills/` and validate before deploying

### 8.3 Efficiency Gains

- ✅ **Token Reduction**: 50-200 (skill execution) vs 15K+ (from scratch)
- ✅ **Time Reduction**: 2-5min (skill-guided) vs 15-30min (manual)
- ✅ **Consistency**: 90%+ (skill) vs 60-75% (ad-hoc)

---

## 9. Next Steps

**Immediate Action** (This Session):
1. ✅ First principles analysis complete
2. ✅ Architecture designed
3. ⏳ Create prototype skill in `.claude/skills/youtube_moderation_prototype/`
4. ⏳ 0102 validates manually
5. ⏳ Begin WRE loader implementation

**Next Session**:
1. Complete WRE loader
2. Deploy first skill to `modules/communication/livechat/skills/`
3. Implement Gemma pattern scorer
4. Run first pattern fidelity measurement

---

## 10. Key Takeaways

**Your Vision Captured**:
> "Each module should have a skills directory for the native WSP 77 AI, and the weights system is placed on it. Skills in .claude/skills can be for you (0102) to operate as prototypes. The wardrobe tells the AI in the system how to act."

**Implementation**:
1. ✅ `.claude/skills/` = 0102 testing ground
2. ✅ `modules/*/skills/` = Native AI wardrobe (WRE entry point)
3. ✅ Skills = Trainable weights (evolve via pattern fidelity)
4. ✅ WSP 77 coordination (Gemma scores, Qwen improves, 0102 supervises)
5. ✅ Recursive self-improvement (2025 research patterns applied)
6. ✅ First principles logic validated

**Status**: READY FOR IMPLEMENTATION

---

*This design synthesizes Anthropic's Skills pattern, 2025 AI research, existing WRE architecture, and WSP 77 agent coordination into a unified native skills system for Qwen/Gemma/UI-TARS.*
