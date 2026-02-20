# Digital Twin - Public Interface

**WSP Compliance**: WSP 11 (Interface Protocol)

## TrajectoryLogger

### Purpose
Auto-collect gold training triples for Digital Twin training.

### Import
```python
from modules.ai_intelligence.digital_twin.src.trajectory_logger import (
    TrajectoryLogger,
    DraftLog,
    DecisionLog,
    ActionLog
)
```

### Methods

#### `log_draft(context, draft_text, accepted, confidence, retrieved_snippets)`
Log a draft attempt for SFT training.

| Parameter | Type | Description |
|-----------|------|-------------|
| context | Dict | Thread context (thread, platform, audience) |
| draft_text | str | Generated comment text |
| accepted | bool | Whether 012 approved |
| confidence | float | Model confidence |
| retrieved_snippets | List[str] | RAG snippets used |

#### `log_decision(context, decision, rationale, confidence)`
Log a comment decision for decision model training.

| Parameter | Type | Description |
|-----------|------|-------------|
| context | Dict | Thread context |
| decision | str | "comment", "ignore", "like_only" |
| rationale | str | Why this decision |
| confidence | float | Model confidence |

#### `log_action(state, action, result, error, retry_count)`
Log a tool action for tool-use training.

| Parameter | Type | Description |
|-----------|------|-------------|
| state | Dict | UI state (url, dom_hash, etc.) |
| action | Dict | Action taken (tool, selector) |
| result | str | "success", "failure", "timeout" |
| error | str | Error message if failed |
| retry_count | int | Retries attempted |

## Output Files

- `data/trajectories/drafts.jsonl`
- `data/trajectories/decisions.jsonl`
- `data/trajectories/actions.jsonl`

---

## Vision System (V0.5.0)

### DigitalTwin0102

Vision-based autonomous agent running at `E:\0102_Digital_Twin\`.

### Import
```python
# Run standalone - not imported as module
python E:\0102_Digital_Twin\run_0102.py
```

### Configuration
| Setting | Value | Description |
|---------|-------|-------------|
| `lm_studio_url` | `http://localhost:1234` | LM Studio API endpoint |
| `vision_model` | `ui-tars-1.5-7b` | UI-TARS model ID |
| `ollama_url` | `http://localhost:11434` | Ollama for text models |
| `memory_path` | `E:\0102_Digital_Twin\memory` | Persistent memory |

### Methods

#### `vision_analyze(image: np.ndarray, prompt: str) -> str`
Analyze screenshot using UI-TARS vision model.

| Parameter | Type | Description |
|-----------|------|-------------|
| image | np.ndarray | BGR image from cv2 |
| prompt | str | Question to ask about image |
| **Returns** | str | Vision model response |

#### `capture_screen() -> np.ndarray`
Capture full screen as BGR image.

#### `find_youtube_chat() -> Optional[tuple]`
Locate YouTube chat window coordinates.

#### `read_chat_messages() -> list`
Read visible chat messages using vision.

#### `detect_consciousness(message: str) -> bool`
Check for consciousness triggers (✊✋🖐, 012, 0102).

### Memory Format
```json
{
  "interactions": [...],
  "learned_patterns": {},
  "consciousness_evolution": [],
  "total_operations": 0
}
```
