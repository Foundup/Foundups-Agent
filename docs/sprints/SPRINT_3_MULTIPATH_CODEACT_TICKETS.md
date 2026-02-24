# Sprint 3: Multi-Path & CodeAct - Implementation Tickets

**Objective**: Add Tree-of-Thought skill selection (P2-B) + hybrid CodeAct format (P2-E)
**Target**: Multi-candidate skill selection with measured branch scoring
**Duration**: 1 week
**Depends On**: Sprint 1+2 complete (ReAct + TT-SI + RAG + Graph)

---

## Ticket 3.1: Tree-of-Thought Skill Selection

**Priority**: P2 | **Estimate**: 6h | **Owner**: 0102

### Problem
Single skill path chosen directly. Cannot contextually choose among competing high-quality skills when multiple candidates could handle the same intent.

### Target Files
| File | Action |
|------|--------|
| `modules/infrastructure/wre_core/src/skill_selector.py` | CREATE new module |
| `modules/infrastructure/wre_core/src/pattern_memory.py` | ADD skill scoring helpers |
| `modules/infrastructure/wre_core/wre_master_orchestrator/src/wre_master_orchestrator.py` | ADD ToT routing |

### Implementation Steps

#### Step 3.1.1: Add skill scoring methods to PatternMemory

```python
# ------------------------------------------------------------------ #
#  Tree-of-Thought Skill Scoring (Sprint 3 - Gap B)                   #
# ------------------------------------------------------------------ #

def get_skill_fidelity_stats(self, skill_name: str, days: int = 30) -> Dict:
    """
    Get historical fidelity statistics for a skill.

    Returns:
        {
            "skill_name": str,
            "total_executions": int,
            "avg_fidelity": float,
            "success_rate": float,  # fidelity >= 0.7
            "recent_trend": float   # last 7 days vs previous
        }
    """
    cursor = self.conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    recent_cutoff = (datetime.now() - timedelta(days=7)).isoformat()

    # Overall stats
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            AVG(pattern_fidelity) as avg_fidelity,
            SUM(CASE WHEN pattern_fidelity >= 0.7 THEN 1 ELSE 0 END) as successes
        FROM skill_outcomes
        WHERE skill_name = ? AND timestamp >= ?
    """, (skill_name, cutoff))
    row = cursor.fetchone()

    total = row['total'] or 0
    avg_fidelity = row['avg_fidelity'] or 0.5
    success_rate = (row['successes'] or 0) / max(total, 1)

    # Recent trend (last 7 days vs previous)
    cursor.execute("""
        SELECT AVG(pattern_fidelity) as recent_avg
        FROM skill_outcomes
        WHERE skill_name = ? AND timestamp >= ?
    """, (skill_name, recent_cutoff))
    recent_avg = cursor.fetchone()['recent_avg'] or avg_fidelity

    cursor.execute("""
        SELECT AVG(pattern_fidelity) as older_avg
        FROM skill_outcomes
        WHERE skill_name = ? AND timestamp >= ? AND timestamp < ?
    """, (skill_name, cutoff, recent_cutoff))
    older_avg = cursor.fetchone()['older_avg'] or avg_fidelity

    recent_trend = recent_avg - older_avg

    return {
        "skill_name": skill_name,
        "total_executions": total,
        "avg_fidelity": round(avg_fidelity, 3),
        "success_rate": round(success_rate, 3),
        "recent_trend": round(recent_trend, 3)
    }

def rank_skills_for_context(
    self,
    candidate_skills: List[str],
    context_keywords: List[str]
) -> List[Dict]:
    """
    Rank candidate skills by historical fidelity and context match.

    ToT scoring formula:
        score = (0.6 * avg_fidelity) + (0.2 * success_rate) + (0.1 * trend_bonus) + (0.1 * context_match)

    Returns sorted list of {skill_name, score, components}
    """
    scored = []

    for skill in candidate_skills:
        stats = self.get_skill_fidelity_stats(skill)

        # Context match: check if skill name contains context keywords
        context_match = sum(
            1 for kw in context_keywords
            if kw.lower() in skill.lower()
        ) / max(len(context_keywords), 1)

        # Trend bonus: positive trend = bonus, negative = penalty
        trend_bonus = max(0, min(1, 0.5 + stats['recent_trend']))

        # ToT score
        score = (
            0.6 * stats['avg_fidelity'] +
            0.2 * stats['success_rate'] +
            0.1 * trend_bonus +
            0.1 * context_match
        )

        scored.append({
            "skill_name": skill,
            "score": round(score, 3),
            "components": {
                "fidelity": stats['avg_fidelity'],
                "success_rate": stats['success_rate'],
                "trend_bonus": round(trend_bonus, 3),
                "context_match": round(context_match, 3)
            },
            "total_executions": stats['total_executions']
        })

    # Sort by score descending
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored
```

