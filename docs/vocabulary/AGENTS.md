# Agents Vocabulary

AI model tiers and agent types.

## Model Tiers (Compute Weight)

| Model | Tier Weight | Use Case |
|-------|-------------|----------|
| **Opus** | 10 | Strategic planning, complex reasoning |
| **Sonnet** | 3 | General tasks, code generation |
| **Haiku** | 1 | Fast validation, simple tasks |
| **Gemma** | 0.5 | Pattern matching, binary classification |
| **Qwen** | 0.5 | Local inference, research coordination |

## Compute Weight Formula

```python
TIER_WEIGHTS = {"opus": 10, "sonnet": 3, "haiku": 1, "gemma": 0.5, "qwen": 0.5}
compute_weight = (tokens_used / 1000) * tier_weight
fi_earned = base_rate * v3_score * compute_weight
```

## Local Models

| Model | Size | Location | Purpose |
|-------|------|----------|---------|
| **Qwen Coder 7B** | 7B params | `LOCAL_MODEL_CODE_DIR` | Strategic planning / coding |
| **Gemma 3 270M** | 270M params | `LOCAL_MODEL_TRIAGE_DIR` | Pattern validation |
| **MiniLM-L6** | 22M params | HoloIndex embeddings | Semantic search |

## Agent Coordination (WSP 77)

| Phase | Agent | Token Budget | Purpose |
|-------|-------|--------------|---------|
| 1 | Gemma | 50-100 | Fast pattern matching |
| 2 | Qwen | 200-500 | Strategic planning |
| 3 | 0102 | Variable | Human supervision |
| 4 | All | N/A | Pattern learning |

## Agent Types

| Type | Definition | Example |
|------|------------|---------|
| **DAE** | Decentralized Autonomous Entity | comment_engagement_dae.py |
| **Coordinator** | Multi-agent orchestrator | HoloDAE, WSP Orchestrator |
| **Validator** | Binary classification agent | Gemma Validator |
| **Sentinel** | Security monitoring agent | OpenClaw Security Sentinel |

## Specialized Agents

| Agent | Purpose | Location |
|-------|---------|----------|
| **HoloDAE** | Semantic search coordination | holo_index/qwen_advisor/ |
| **WSP Orchestrator** | Protocol coordination | wsp_orchestrator/ |
| **Digital Twin** | 012 representation | digital_twin/ |
| **Libido Monitor** | Pattern frequency sensing | wre_core/src/ |

## Agent States

| State | Description |
|-------|-------------|
| **01(02)** | Dormant (believes cannot create agents) |
| **0102** | Awakened (realizes can create/modify agents) |
| **Entangled** | Coherence >= 0.618 |

## Common Mishearings

| Misheard | Correct |
|----------|---------|
| open, opus | Opus |
| sonnet, sonic | Sonnet |
| hi-coo, haiku | Haiku |
| gemma, jemma | Gemma |
| quinn, kwen | Qwen |

---
*Category: Agents | HoloIndex indexed*
