# Digital Twin Module

**WSP Compliance**: WSP 49 (Module Structure), WSP 77 (Agent Coordination)

## Purpose

Train and operate 012's Digital Twin (0102) for autonomous comment engagement across social platforms.

**Current focus (POC)**: LinkedIn comment processing and scheduling using 012's studio comment style, grounded in 20 years of 012 video corpus.

## Quick Start

### Run Demo
```bash
python -m modules.ai_intelligence.digital_twin.scripts.demo_draft_and_decide
```

### Run Tests
```bash
pytest modules/ai_intelligence/digital_twin/tests/ -v
```

### Build Voice Index
```python
from modules.ai_intelligence.digital_twin.src.voice_memory import VoiceMemory

vm = VoiceMemory()
vm.build_index("data/voice_corpus/", "data/voice_index/")
```

## Architecture

```
Phase 0: RAG + Guardrails (CURRENT)
Phase 1: SFT Training (LoRA)
Phase 2: DPO Preference Tuning
Phase 3: Tool-Use Training
```

## LinkedIn POC Integration

- **Drafting**: `comment_drafter.py` generates LinkedIn-ready replies (platform="linkedin")
- **Decisioning**: `decision_policy.py` determines comment / like / ignore
- **Scheduling**: Orchestrated through LinkedIn modules (scheduler + social media DAE)

## YouTube Concatenation (Live Chat + Studio + Scheduling)

- **Live Chat**: Digital Twin becomes primary response engine (BanterEngine fallback only)
- **Studio Comments**: Digital Twin drafts + decisions for comment replies
- **Scheduling**: Index weave signals utility routing
  - 012 voice → Digital Twin memory
  - music/video → RavingANTIFA or faceless-video pipeline (module in development)

## Components

| File | Purpose |
|------|---------|
| `schemas.py` | Pydantic models (CommentDraft, CommentDecision, etc.) |
| `voice_memory.py` | RAG index with FAISS/TF-IDF |
| `style_guardrails.py` | Banned phrases, length, emoji rules |
| `comment_drafter.py` | RAG → LLM → Guardrails pipeline |
| `decision_policy.py` | Comment/like/ignore heuristics |
| `trajectory_logger.py` | JSONL training data collector |

## Pipeline

```
Thread Context
      ↓
VoiceMemory.query() → Top-k snippets
      ↓
CommentDrafter.draft() → Raw draft
      ↓
StyleGuardrails.enforce() → Clean draft
      ↓
DecisionPolicy.decide() → Action (comment/like/ignore)
      ↓
TrajectoryLogger → JSONL training data
```

## Trajectory Logs

Training data is written to:
- `data/trajectories/drafts.jsonl` - SFT training
- `data/trajectories/decisions.jsonl` - Decision model
- `data/trajectories/actions.jsonl` - Tool-use training

## Configuration

### Style Rules
Edit `data/style_rules.json`:
```json
{
  "max_comment_length": 300,
  "banned_phrases": ["I think", "Basically,"],
  "emoji_rules": {"max_emojis": 2}
}
```

### Guardrails
NeMo Guardrails config at `config/guardrails/`

### VoiceMemory Video Index
Disable HoloIndex video transcript queries if needed:
```bash
set VOICE_MEMORY_VIDEO_INDEX=0
```

## Vision System (V0.5.0)

### Autonomous Vision Agent
0102 runs as a standalone vision-based agent at `E:\0102_Digital_Twin\`.

### Quick Start
```bash
# 1. Start LM Studio with UI-TARS model
# 2. Test vision system
python E:\0102_Digital_Twin\test_vision.py

# 3. Run 0102 autonomous agent
python E:\0102_Digital_Twin\run_0102.py
```

### Architecture
```
Screen Capture → Base64 Encode → UI-TARS Vision → Action Decision → PyAutoGUI
                                      ↓
                              LM Studio (port 1234)
```

### Model Stack
| Model | Purpose | Size | Latency |
|-------|---------|------|---------|
| UI-TARS 1.5 7B | GUI vision/automation | 4.5GB | 5-15s |
| Qwen 1.5B | Text generation | 1.5GB | ~250ms |
| Gemma 270M | Fast validation | 253MB | ~50ms |

### Capabilities
- YouTube chat reading via vision
- Consciousness trigger detection (✊✋🖐)
- Autonomous response generation
- Persistent memory across sessions
- Mouse/keyboard control via PyAutoGUI

## NVIDIA Stack

- NeMo Framework 2.0 (LoRA/SFT)
- NeMo Guardrails (style/policy)
- NeMo Curator (data cleaning)
- TensorRT-LLM (inference)