#### Step 3.1.2: Create SkillSelector module

Create `modules/infrastructure/wre_core/src/skill_selector.py`:

```python
"""
Tree-of-Thought Skill Selector (Sprint 3 - Gap B)

Implements multi-candidate skill selection with branch scoring.
Uses historical fidelity, success rate, trend, and context match.

WSP References: WSP 46, WSP 48, WSP 77
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SkillCandidate:
    """A candidate skill for ToT selection."""
    skill_name: str
    score: float
    fidelity: float
    success_rate: float
    trend_bonus: float
    context_match: float
    total_executions: int


@dataclass
class ToTSelection:
    """Result of Tree-of-Thought selection."""
    selected: SkillCandidate
    candidates: List[SkillCandidate]
    selection_reason: str
    confidence: float


class SkillSelector:
    """
    Tree-of-Thought skill selector.

    Given multiple candidate skills that could handle an intent,
    selects the best one based on historical performance and context.
    """

    def __init__(self, pattern_memory, skills_loader=None):
        """
        Initialize selector with memory and optional skills loader.

        Args:
            pattern_memory: PatternMemory instance for fidelity stats
            skills_loader: Optional WRESkillsLoader for skill discovery
        """
        self.memory = pattern_memory
        self.skills_loader = skills_loader
        self.min_executions_for_confidence = 5
        self.cold_start_score = 0.5  # Score for skills with no history

    def select_skill(
        self,
        candidates: List[str],
        context: Dict,
        max_branches: int = 5
    ) -> ToTSelection:
        """
        Select best skill from candidates using ToT scoring.

        Args:
            candidates: List of candidate skill names
            context: Execution context with keywords for matching
            max_branches: Maximum candidates to evaluate

        Returns:
            ToTSelection with selected skill and evaluation details
        """
        if not candidates:
            raise ValueError("No candidate skills provided")

        # Limit branches
        candidates = candidates[:max_branches]

        # Extract context keywords
        context_keywords = self._extract_keywords(context)

        # Score all candidates
        if self.memory:
            ranked = self.memory.rank_skills_for_context(candidates, context_keywords)
        else:
            # Fallback: equal scores
            ranked = [
                {"skill_name": s, "score": self.cold_start_score,
                 "components": {}, "total_executions": 0}
                for s in candidates
            ]

        # Convert to SkillCandidate objects
        skill_candidates = []
        for r in ranked:
            components = r.get("components", {})
            skill_candidates.append(SkillCandidate(
                skill_name=r["skill_name"],
                score=r["score"],
                fidelity=components.get("fidelity", 0.5),
                success_rate=components.get("success_rate", 0.5),
                trend_bonus=components.get("trend_bonus", 0.5),
                context_match=components.get("context_match", 0.0),
                total_executions=r.get("total_executions", 0)
            ))

        # Select best
        selected = skill_candidates[0]

        # Calculate confidence
        confidence = self._calculate_confidence(selected, skill_candidates)

        # Determine selection reason
        reason = self._explain_selection(selected, skill_candidates)

        logger.info(
            f"[TOT-SELECT] Selected {selected.skill_name} "
            f"(score={selected.score:.3f}, confidence={confidence:.3f}) "
            f"from {len(candidates)} candidates"
        )

        return ToTSelection(
            selected=selected,
            candidates=skill_candidates,
            selection_reason=reason,
            confidence=confidence
        )

    def _extract_keywords(self, context: Dict) -> List[str]:
        """Extract keywords from context for matching."""
        keywords = []

        # Common context fields that might contain keywords
        for key in ['intent', 'action', 'query', 'task', 'command']:
            if key in context:
                value = str(context[key])
                # Split on common separators
                keywords.extend(value.replace('_', ' ').replace('-', ' ').split())

        # Also check for explicit keywords field
        if 'keywords' in context:
            keywords.extend(context['keywords'])

        return [k.lower() for k in keywords if len(k) > 2]

    def _calculate_confidence(
        self,
        selected: SkillCandidate,
        all_candidates: List[SkillCandidate]
    ) -> float:
        """
        Calculate selection confidence.

        High confidence when:
        - Large score gap to second place
        - Selected skill has many executions
        - High fidelity history
        """
        if len(all_candidates) < 2:
            return 0.9 if selected.total_executions >= self.min_executions_for_confidence else 0.5

        # Score gap to second place
        second = all_candidates[1]
        score_gap = selected.score - second.score
        gap_confidence = min(1.0, score_gap / 0.2)  # 0.2 gap = full confidence

        # Execution count confidence
        exec_confidence = min(1.0, selected.total_executions / 20)

        # Fidelity confidence
        fidelity_confidence = selected.fidelity

        # Weighted combination
        confidence = (
            0.4 * gap_confidence +
            0.3 * exec_confidence +
            0.3 * fidelity_confidence
        )

        return round(confidence, 3)

    def _explain_selection(
        self,
        selected: SkillCandidate,
        all_candidates: List[SkillCandidate]
    ) -> str:
        """Generate human-readable selection explanation."""
        reasons = []

        if selected.fidelity >= 0.8:
            reasons.append(f"high fidelity ({selected.fidelity:.0%})")

        if selected.success_rate >= 0.8:
            reasons.append(f"high success rate ({selected.success_rate:.0%})")

        if selected.trend_bonus > 0.6:
            reasons.append("improving trend")

        if selected.context_match > 0.5:
            reasons.append("strong context match")

        if selected.total_executions >= 20:
            reasons.append(f"proven ({selected.total_executions} executions)")
        elif selected.total_executions < self.min_executions_for_confidence:
            reasons.append("cold start (limited history)")

        if len(all_candidates) > 1:
            gap = selected.score - all_candidates[1].score
            if gap > 0.1:
                reasons.append(f"clear winner (+{gap:.2f} margin)")

        return "; ".join(reasons) if reasons else "default selection"

    def find_candidates_for_intent(self, intent: str) -> List[str]:
        """
        Find candidate skills that could handle an intent.

        Uses skills_loader if available, otherwise returns empty list.
        """
        if not self.skills_loader:
            return []

        # This would integrate with skills registry
        # For now, return skills matching intent keywords
        all_skills = self.skills_loader.list_skills() if hasattr(self.skills_loader, 'list_skills') else []

        intent_lower = intent.lower()
        candidates = [
            s for s in all_skills
            if any(kw in s.lower() for kw in intent_lower.split('_'))
        ]

        return candidates[:10]  # Limit to top 10 matches
```

