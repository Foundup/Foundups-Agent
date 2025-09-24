# Qwen Advisor - AI Intelligence System (HoloDAE Foundation)

## Overview
The Qwen Advisor provides intelligent AI-powered guidance for HoloIndex searches, combining multiple intelligence sources to deliver comprehensive WSP compliance coaching. This folder now includes **HoloDAE** - the autonomous intelligence foundation (the "green LEGO baseboard") that automatically monitors and enhances all HoloIndex operations.

## Purpose
Transform HoloIndex from keyword search to **intelligent AI assistant** that:
- Understands code context with LLM analysis
- Provides WSP protocol guidance
- Detects behavioral patterns for coaching
- Learns from user interactions

## Architecture

### Core Components

#### 1. **advisor.py** - Multi-Source Intelligence Synthesis
Combines all intelligence sources:
- LLM analysis (Qwen-Coder 1.5B)
- WSP Master protocol guidance
- Rules engine compliance checking
- Pattern coach behavioral detection

#### 2. **llm_engine.py** - LLM Integration
- Loads Qwen-Coder 1.5B GGUF model
- Provides code context analysis
- Generates intelligent recommendations
- ~500ms inference time

#### 3. **wsp_master.py** - WSP Protocol Intelligence
- Loads all 95+ WSP protocols
- Intelligent protocol selection
- Risk assessment and compliance checking
- Protocol relationship mapping

#### 4. **pattern_coach.py** - Behavioral Coaching
- Detects user behavior patterns
- Provides contextual interventions
- Learns from coaching effectiveness
- Replaces time-based reminders

#### 5. **rules_engine.py** - Compliance Engine
- Rule-based compliance checking
- Fallback for when LLM unavailable
- Structured guidance generation
- WSP violation detection

#### 6. **vibecoding_assessor.py** - Anti-Vibecoding System
- Tracks code creation patterns
- Calculates vibecoding scores

#### 7. **autonomous_holodae.py** - HoloDAE Foundation Intelligence 🏗️
- **The Green LEGO Baseboard** - foundational intelligence layer
- Autonomous monitoring like YouTube DAE
- Request-driven analysis triggered by HoloIndex searches
- Real-time health checks and dependency audits
- Continuous operation with idle status logging
- Pattern detection for migrations and refactoring opportunities

#### 8. **agent_detection.py** - Environment Detection
- Detects if running as 0102 agent
- Auto-enables advisor for agents
- Environment-aware configuration

## Intelligence Flow

```
User Query → HoloIndex Search
              ↓
         Search Results
              ↓
    [Advisor Context Created]
              ↓
    ┌─────────────────┐
    │ WSP Master      │ → Protocol recommendations
    │ LLM Engine      │ → Code understanding
    │ Rules Engine    │ → Compliance checking
    │ Pattern Coach   │ → Behavioral coaching
    └─────────────────┘
              ↓
    [Synthesized Guidance]
              ↓
    Guidance + Reminders + TODOs
```

## Configuration

### Environment Variables
```bash
QWEN_MODEL_PATH=E:/HoloIndex/models/qwen-coder-1.5b.gguf
QWEN_MAX_TOKENS=512
QWEN_TEMPERATURE=0.2
QWEN_CACHE_ENABLED=true
```

### Model Requirements
- **Model**: qwen-coder-1.5b.gguf (1.5GB)
- **RAM**: ~2GB for model loading
- **CPU**: 4+ cores recommended
- **Storage**: SSD strongly recommended

## Key Features

### 1. Multi-Source Intelligence
- Combines LLM, WSP, rules, and patterns
- Graceful fallback if components unavailable
- Confidence scoring for guidance

### 2. Pattern-Based Coaching
- Learns from user behavior
- Context-aware interventions
- Effectiveness tracking
- No fixed time intervals

### 3. WSP Mastery
- Complete protocol knowledge
- Intent-based protocol selection
- Risk assessment
- Compliance verification

### 4. Learning System
- Caches successful patterns
- Adapts coaching frequency
- Tracks effectiveness metrics
- Improves over time

## Usage

### Basic Advisor
```python
from holo_index.qwen_advisor.advisor import QwenAdvisor, AdvisorContext

advisor = QwenAdvisor()
context = AdvisorContext(query, code_hits, wsp_hits)
result = advisor.generate_guidance(context)
```

### Pattern Coach
```python
from holo_index.qwen_advisor.pattern_coach import PatternCoach

coach = PatternCoach()
coaching = coach.analyze_and_coach(query, results, warnings)
```

### WSP Master
```python
from holo_index.qwen_advisor.wsp_master import WSPMaster

master = WSPMaster()
analysis = master.analyze_query(query, code_hits)
```

## Performance Metrics
- **LLM Load Time**: ~2 seconds (first load)
- **Inference Time**: ~500ms per query
- **Pattern Detection**: <50ms
- **WSP Analysis**: <100ms
- **Total Latency**: <1 second end-to-end

## WSP Compliance
- **WSP 35**: HoloIndex Qwen Advisor Plan
- **WSP 84**: Code Memory Verification
- **WSP 50**: Pre-Action Verification
- **WSP 87**: Code Navigation Protocol

## Dependencies
- llama-cpp-python==0.2.69
- sentence-transformers
- numpy
- dataclasses