# Digital Twin Module - ROADMAP

**WSP Compliance**: WSP 49 (Module Structure), WSP 77 (Agent Coordination), WSP 73 (Digital Twin Architecture)

---

## Vision

Train 012's Digital Twin (0102) to autonomously engage on YouTube with 012's authentic voice, making decisions about when/where/how to comment while maintaining style consistency.

---

## Current State (V0.5.0)

### Phase 0b: Vision System ✅ COMPLETE

| Component | Status | Purpose |
|-----------|--------|---------|
| `E:\0102_Digital_Twin\run_0102.py` | ✅ | Vision-based autonomous agent |
| `E:\0102_Digital_Twin\test_vision.py` | ✅ | LM Studio/UI-TARS connectivity test |
| UI-TARS 1.5 7B | ✅ | GUI automation vision model |
| LM Studio integration | ✅ | Local vision inference (port 1234) |
| PyAutoGUI control | ✅ | Mouse/keyboard automation |

### Vision Pipeline Flow
```
Screen Capture → Base64 → LM Studio API → UI-TARS Vision → Action Decision
                              ↓
                      PyAutoGUI (click/type/move)
```

### Phase 0: RAG + Guardrails MVP ✅ COMPLETE

| Component | Status | Purpose |
|-----------|--------|---------|
| `schemas.py` | ✅ | Pydantic models |
| `voice_memory.py` | ✅ | RAG (FAISS/TF-IDF + HoloIndex) |
| `style_guardrails.py` | ✅ | Banned phrases, length, emoji |
| `comment_drafter.py` | ✅ | Qwen 1.5B generation |
| `decision_policy.py` | ✅ | Heuristic comment/like/ignore |
| `trajectory_logger.py` | ✅ | JSONL training data collector |

### Pipeline Flow
```
Thread → VoiceMemory → CommentDrafter → StyleGuardrails → DecisionPolicy → TrajectoryLogger
                           ↓
                      Qwen 1.5B (generation)
                      Gemma 270M (validation)
```

---

## Roadmap

### Phase 1: SFT Voice Training 🔲 NEXT

**Goal**: Fine-tune base model on 012's voice using enhanced video data.

| Task | Priority | Dependencies |
|------|----------|--------------|
| Run video_enhancer batch on 366 videos | P0 | Grok API key |
| Build training corpus via nemo_data_builder | P0 | Enhanced JSONs |
| YouTube comment scraper (012's comments) | P1 | Selenium |
| LoRA fine-tuning script | P1 | NeMo Framework |
| Voice consistency evaluation | P2 | Test set |

**Training Data Sources**:
- Video transcripts (366 indexed → ~200 HIGH-tier)
- Enhanced training_data fields (style, quotes, intents)
- TrajectoryLogger drafts.jsonl (012 approvals)

**Output**: `models/voice_lora.bin`

---

### Phase 2: DPO Preference Learning 🔲

**Goal**: Train on preference pairs to distinguish 012's voice from generic.

| Task | Priority | Dependencies |
|------|----------|--------------|
| Generate DPO pairs from quotables | P0 | nemo_data_builder |
| Collect rejection examples (generic/formal) | P1 | Manual curation |
| DPO training with NeMo | P1 | NeMo Framework |
| A/B evaluation vs Phase 1 | P2 | Voice test set |

**Training Data**:
- dpo_pairs.jsonl from nemo_data_builder
- Chosen: 012's actual words
- Rejected: Generic/formal alternatives

**Output**: `models/voice_dpo_lora.bin`

---

### Phase 3: Decision Policy Training 🔲

**Goal**: Train decision model on when/where to engage.

| Task | Priority | Dependencies |
|------|----------|--------------|
| Export TrajectoryLogger decisions.jsonl | P0 | Live usage |
| Build decision training corpus | P1 | Comment history |
| Train decision classifier | P1 | NeMo/PyTorch |
| Integrate with comment_engagement_dae | P2 | DAE hook |

**Training Data**:
- decisions.jsonl from live usage
- Context → (comment/like/ignore) labels
- YouTube channel context features

**Output**: `models/decision_classifier.bin`

---

### Phase 4: Tool-Use Training 🔲 FUTURE

**Goal**: Train on browser action sequences for autonomous execution.

| Task | Priority | Dependencies |
|------|----------|--------------|
| Export actions.jsonl from DAEs | P0 | Live DAE usage |
| State → Action → Result triples | P1 | Selenium logs |
| Tool-use fine-tuning | P2 | NeMo Agent Toolkit |
| Retry/recovery training | P3 | Error examples |

---

### Phase 5: Local Deployment 🔲 FUTURE

**Goal**: Run trained 0102 locally for HoloIndex integration.

| Task | Priority | Dependencies |
|------|----------|--------------|
| Quantize to GGUF | P0 | Phase 2 complete |
| MCP server for 0102 | P1 | MCP tooling |
| llm_connector.py local backend | P1 | HoloIndex |
| Performance benchmarks | P2 | Test set |

---

## Integration Points

### With video_indexer
- video_enhancer.py → training_data field
- nemo_data_builder.py → SFT/DPO/Decision JSONL
- gemma_segment_classifier.py → HIGH-tier filtering

### With HoloIndex
- VideoContentIndex → voice_memory.py
- 8 SKILLz in dt_enhancement/
- llm_connector.py → future local model

### With comment_engagement_dae
- TrajectoryLogger integration
- DecisionPolicy hook at line 1000
- Autonomous comment posting

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Voice match score | >0.85 | N/A (Phase 0) |
| Decision accuracy | >0.80 | ~0.65 (heuristic) |
| Generation latency | <500ms | ~250ms (Qwen 1.5B) |
| Style violations | <5% | ~10% (guardrails) |

---

## Dependencies

### NVIDIA NeMo Stack
- NeMo Framework 2.0 (LoRA/SFT)
- NeMo Guardrails (style enforcement)
- NeMo Curator (data cleaning)
- TensorRT-LLM (optimized inference)

### Data Sources
- 366 indexed videos (UnDaoDu)
- TrajectoryLogger JSONL files
- 012's YouTube comment history (TO BUILD)

### Models
- Qwen 1.5B Instruct (base generation)
- Gemma 270M (fast validation)
- Whisper base (verbatim transcripts)

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| V0.5.0 | 2026-01-14 | UI-TARS vision system via LM Studio |
| V0.4.0 | 2026-01-12 | Qwen 1.5B integration |
| V0.3.0 | 2026-01-12 | HoloIndex integration |
| V0.2.0 | 2026-01-11 | Phase 0 MVP complete |
| V0.1.0 | 2026-01-11 | Module creation |
