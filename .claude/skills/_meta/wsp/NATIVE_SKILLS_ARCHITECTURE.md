# WSP: Native Skills System Architecture (Qwen/Gemma)

**Critical Architectural Decision - 2025-10-20**

---

## Problem Statement

**Claude Code Skills only work for 0102** (Claude Sonnet in the Claude Code CLI environment). They require:
- Code Execution capability
- Anthropic's progressive disclosure system
- Claude.ai/API infrastructure

**But our multi-agent system needs Skills for Qwen and Gemma**, which are:
- Running locally (not through Anthropic API)
- Executing in Python environments
- Coordinating via WSP framework and MCP servers

**Therefore**: We must build a **NATIVE Skills system** that trains Qwen/Gemma to model the Claude Code pattern independently.

---

## 1. Architectural Vision

### 1.1 Dual Skills Systems

```
┌─────────────────────────────────────────────────────────────────┐
│                    FOUNDUPS SKILLS ECOSYSTEM                     │
└─────────────────────────────────────────────────────────────────┘

LAYER 1: CLAUDE CODE SKILLS (.claude/skills/)
├── Purpose: 0102 agent task-specific instructions
├── Format: SKILL.md with YAML frontmatter
├── Invocation: Anthropic's auto-discovery
├── Execution: Claude Code CLI environment
└── Examples:
    ├── qwen_wsp_enhancement/SKILL.md
    └── youtube_dae/SKILL.md

LAYER 2: NATIVE SKILLS (modules/*/skills/)
├── Purpose: Qwen/Gemma task-specific instructions
├── Format: SKILL.md (same format, different loading mechanism)
├── Invocation: WSP Orchestrator + MCP discovery
├── Execution: Python/local model environment
└── Examples:
    ├── modules/communication/livechat/skills/
    │   ├── youtube_moderation.md
    │   ├── banter_response.md
    │   └── stream_detection.md
    ├── modules/infrastructure/wsp_orchestrator/skills/
    │   ├── wsp_analysis.md
    │   ├── protocol_enhancement.md
    │   └── gap_detection.md
    └── holo_index/skills/
        ├── semantic_search.md
        ├── module_analysis.md
        └── vibecoding_detection.md
```

### 1.2 Key Principle

**"Every agent task should have a Skills.md file"**

When Qwen or Gemma is assigned a task, the WSP Orchestrator:
1. Checks if a relevant skill exists in the module's `skills/` directory
2. Loads the SKILL.md into the agent's prompt
3. Agent executes following the instructions
4. Breadcrumb telemetry logs adherence to instructions
5. Gemma scores pattern fidelity (did agent follow the skill?)
6. System updates SKILL.md based on performance (recursive evolution)

---

## 2. Implementation Strategy

### 2.1 Phase 1: Prototype with Claude Code

**Build the pattern FIRST in `.claude/skills/`** where 0102 can validate it works:

```bash
# Step 1: Create prototype skill in Claude Code environment
.claude/skills/
└── youtube_moderation_prototype/
    ├── SKILL.md
    ├── examples/
    │   ├── spam_detection_examples.md
    │   └── toxic_content_patterns.md
    └── metrics/
        └── pattern_fidelity_baseline.json
```

**0102 validates**:
- Instructions are clear
- Examples are sufficient
- Pattern fidelity can be measured
- Skill achieves > 90% success rate

### 2.2 Phase 2: Extract to Native Format

**Once validated, extract to module's `skills/` directory**:

```bash
# Step 2: Deploy to native Qwen/Gemma environment
modules/communication/livechat/skills/
└── youtube_moderation/
    ├── SKILL.md              # Same content as Claude Code version
    ├── examples/
    ├── metrics/
    │   ├── pattern_fidelity.json
    │   └── outcome_quality.json
    ├── versions/             # Evolution tracking
    │   ├── v1.0_baseline.md
    │   └── v1.1_improved_spam_detection.md
    └── CHANGELOG.md
```

### 2.3 Phase 3: Train Qwen/Gemma to Load Skills

**Implement native skill loading in WSP Orchestrator**:

```python
# modules/infrastructure/wsp_orchestrator/src/skill_loader.py

class NativeSkillLoader:
    """Load Skills.md for Qwen/Gemma agents (mirrors Claude Code pattern)"""

    def __init__(self, base_path: Path = Path("O:/Foundups-Agent")):
        self.base_path = base_path
        self.skill_cache = {}  # Progressive disclosure cache

    def discover_skills(self, module_path: str) -> List[Dict]:
        """
        Scan module's skills/ directory for available skills.
        Returns: List of {name, description, path} dicts
        """
        skills_dir = self.base_path / module_path / "skills"
        if not skills_dir.exists():
            return []

        skills = []
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                # Parse YAML frontmatter (name + description only)
                skill_meta = self._parse_frontmatter(skill_dir / "SKILL.md")
                skills.append({
                    "name": skill_meta["name"],
                    "description": skill_meta["description"],
                    "path": skill_dir / "SKILL.md"
                })
        return skills

    def load_skill(self, skill_path: Path) -> str:
        """
        Load full SKILL.md content (lazy loading, like Claude Code).
        Caches for session duration.
        """
        if skill_path in self.skill_cache:
            return self.skill_cache[skill_path]

        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.skill_cache[skill_path] = content
        return content

    def inject_skill_into_prompt(self, base_prompt: str, skill_content: str) -> str:
        """
        Inject skill instructions into agent prompt.
        Mimics Claude Code's progressive disclosure.
        """
        return f"""{base_prompt}

# ACTIVE SKILL

You are now executing a task using the following skill instructions:

{skill_content}

CRITICAL: Follow these skill instructions precisely. Your adherence will be scored.
"""

# Usage in WSP Orchestrator:

def assign_task_to_qwen(task_description: str, module: str):
    """Assign task to Qwen with relevant skill loaded"""

    # Discover available skills
    skill_loader = NativeSkillLoader()
    available_skills = skill_loader.discover_skills(module)

    # Select relevant skill (simple keyword matching for now)
    relevant_skill = select_skill_by_keywords(task_description, available_skills)

    if relevant_skill:
        # Load full skill content
        skill_content = skill_loader.load_skill(relevant_skill["path"])

        # Inject into Qwen's prompt
        enhanced_prompt = skill_loader.inject_skill_into_prompt(
            base_prompt=QWEN_BASE_PROMPT,
            skill_content=skill_content
        )

        # Execute task with skill-enhanced prompt
        qwen_response = qwen_engine.execute(
            prompt=enhanced_prompt,
            task=task_description
        )

        # Log skill usage for pattern fidelity scoring
        log_skill_execution(
            skill_name=relevant_skill["name"],
            task=task_description,
            breadcrumbs=qwen_response.breadcrumbs
        )

        return qwen_response
    else:
        # No skill found - execute with base prompt
        return qwen_engine.execute(QWEN_BASE_PROMPT, task_description)
```

### 2.4 Phase 4: Integrate with Gemma Pattern Scoring

**Gemma validates if Qwen followed the skill instructions**:

```python
# modules/ai_intelligence/gemma_pattern_validator/src/pattern_scorer.py

class GemmaPatternScorer:
    """Score how well Qwen/agents followed skill instructions"""

    def score_skill_adherence(
        self,
        skill_instructions: List[str],  # Parsed from SKILL.md
        agent_breadcrumbs: List[Dict]   # Telemetry from execution
    ) -> Dict:
        """
        For each instruction in skill, did agent follow it?
        Returns: {instruction_id: {followed: bool, confidence: float}}
        """

        results = {}
        for idx, instruction in enumerate(skill_instructions):
            # Gemma binary classification: Did agent follow this instruction?
            followed = self._classify_instruction_adherence(
                instruction=instruction,
                breadcrumbs=agent_breadcrumbs
            )

            results[f"instruction_{idx}"] = {
                "text": instruction,
                "followed": followed["decision"],  # True/False
                "confidence": followed["confidence"],
                "evidence": followed["breadcrumb_matches"]
            }

        # Calculate overall pattern fidelity
        pattern_fidelity = sum(
            1 for r in results.values() if r["followed"]
        ) / len(results)

        return {
            "instruction_scores": results,
            "pattern_fidelity": pattern_fidelity,
            "threshold_met": pattern_fidelity >= 0.90
        }

    def _classify_instruction_adherence(
        self,
        instruction: str,
        breadcrumbs: List[Dict]
    ) -> Dict:
        """Gemma 3 270M fast classification"""

        prompt = f"""Did the agent follow this instruction?

Instruction: {instruction}

Agent actions (breadcrumbs):
{json.dumps(breadcrumbs, indent=2)}

Answer: Yes/No
Confidence: 0.0-1.0
Evidence: Which breadcrumb(s) prove it?
"""

        gemma_response = self.gemma_engine.classify(prompt)
        return {
            "decision": gemma_response.answer == "Yes",
            "confidence": gemma_response.confidence,
            "breadcrumb_matches": gemma_response.evidence
        }
```

