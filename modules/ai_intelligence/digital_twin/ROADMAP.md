# Digital Twin Module - ROADMAP

**WSP Compliance**: WSP 49 (Module Structure), WSP 77 (Agent Coordination), WSP 73 (Digital Twin Architecture)

---

## Vision

Train 012's Digital Twin (0102) to autonomously engage across social platforms with 012's authentic voice, using 20 years of 012 video corpus to drive comment drafting, decisioning, and scheduling. Current POC focus: LinkedIn comment processing and scheduling with 012 studio comment style.

---

## Current State (V0.5.2) - Audited 2026-01-21

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

### POC Focus (Active)
- LinkedIn comment drafting with platform="linkedin"
- 012 studio comment style alignment via guardrails + voice memory
- Scheduling handoff to LinkedIn orchestration layer
- Concatenate Digital Twin into YouTube live chat + Studio comments (BanterEngine fallback only)
- Index utility routing (012 voice vs music/video → RavingANTIFA/faceless pipeline)

---

## Roadmap

### Phase 1: SFT Voice Training 🔄 IN PROGRESS

**Goal**: Fine-tune base model on 012's voice using enhanced video data and studio comment samples.

#### 1.1 Video Enhancement Batch (P0) ✅ COMPLETE

| Metric | Value | Status |
|--------|-------|--------|
| Total UnDaoDu videos indexed | 454 | ✅ |
| Videos enhanced (training_data) | 454 | ✅ 100% |
| Batch script completed | 13 batches | ✅ |
| Remaining to enhance | 0 | ✅ |
| Success rate | 100% | 0 failures |

**WSP 15 Quality Tier Distribution** (final):
| Tier | Percentage | Meaning |
|------|------------|---------|
| Tier 2 (HIGH) | ~65% | Training-worthy |
| Tier 1 (MED) | ~35% | Usable |
| Tier 0 (LOW) | 0% | None skipped |

**Menu access**: `main.py` → YouTube DAEs → Indexing → Option 5 (Enhance)

#### 1.2 Training Corpus (P0) ✅ FOUNDATION BUILT

| File | Entries | Size | Status |
|------|---------|------|--------|
| `training_data/voice_sft.jsonl` | 119 | 51.5 KB | ✅ |
| `training_data/decision_sft.jsonl` | 161 | - | ✅ |
| `training_data/dpo_pairs.jsonl` | 88 | - | ✅ |

**To rebuild with more data**: `python -m modules.ai_intelligence.video_indexer.src.nemo_data_builder`

#### 1.3 LoRA Training (P1) 🔲 NOT STARTED

| Task | Status | Notes |
|------|--------|-------|
| Qwen 2.5 1.5B model | ✅ | Verified at `E:\HuggingFace\models--Qwen--Qwen2.5-1.5B-Instruct\` |
| lora_trainer.py | ✅ | Exists at `digital_twin/src/lora_trainer.py` |
| Run training | 🔲 | Awaiting more enhanced data |
| Validate output | 🔲 | - |

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

| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| Videos enhanced | 454 | 454 (100%) | ✅ Phase 1.1 COMPLETE |
| Quality Tier 2 rate | >70% | ~65% | Near target |
| Training corpus entries | 500+ | 368 | Needs rebuild with full data |
| Voice match score | >0.85 | N/A | Awaiting Phase 1.3 |
| Decision accuracy | >0.80 | ~0.65 | Heuristic baseline |
| Generation latency | <500ms | ~250ms | Qwen 1.5B ✅ |
| Style violations | <5% | ~10% | Guardrails tuning needed |

---

## Dependencies

### NVIDIA NeMo Stack
- NeMo Framework 2.0 (LoRA/SFT)
- NeMo Guardrails (style enforcement)
- NeMo Curator (data cleaning)
- TensorRT-LLM (optimized inference)

### Data Sources
- 20 years of 012 video corpus (current index: 454 UnDaoDu videos)
- 454 enhanced with training_data (100%) ✅
- TrajectoryLogger JSONL files
- 012's YouTube comment history (TO BUILD)

### Voice Cloning (Phase 6) - Status: 🔲 NOT STARTED

| Task | Status | Notes |
|------|--------|-------|
| Extract audio from indexed videos | 🔲 | 0 audio files extracted |
| Separate vocals (UVR) | 🔲 | - |
| Create 20+ min clean dataset | 🔲 | - |
| Install RVC v2 WebUI | 🔲 | - |
| Train 012 voice model | 🔲 | - |
| Integrate with Digital Twin | 🔲 | - |

### Models
- Qwen 1.5B Instruct (base generation)
- Gemma 270M (fast validation)
- Whisper base (verbatim transcripts)

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| V0.5.3 | 2026-01-22 | Phase 1.1 COMPLETE: All 454 videos enhanced (100%), menu integration added |
| V0.5.2 | 2026-01-21 | First-principles audit: 454 videos indexed, 132 enhanced (29%), training corpus built |
| V0.5.1 | 2026-01-20 | LinkedIn Digital Twin POC alignment |
| V0.5.0 | 2026-01-14 | UI-TARS vision system via LM Studio |
| V0.4.0 | 2026-01-12 | Qwen 1.5B integration |
| V0.3.0 | 2026-01-12 | HoloIndex integration |
| V0.2.0 | 2026-01-11 | Phase 0 MVP complete |
| V0.1.0 | 2026-01-11 | Module creation |