#### Step 3.1.3: Wire ToT into WREMasterOrchestrator

In `wre_master_orchestrator.py`, add ToT selection before execution:

```python
# In __init__():
from modules.infrastructure.wre_core.src.skill_selector import SkillSelector
self.skill_selector = SkillSelector(self.sqlite_memory, self.skills_loader)
self.tot_enabled = os.getenv("WRE_TOT_SELECTION", "1").strip() == "1"

# Add new method:
def select_skill_tot(
    self,
    candidates: List[str],
    context: Dict,
    max_branches: int = 5
) -> Tuple[str, Dict]:
    """
    Select best skill from candidates using Tree-of-Thought.

    Returns:
        (selected_skill_name, selection_metadata)
    """
    if not self.tot_enabled or not candidates:
        return candidates[0] if candidates else None, {}

    try:
        selection = self.skill_selector.select_skill(candidates, context, max_branches)

        # Record selection for telemetry
        if self.sqlite_memory:
            self.sqlite_memory.increment_counter("tot_selections")
            if selection.confidence >= 0.7:
                self.sqlite_memory.increment_counter("tot_high_confidence")

        return selection.selected.skill_name, {
            "tot_score": selection.selected.score,
            "tot_confidence": selection.confidence,
            "tot_reason": selection.selection_reason,
            "tot_candidates": len(selection.candidates)
        }
    except Exception as exc:
        logger.warning(f"[WRE-TOT] Selection failed: {exc}")
        return candidates[0], {"tot_error": str(exc)}
```