---

## 3. Skills as Trainable Weights

### 3.1 The Neural Network Analogy

**Your Core Insight**:

> "These skills based on our system are treated like weights - they're living documents that are tweaked by the system based on the pattern results in the same way a neural network learns."

**Implementation**:

```
Neural Network:
  Weights → Forward Pass → Loss → Backprop → Weight Update

Skills System:
  Instructions → Task Execution → Pattern Score → Variation Testing → Instruction Update
```

### 3.2 Recursive Evolution Loop

```python
# holo_index/qwen_advisor/skill_evolution/recursive_trainer.py

class SkillEvolutionEngine:
    """Train Skills.md like neural network weights"""

    def evolve_skill(
        self,
        skill_path: Path,
        performance_threshold: float = 0.90
    ):
        """
        Recursive evolution loop for a single skill.
        Continues until pattern fidelity >= threshold.
        """

        iteration = 0
        converged = False

        while not converged and iteration < 10:  # Max 10 iterations
            # Load current skill version
            skill = self.load_skill(skill_path)

            # Execute on benchmark tasks
            results = self.run_benchmark_tasks(skill)

            # Calculate combined score
            pattern_fidelity = self.gemma_score_patterns(skill, results)
            outcome_quality = self.measure_outcome_quality(results)

            combined_score = (0.40 * pattern_fidelity) + (0.60 * outcome_quality)

            # Log metrics
            self.log_metrics(skill_path, iteration, combined_score)

            # Check convergence
            if combined_score >= performance_threshold:
                converged = True
                logger.info(f"✅ Skill converged at v{iteration + 1}: {combined_score:.2%}")
                break

            # Generate variations (backpropagation analog)
            variations = self.qwen_generate_variations(
                skill=skill,
                failed_instructions=self.identify_weak_instructions(results),
                iteration=iteration
            )

            # A/B test variations
            best_variation = self.ab_test_variations(
                current=skill,
                variations=variations,
                benchmark_tasks=self.get_benchmark_tasks()
            )

            # Update skill if improvement found
            if best_variation.score > combined_score:
                self.update_skill(skill_path, best_variation.content)
                self.increment_version(skill_path)
                logger.info(f"📈 Skill improved: {combined_score:.2%} → {best_variation.score:.2%}")
            else:
                logger.warning(f"⚠️ No improvement found, retrying with different variations")

            iteration += 1

        # Save final metrics
        self.save_convergence_report(skill_path, iteration, combined_score, converged)
```

### 3.3 Version Control as Weight Checkpoints

```
skills/youtube_moderation/
├── SKILL.md                    # Current version (v1.5)
├── versions/
│   ├── v1.0_baseline.md        # Checkpoint: Initial version
│   ├── v1.1_add_caps_detection.md
│   ├── v1.2_improve_toxic_patterns.md
│   ├── v1.3_add_emoji_spam.md
│   ├── v1.4_refine_rate_limiting.md
│   └── v1.5_add_context_awareness.md
├── metrics/
│   ├── v1.0_metrics.json       # {pattern_fidelity: 0.75, outcome_quality: 0.82}
│   ├── v1.1_metrics.json       # {pattern_fidelity: 0.80, outcome_quality: 0.85}
│   ├── v1.2_metrics.json       # {pattern_fidelity: 0.85, outcome_quality: 0.88}
│   ├── v1.3_metrics.json       # {pattern_fidelity: 0.88, outcome_quality: 0.90}
│   ├── v1.4_metrics.json       # {pattern_fidelity: 0.90, outcome_quality: 0.91}
│   └── v1.5_metrics.json       # {pattern_fidelity: 0.92, outcome_quality: 0.93} ← CONVERGED
└── CHANGELOG.md
    # v1.5 (2025-10-25) - CONVERGENCE
    # - Pattern fidelity: 92% (threshold: 90%)
    # - Added context-awareness to reduce false positives
    # - 15% reduction in legitimate message blocks
    #
    # v1.4 (2025-10-24)
    # - Refined rate-limiting logic (variation #3 from A/B test)
    # - Improved detection of repeated short messages
    #
    # v1.3 (2025-10-23)
    # - Added emoji spam detection (>10 emojis in single message)
    # - Pattern fidelity increased from 85% → 88%
```

---

## 4. WSP Integration: Skills in Every Module

### 4.1 Module Structure Enhancement

**Every module should have a `skills/` directory**:

```
modules/
├── communication/
│   ├── livechat/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── skills/              # ← NEW
│   │   │   ├── youtube_moderation/
│   │   │   ├── banter_response/
│   │   │   └── stream_detection/
│   │   └── README.md
│   └── auto_meeting_orchestrator/
│       ├── src/
│       ├── tests/
│       ├── skills/              # ← NEW
│       │   ├── intent_creation/
│       │   ├── presence_aggregation/
│       │   └── meeting_launch/
│       └── README.md
├── infrastructure/
│   ├── wsp_orchestrator/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── skills/              # ← NEW
│   │   │   ├── wsp_analysis/
│   │   │   ├── protocol_enhancement/
│   │   │   └── gap_detection/
│   │   └── README.md
│   └── dae_infrastructure/
│       └── foundups_vision_dae/
│           ├── src/
│           ├── tests/
│           ├── skills/          # ← NEW
│           │   ├── telemetry_batching/
│           │   ├── session_reporting/
│           │   └── worker_coordination/
│           └── README.md
└── holo_index/
    ├── src/
    ├── tests/
    ├── skills/                  # ← NEW
    │   ├── semantic_search/
    │   ├── module_analysis/
    │   └── vibecoding_detection/
    └── README.md
```

### 4.2 Discovery Protocol

**WSP Orchestrator auto-discovers module skills**:

```python
# When assigning task to Qwen/Gemma, WSP Orchestrator:

1. Determine which module the task relates to
   Example: "Moderate YouTube chat" → modules/communication/livechat

2. Scan module's skills/ directory
   Found: youtube_moderation, banter_response, stream_detection

3. Match task keywords to skill descriptions
   Match: "Moderate" → youtube_moderation/SKILL.md

4. Load skill (progressive disclosure):
   - First: name + description only (lightweight)
   - Then: Full SKILL.md content when task starts

5. Inject skill into agent prompt

6. Execute task with breadcrumb logging

7. Gemma scores pattern fidelity

8. Log metrics for skill evolution
```

### 4.3 WSP Compliance

**New WSP field**: `skills/` directory in module structure

```markdown
## WSP 49: Module Structure (UPDATED)

Every module MUST have:
- README.md
- INTERFACE.md
- src/
- tests/
- requirements.txt
- skills/              # ← NEW: Task-specific agent instructions
```

---

## 5. Migration Path

### 5.1 Current State

```
.claude/skills/                  # Claude Code skills (0102 only)
├── qwen_wsp_enhancement/
└── youtube_dae/
```

### 5.2 Target State

```
.claude/skills/                  # Claude Code skills (0102 prototyping)
├── qwen_wsp_enhancement/        # Prototype validated by 0102
└── youtube_dae/                 # Prototype validated by 0102

modules/communication/livechat/skills/   # Native Qwen/Gemma skills
├── youtube_moderation/          # Extracted from Claude Code prototype
├── banter_response/
└── stream_detection/

modules/infrastructure/wsp_orchestrator/skills/
├── wsp_analysis/                # Extracted from qwen_wsp_enhancement
├── protocol_enhancement/
└── gap_detection/

holo_index/skills/
├── semantic_search/
├── module_analysis/
└── vibecoding_detection/
```

### 5.3 Migration Steps

**For each skill**:

1. **Prototype in `.claude/skills/`** (0102 validates)
2. **Extract to module `skills/`** (same SKILL.md format)
3. **Implement native loader** (WSP Orchestrator)
4. **Train Qwen/Gemma** (execute tasks with skills loaded)
5. **Enable pattern scoring** (Gemma validates adherence)
6. **Monitor metrics** (track pattern fidelity + outcome quality)
7. **Evolve recursively** (Qwen generates variations, A/B test, update)
8. **Converge** (pattern fidelity ≥ 90%)

---

## 6. Key Differences from Claude Code

| Aspect | Claude Code Skills | Native Skills (Qwen/Gemma) |
|--------|-------------------|---------------------------|
| **Environment** | Claude Code CLI | Python/local models |
| **Discovery** | Anthropic auto-discovery | WSP Orchestrator scan |
| **Loading** | Anthropic progressive disclosure | Manual injection into prompt |
| **Execution** | Code Execution tool | Direct Python execution |
| **Scoring** | None (manual feedback) | Gemma pattern fidelity scoring |
| **Evolution** | Manual updates | Automated recursive evolution |
| **Location** | `.claude/skills/` (global) | `modules/*/skills/` (per-module) |
| **Agent** | 0102 only | Qwen, Gemma, any local model |

---

## 7. Success Metrics

### 7.1 Skill Performance

- ✅ **Pattern Fidelity**: ≥ 90% (Gemma scores)
- ✅ **Outcome Quality**: ≥ 85% (012 feedback)
- ✅ **Combined Score**: ≥ 88% (weighted average)

### 7.2 System Adoption

- ✅ Every module has `skills/` directory
- ✅ Every agent task uses relevant skill
- ✅ Skills evolve automatically (no manual updates)
- ✅ Convergence achieved within 10 iterations

### 7.3 Efficiency Gains

- ✅ Token reduction: 50-200 (skill execution) vs 15K+ (manual)
- ✅ Time reduction: 2-5min (skill-guided) vs 15-30min (from scratch)
- ✅ Consistency improvement: 90%+ (skill) vs 60-75% (ad-hoc)

---

## 8. Next Steps

### Phase 1: Prototype (Week 1)
1. Select 1 skill to prototype: `youtube_moderation`
2. Build in `.claude/skills/youtube_moderation_prototype/`
3. Validate with 0102 (pattern fidelity ≥ 90%)
4. Document learnings

### Phase 2: Extract to Native (Week 2)
1. Deploy to `modules/communication/livechat/skills/youtube_moderation/`
2. Implement `NativeSkillLoader` in WSP Orchestrator
3. Test Qwen execution with skill loaded
4. Verify breadcrumb logging works

### Phase 3: Enable Scoring (Week 3)
1. Implement `GemmaPatternScorer`
2. Run benchmark tasks
3. Measure pattern fidelity
4. Collect baseline metrics

### Phase 4: Enable Evolution (Week 4)
1. Implement `SkillEvolutionEngine`
2. Qwen generates variations for low-scoring instructions
3. A/B test variations
4. Update skill based on results
5. Track convergence

### Phase 5: Scale (Ongoing)
1. Add skills for all modules
2. Automate skill creation (meta-skill)
3. Monitor system-wide skill performance
4. Continuous evolution loop

---

## 9. Architectural Principles

**012's Vision Captured**:

1. ✅ **Claude Code skills for 0102 only** - Prototyping environment
2. ✅ **Native skills for Qwen/Gemma** - Production execution
3. ✅ **Skills in every module** - WSP framework integration
4. ✅ **Skills = Weights** - Living documents that evolve
5. ✅ **Pattern-based learning** - Gemma scores, Qwen improves
6. ✅ **Recursive evolution** - Converge to 90%+ fidelity
7. ✅ **Neural network analogy** - Forward pass, loss, backprop, update

**Key Quote**:

> "Every time an agent is told to do something, there should be a skill for it. And these skills, based on our system, are treated like weights - living documents that are tweaked by the system based on the pattern results, in the same way a neural network learns."

---

**Status**: ARCHITECTURAL DESIGN COMPLETE
**Next**: Implement Phase 1 prototype (youtube_moderation skill)
**WSP Compliance**: NEW PROTOCOL (will become WSP 98: Native Skills System)