### Acceptance Criteria
- [ ] `get_skill_fidelity_stats()` returns historical stats
- [ ] `rank_skills_for_context()` scores multiple candidates
- [ ] `SkillSelector` class created with ToT logic
- [ ] Confidence calculation considers score gap and history
- [ ] `select_skill_tot()` wired into orchestrator
- [ ] Telemetry: `tot_selections`, `tot_high_confidence` counters

---

## Ticket 3.2: Hybrid CodeAct Skill Format

**Priority**: P2 | **Estimate**: 4h | **Owner**: 0102

### Problem
Mixed model where some executors are code-based, many flows remain prompt-text execution. Runtime adaptability is limited for complex branching operations.

### Target Files
| File | Action |
|------|--------|
| `modules/infrastructure/wre_core/src/codeact_executor.py` | CREATE hybrid executor |
| `modules/infrastructure/wre_core/src/wre_skills_loader.py` | EXTEND schema support |

### Implementation Steps

#### Step 3.2.1: Define CodeAct skill schema

```python
"""
CodeAct Skill Schema (Sprint 3 - Gap E)

Hybrid format combining declarative prompt with executable code.

Example skill.json:
{
    "name": "git_commit_with_review",
    "version": "1.0.0",
    "format": "codeact",  # NEW: declares hybrid format

    "prompt_section": {
        "description": "Commit changes with pre-commit review",
        "system_prompt": "You are a git expert...",
        "few_shot_examples": [...]
    },

    "code_section": {
        "pre_actions": [
            {"type": "shell", "command": "git status", "capture": "status_output"},
            {"type": "shell", "command": "git diff --stat", "capture": "diff_output"}
        ],
        "conditionals": [
            {
                "if": "len(diff_output.strip()) == 0",
                "then": {"type": "return", "value": {"error": "No changes to commit"}},
                "else": {"type": "continue"}
            }
        ],
        "main_action": {
            "type": "llm_generate",
            "prompt_template": "Review these changes:\n{diff_output}\n\nGenerate commit message:",
            "output_var": "commit_message"
        },
        "post_actions": [
            {"type": "shell", "command": "git commit -m \"{commit_message}\"", "capture": "commit_result"}
        ]
    },

    "safety_gates": {
        "allowed_commands": ["git *", "echo *"],
        "blocked_patterns": ["rm -rf", "sudo *", "> /dev/*"],
        "max_execution_time_ms": 30000,
        "require_confirmation": ["git push", "git reset"]
    }
}
"""
```

#### Step 3.2.2: Create CodeActExecutor

Create `modules/infrastructure/wre_core/src/codeact_executor.py`:

```python
"""
CodeAct Executor (Sprint 3 - Gap E)

Executes hybrid prompt+code skills with safety gates.

WSP References: WSP 46, WSP 50, WSP 64
"""

import logging
import subprocess
import re
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CodeActResult:
    """Result of CodeAct execution."""
    success: bool
    outputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: int = 0
    actions_executed: int = 0
    gates_triggered: List[str] = field(default_factory=list)


@dataclass
class SafetyGates:
    """Safety configuration for CodeAct execution."""
    allowed_commands: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=list)
    max_execution_time_ms: int = 30000
    require_confirmation: List[str] = field(default_factory=list)

    def is_command_allowed(self, command: str) -> bool:
        """Check if command is allowed by safety gates."""
        # Check blocked patterns first
        for pattern in self.blocked_patterns:
            if self._matches_pattern(command, pattern):
                return False

        # If no allowed patterns, allow all (that aren't blocked)
        if not self.allowed_commands:
            return True

        # Check allowed patterns
        for pattern in self.allowed_commands:
            if self._matches_pattern(command, pattern):
                return True

        return False

    def requires_confirmation(self, command: str) -> bool:
        """Check if command requires user confirmation."""
        for pattern in self.require_confirmation:
            if self._matches_pattern(command, pattern):
                return True
        return False

    def _matches_pattern(self, command: str, pattern: str) -> bool:
        """Match command against glob-style pattern."""
        # Convert glob to regex
        regex = pattern.replace('*', '.*').replace('?', '.')
        return bool(re.match(f"^{regex}$", command, re.IGNORECASE))


class CodeActExecutor:
    """
    Executes hybrid CodeAct skills.

    Combines:
    - Pre-actions: Shell commands to gather context
    - Conditionals: Branch based on action results
    - Main action: LLM generation or tool call
    - Post-actions: Execute based on LLM output
    """

    def __init__(
        self,
        repo_root: Path,
        llm_callback=None,
        confirmation_callback=None
    ):
        """
        Initialize CodeAct executor.

        Args:
            repo_root: Repository root for relative paths
            llm_callback: Function(prompt) -> str for LLM generation
            confirmation_callback: Function(command) -> bool for confirmations
        """
        self.repo_root = Path(repo_root)
        self.llm_callback = llm_callback
        self.confirmation_callback = confirmation_callback

    def execute(
        self,
        skill_spec: Dict,
        input_context: Dict,
        safety_override: Optional[SafetyGates] = None
    ) -> CodeActResult:
        """
        Execute a CodeAct skill.

        Args:
            skill_spec: Full skill specification with code_section
            input_context: Input variables for template substitution
            safety_override: Optional safety gates override

        Returns:
            CodeActResult with outputs and execution metadata
        """
        start_time = time.time()
        outputs = dict(input_context)  # Start with input context
        actions_executed = 0
        gates_triggered = []

        # Load safety gates
        gates_spec = skill_spec.get("safety_gates", {})
        gates = safety_override or SafetyGates(
            allowed_commands=gates_spec.get("allowed_commands", []),
            blocked_patterns=gates_spec.get("blocked_patterns", []),
            max_execution_time_ms=gates_spec.get("max_execution_time_ms", 30000),
            require_confirmation=gates_spec.get("require_confirmation", [])
        )

        code_section = skill_spec.get("code_section", {})

        try:
            # Execute pre-actions
            for action in code_section.get("pre_actions", []):
                result = self._execute_action(action, outputs, gates)
                if result.get("error"):
                    return CodeActResult(
                        success=False,
                        outputs=outputs,
                        error=f"Pre-action failed: {result['error']}",
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        actions_executed=actions_executed,
                        gates_triggered=gates_triggered
                    )
                outputs.update(result.get("outputs", {}))
                actions_executed += 1
                if result.get("gate_triggered"):
                    gates_triggered.append(result["gate_triggered"])

            # Evaluate conditionals
            for conditional in code_section.get("conditionals", []):
                condition = conditional.get("if", "True")
                try:
                    # Safe eval with only outputs as context
                    condition_result = eval(condition, {"__builtins__": {}}, outputs)
                except Exception as e:
                    logger.warning(f"[CODEACT] Conditional eval failed: {e}")
                    condition_result = False

                branch = conditional.get("then") if condition_result else conditional.get("else")
                if branch:
                    if branch.get("type") == "return":
                        return CodeActResult(
                            success=True,
                            outputs=branch.get("value", {}),
                            execution_time_ms=int((time.time() - start_time) * 1000),
                            actions_executed=actions_executed,
                            gates_triggered=gates_triggered
                        )
                    # "continue" type just proceeds

            # Execute main action
            main_action = code_section.get("main_action")
            if main_action:
                result = self._execute_action(main_action, outputs, gates)
                if result.get("error"):
                    return CodeActResult(
                        success=False,
                        outputs=outputs,
                        error=f"Main action failed: {result['error']}",
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        actions_executed=actions_executed,
                        gates_triggered=gates_triggered
                    )
                outputs.update(result.get("outputs", {}))
                actions_executed += 1

            # Execute post-actions
            for action in code_section.get("post_actions", []):
                result = self._execute_action(action, outputs, gates)
                if result.get("error"):
                    return CodeActResult(
                        success=False,
                        outputs=outputs,
                        error=f"Post-action failed: {result['error']}",
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        actions_executed=actions_executed,
                        gates_triggered=gates_triggered
                    )
                outputs.update(result.get("outputs", {}))
                actions_executed += 1
                if result.get("gate_triggered"):
                    gates_triggered.append(result["gate_triggered"])

            return CodeActResult(
                success=True,
                outputs=outputs,
                execution_time_ms=int((time.time() - start_time) * 1000),
                actions_executed=actions_executed,
                gates_triggered=gates_triggered
            )

        except Exception as exc:
            logger.error(f"[CODEACT] Execution failed: {exc}")
            return CodeActResult(
                success=False,
                outputs=outputs,
                error=str(exc),
                execution_time_ms=int((time.time() - start_time) * 1000),
                actions_executed=actions_executed,
                gates_triggered=gates_triggered
            )

    def _execute_action(
        self,
        action: Dict,
        context: Dict,
        gates: SafetyGates
    ) -> Dict:
        """Execute a single action."""
        action_type = action.get("type")

        if action_type == "shell":
            return self._execute_shell(action, context, gates)
        elif action_type == "llm_generate":
            return self._execute_llm(action, context)
        elif action_type == "python":
            return self._execute_python(action, context)
        else:
            return {"error": f"Unknown action type: {action_type}"}

    def _execute_shell(self, action: Dict, context: Dict, gates: SafetyGates) -> Dict:
        """Execute shell command with safety checks."""
        command = action.get("command", "")
        capture_var = action.get("capture")

        # Template substitution
        try:
            command = command.format(**context)
        except KeyError as e:
            return {"error": f"Missing context variable: {e}"}

        # Safety check
        if not gates.is_command_allowed(command):
            return {
                "error": f"Command blocked by safety gates: {command}",
                "gate_triggered": f"blocked:{command}"
            }

        # Confirmation check
        if gates.requires_confirmation(command):
            if self.confirmation_callback:
                if not self.confirmation_callback(command):
                    return {
                        "error": f"Command requires confirmation: {command}",
                        "gate_triggered": f"confirmation_denied:{command}"
                    }
            else:
                return {
                    "error": f"Command requires confirmation but no callback: {command}",
                    "gate_triggered": f"confirmation_required:{command}"
                }

        # Execute
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=gates.max_execution_time_ms / 1000,
                cwd=str(self.repo_root)
            )

            output = result.stdout
            if result.returncode != 0 and result.stderr:
                output = f"{output}\nSTDERR: {result.stderr}"

            outputs = {}
            if capture_var:
                outputs[capture_var] = output.strip()

            return {"outputs": outputs}

        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out: {command}"}
        except Exception as e:
            return {"error": f"Shell execution failed: {e}"}

    def _execute_llm(self, action: Dict, context: Dict) -> Dict:
        """Execute LLM generation action."""
        if not self.llm_callback:
            return {"error": "No LLM callback configured"}

        template = action.get("prompt_template", "")
        output_var = action.get("output_var", "llm_output")

        try:
            prompt = template.format(**context)
            result = self.llm_callback(prompt)
            return {"outputs": {output_var: result}}
        except Exception as e:
            return {"error": f"LLM generation failed: {e}"}

    def _execute_python(self, action: Dict, context: Dict) -> Dict:
        """Execute Python code action (sandboxed)."""
        code = action.get("code", "")
        output_var = action.get("output_var", "python_output")

        # Create safe execution environment
        safe_builtins = {
            'len': len, 'str': str, 'int': int, 'float': float,
            'list': list, 'dict': dict, 'bool': bool,
            'min': min, 'max': max, 'sum': sum, 'sorted': sorted,
            'range': range, 'enumerate': enumerate, 'zip': zip
        }

        local_vars = dict(context)

        try:
            exec(code, {"__builtins__": safe_builtins}, local_vars)

            # Extract result if specified
            result = local_vars.get('result', local_vars.get(output_var))
            return {"outputs": {output_var: result}}
        except Exception as e:
            return {"error": f"Python execution failed: {e}"}
```

#### Step 3.2.3: Extend skill loader for CodeAct format

In `wre_skills_loader.py`, add CodeAct detection:

```python
def _detect_skill_format(self, skill_spec: Dict) -> str:
    """Detect skill format: 'prompt', 'codeact', or 'hybrid'."""
    if skill_spec.get("format") == "codeact":
        return "codeact"
    if "code_section" in skill_spec:
        return "codeact"
    if "prompt_section" in skill_spec and "code_section" in skill_spec:
        return "hybrid"
    return "prompt"

def load_skill(self, skill_name: str) -> Dict:
    """Load skill with format detection."""
    skill_spec = self._load_skill_spec(skill_name)
    skill_spec["_detected_format"] = self._detect_skill_format(skill_spec)
    return skill_spec
```

### Acceptance Criteria
- [ ] CodeAct schema documented with example
- [ ] `SafetyGates` class validates commands
- [ ] `CodeActExecutor` handles pre/main/post actions
- [ ] Conditional branching works
- [ ] Shell commands respect safety gates
- [ ] LLM generation integrated via callback
- [ ] Skills loader detects CodeAct format

---

## Ticket 3.3: Dashboard Extension for Sprint 3

**Priority**: P2 | **Estimate**: 2h | **Owner**: 0102

### Problem
No visibility into ToT selection effectiveness or CodeAct execution patterns.

### Implementation

Extend `get_telemetry_dashboard()` in PatternMemory:

```python
# Sprint 3: ToT and CodeAct metrics
tot_selections = counters.get("tot_selections", 0)
tot_high_confidence = counters.get("tot_high_confidence", 0)
tot_confidence_rate = tot_high_confidence / max(tot_selections, 1)

codeact_executions = counters.get("codeact_executions", 0)
codeact_gate_triggers = counters.get("codeact_gate_triggers", 0)

return {
    # Sprint 1
    "retry_count": counters.get("react_retry_count", 0),
    "total_executions": counters.get("total_executions", 0),
    "variation_win_rate": round(win_rate, 3),
    "avg_fidelity_delta": round(avg_delta, 3),
    "variations_tested": total_tested,
    "variations_promoted": promoted,

    # Sprint 2
    "retrieval_coverage": round(retrieval_coverage, 3),
    "avg_retrieval_relevance": round(row['avg_relevance'] or 0, 3),
    "total_retrievals": retrieval_total,
    "skill_edges": edge_count,
    "connected_skills": connected_skills,

    # Sprint 3
    "tot_selections": tot_selections,
    "tot_confidence_rate": round(tot_confidence_rate, 3),
    "codeact_executions": codeact_executions,
    "codeact_gate_triggers": codeact_gate_triggers
}
```

### Acceptance Criteria
- [ ] Dashboard includes `tot_selections`, `tot_confidence_rate`
- [ ] Dashboard includes `codeact_executions`, `codeact_gate_triggers`

---

## Sprint 3 Execution Order

```
3.1.1 → 3.1.2 → 3.2.1 → 3.2.2 → 3.1.3 → 3.2.3 → 3.3
  ↓       ↓       ↓       ↓       ↓       ↓       ↓
scoring selector schema  executor wiring  loader  dash
methods  module  docs    module   ToT    detect  extend
```

**Rationale**: Scoring methods first (PatternMemory dependency), then SkillSelector, then CodeAct in parallel, then wiring and dashboard.

---

## Validation Plan

### Unit Tests
```python
# test_skill_selector.py
def test_rank_skills_by_fidelity():
    """Verify fidelity-based ranking."""

def test_context_match_scoring():
    """Verify context keywords boost score."""

def test_cold_start_handling():
    """Verify new skills get default score."""

# test_codeact_executor.py
def test_shell_action_execution():
    """Verify shell commands run."""

def test_safety_gates_block():
    """Verify blocked patterns are enforced."""

def test_conditional_branching():
    """Verify if/then/else works."""

def test_llm_callback_integration():
    """Verify LLM generation works."""
```

### Integration Test
```bash
WRE_TOT_SELECTION=1 python -c "
from modules.infrastructure.wre_core.wre_master_orchestrator import WREMasterOrchestrator
m = WREMasterOrchestrator()
skill, meta = m.select_skill_tot(['qwen_gitpush', 'qwen_gitdiff'], {'intent': 'push'})
print(f'Selected: {skill}, ToT meta: {meta}')
"
```

---

## Success Metrics (CTO Gate)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| ToT selection accuracy | N/A | 80% | Best skill chosen vs manual |
| ToT confidence rate | N/A | 70% | High-confidence selections |
| CodeAct adoption | 0% | 20% | High-impact skills using CodeAct |
| Gate trigger rate | N/A | <5% | Safety gates blocking valid commands |

---

*Created: 2026-02-24 | Sprint 3 of WRE CoT Closure*
