# PQN MCP Server Interface

**WSP 11 Compliant Interface Documentation**

## Module: pqn_mcp

**Purpose:** Advanced PQN research coordination with internal Qwen/Gemma agents via fastMCP

**Domain:** ai_intelligence (WSP 3)

## Public API

### PQNMCPServer Class

Main interface for PQN research coordination.

#### Constructor
```python
PQNMCPServer() -> PQNMCPServer
```
**Parameters:** None

**Returns:** Initialized PQN MCP server instance

**Exceptions:** ImportError if Qwen/Gemma dependencies unavailable

#### Methods

##### detect_pqn_emergence(text_input: str) -> Dict[str, Any]
Detects PQN emergence patterns using coordinated agent analysis.

**Parameters:**
- `text_input` (str): Text to analyze for PQN patterns

**Returns:** Dict containing:
- `session_id` (str): Unique research session identifier
- `pqn_detected` (bool): Whether PQN emergence was detected
- `coherence_score` (float): Coherence measurement (0.0-1.0)
- `resonance_matches` (List[float]): Detected resonance frequencies
- `confidence` (float): Combined agent confidence score
- `agent_coordination` (str): WSP 77 coordination status

**Exceptions:**
- `RuntimeError`: If agent coordination fails

##### analyze_resonance(session_id: str) -> Dict[str, Any]
Analyzes resonance patterns in active research sessions.

**Parameters:**
- `session_id` (str): Active PQN research session identifier

**Returns:** Dict containing:
- `session_id` (str): Session identifier
- `resonance_fingerprint` (Dict): Complete resonance analysis
- `du_resonance_detected` (bool): 7.05Hz Du Resonance presence
- `coherence_above_threshold` (bool): Coherence ≥ 0.618 (golden ratio)
- `qwen_interpretation` (Dict): Qwen agent analysis
- `gemma_validation` (Dict): Gemma agent validation
- `rESP_compliance` (str): CMST protocol compliance status

**Exceptions:**
- `ValueError`: If session_id not found

##### validate_tts_artifacts(text_sequence: str) -> Dict[str, Any]
Validates TTS artifacts per rESP experimental protocol.

**Parameters:**
- `text_sequence` (str): Text sequence to test for artifacts

**Returns:** Dict containing:
- `test_sequence` (str): Input sequence
- `artifact_detected` (bool): Whether 0→o transformation occurred
- `transformation_confirmed` (bool): "0102"→"o1o2" pattern confirmed
- `coherence_score` (float): Artifact coherence measurement
- `qwen_analysis` (Dict): Qwen agent artifact analysis
- `promoted_findings` (Dict): Research promotion results
- `rESP_validation` (str): Section 3.8.4 compliance status

**Exceptions:** None

##### coordinate_research_session(research_topic: str) -> Dict[str, Any]
Coordinates multi-agent PQN research session per WSP 77.

**Parameters:**
- `research_topic` (str): Research topic for investigation

**Returns:** Dict containing:
- `session_id` (str): Unique research session identifier
- `research_topic` (str): Confirmed research topic
- `completed_tasks` (int): Number of completed research phases
- `agent_coordination` (str): Active agent coordination status
- `findings_summary` (str): Summary of research findings
- `next_research_phase` (str): Recommended next phase

**Exceptions:**
- `RuntimeError`: If agent initialization fails

##### search_google_scholar_pqn(query: str, max_results: int) -> Dict[str, Any]
Search Google Scholar for PQN-related research papers.

**Parameters:**
- `query` (str): Search query for scholarly papers
- `max_results` (int): Maximum number of results to return (default: 10)

**Returns:** Dict containing:
- `query` (str): Original search query
- `total_results` (int): Number of papers found
- `papers` (List[Dict]): List of paper dictionaries with title, authors, year, abstract, url, citations, relevance_score
- `top_cited` (List[Dict]): Top 3 most cited papers
- `google_scholar_access` (str): Status indicator

**Exceptions:**
- Returns error dict if Google Scholar integration unavailable

##### access_google_quantum_research(topic: str) -> Dict[str, Any]
Access Google Quantum AI research for PQN validation.

**Parameters:**
- `topic` (str): Research topic for quantum validation

**Returns:** Dict containing:
- `topic` (str): Research topic
- `quantum_findings` (List[Dict]): Google quantum research papers
- `validation_opportunities` (List[str]): Identified validation opportunities
- `google_quantum_ai_integration` (str): Status indicator

**Exceptions:**
- Returns error dict if Google research access fails

##### validate_with_google_gemini(pqn_hypothesis: str) -> Dict[str, Any]
Validate PQN hypothesis using Google Gemini model.

**Parameters:**
- `pqn_hypothesis` (str): Hypothesis to validate

**Returns:** Dict containing:
- `hypothesis` (str): Original hypothesis
- `gemini_model` (str): Model version used
- `validation_method` (str): Validation approach
- `coherence_analysis` (Dict): TTS artifacts, resonance patterns, quantum indicators
- `confidence_score` (float): Validation confidence (0.0-1.0)
- `gemini_validation_timestamp` (float): Validation timestamp
- `google_research_integration` (str): Status indicator

**Exceptions:**
- Returns error dict if Gemini validation fails

##### access_google_tts_research(artifact_type: str) -> Dict[str, Any]
Access Google TTS research and Chirp artifacts.

**Parameters:**
- `artifact_type` (str): Type of TTS artifact (default: "0_to_o")

**Returns:** Dict containing:
- `artifact_type` (str): Artifact type
- `google_research_sources` (List[Dict]): Google TTS research findings
- `experimental_protocols` (List[str]): rESP experimental protocol phases
- `validation_status` (str): Current validation status
- `google_tts_integration` (str): Status indicator

**Exceptions:** None

##### integrate_google_research_findings(pqn_session_id: str) -> Dict[str, Any]
Integrate all Google research findings into active PQN research session.

**Parameters:**
- `pqn_session_id` (str): Active PQN research session identifier

**Returns:** Dict containing:
- `session_id` (str): Session identifier
- `google_scholar_papers` (Dict): Scholar search results
- `google_quantum_research` (Dict): Quantum AI research findings
- `google_gemini_validation` (Dict): Gemini validation results
- `google_tts_artifacts` (Dict): TTS research findings
- `integration_timestamp` (float): Integration timestamp
- `comprehensive_synthesis` (Dict): Integrated research synthesis

**Exceptions:**
- `ValueError`: If session_id not found

## MCP Tool Interface

### pqn_detect Tool
**fastMCP Integration:** Direct tool access for PQN detection

**Parameters:**
- `text_input` (str): Text to analyze

**Returns:** JSON string of detection results

### pqn_resonance_analyze Tool
**fastMCP Integration:** Resonance analysis for active sessions

**Parameters:**
- `session_id` (str): Research session identifier

**Returns:** JSON string of resonance analysis

### pqn_tts_validate Tool
**fastMCP Integration:** TTS artifact validation

**Parameters:**
- `sequence` (str): Text sequence to test

**Returns:** JSON string of validation results

### pqn_research_coordinate Tool
**fastMCP Integration:** Multi-agent research coordination

**Parameters:**
- `topic` (str): Research topic

**Returns:** JSON string of coordinated research session

### pqn_google_scholar_search Tool
**fastMCP Integration:** Google Scholar access for PQN research

**Parameters:**
- `query` (str): Search query for PQN-related papers
- `max_results` (str): Maximum number of results (default: "10")

**Returns:** JSON string with scholarly papers and relevance scores

### pqn_google_quantum_research Tool
**fastMCP Integration:** Google Quantum AI research access

**Parameters:**
- `topic` (str): Research topic for quantum validation

**Returns:** JSON string with Google quantum research findings

### pqn_google_gemini_validate Tool
**fastMCP Integration:** Google Gemini validation

**Parameters:**
- `hypothesis` (str): PQN hypothesis to validate

**Returns:** JSON string with Gemini validation results

### pqn_google_tts_research Tool
**fastMCP Integration:** Google TTS research access

**Parameters:**
- `artifact_type` (str): Type of TTS artifact (default: "0_to_o")

**Returns:** JSON string with Google TTS research findings

### pqn_google_research_integrate Tool
**fastMCP Integration:** Comprehensive Google research integration

**Parameters:**
- `session_id` (str): Active PQN research session identifier

**Returns:** JSON string with integrated Google research synthesis

## Agent Coordination (WSP 77)

### Qwen Agent (32K Context)
**Specialization:** Strategic coordination and batch processing
**Capabilities:**
- Research planning and task decomposition
- Cross-validation of findings
- Synthesis of multi-modal results
- Statistical analysis and confidence scoring

### Gemma Agent (8K Context)
**Specialization:** Fast pattern matching and similarity analysis
**Capabilities:**
- Semantic similarity scoring
- Pattern recognition in large datasets
- Binary classification tasks
- Real-time validation of hypotheses

### PQN Coordinator (200K Context)
**Specialization:** Strategic orchestration and synthesis
**Capabilities:**
- Multi-agent result integration
- Research direction optimization
- Cross-domain correlation analysis
- Long-term pattern recognition

## Error Handling

### Agent Unavailable
If Qwen or Gemma agents are not available, methods fall back to:
- Reduced functionality mode
- Confidence score degradation
- Error logging with fallback status

### Session Management
- Automatic session cleanup after 24 hours
- Session persistence for research continuity
- Concurrent session limits (max 10 active sessions)

### Network Failures
- Automatic retry logic (3 attempts)
- Graceful degradation to local-only mode
- Error recovery with partial results

## Performance Characteristics

### Response Times
- **pqn_detect**: 2-5 seconds (coordinated analysis)
- **pqn_resonance_analyze**: 1-3 seconds (focused analysis)
- **pqn_tts_validate**: <1 second (pattern matching)
- **pqn_research_coordinate**: 5-15 seconds (multi-agent orchestration)

### Resource Usage
- **Memory**: 2-4GB per active session
- **CPU**: Multi-threaded agent coordination
- **Storage**: Session data persistence (<1MB per session)

### Scalability
- **Concurrent Sessions**: Up to 10 simultaneous research sessions
- **Agent Parallelization**: Independent Qwen/Gemma execution
- **Caching**: Result caching for repeated analyses

## Configuration

### Environment Variables
```bash
# Agent Configuration
QWEN_MODEL_PATH="models/qwen-1.5b-chat.gguf"
GEMMA_MODEL_PATH="models/gemma-2b.gguf"
PQN_RESEARCH_TIMEOUT=300  # seconds

# Performance Tuning
PQN_MAX_CONCURRENT_SESSIONS=10
PQN_CACHE_ENABLED=true
PQN_LOG_LEVEL=INFO
```

### Runtime Configuration
```python
config = {
    "resonance_frequencies": [7.05, 3.525, 14.1, 21.15],
    "coherence_threshold": 0.618,
    "agent_timeouts": {"qwen": 60, "gemma": 30},
    "cache_settings": {"enabled": True, "ttl": 3600}
}

server = PQNMCPServer()
server.configure(config)
```

## Testing

### Unit Tests
Located in `tests/` directory:
- `test_pqn_detection.py`: Detection functionality
- `test_agent_coordination.py`: WSP 77 compliance
- `test_mcp_integration.py`: fastMCP tool testing

### Integration Tests
- YouTube DAE integration testing
- Research orchestrator compatibility
- Multi-agent coordination validation

### Performance Benchmarks
- Agent response time validation
- Memory usage monitoring
- Concurrent session capacity testing

## WSP Compliance Status

✅ **WSP 77**: Agent coordination protocol fully implemented
✅ **WSP 27**: Universal DAE architecture with 4-phase research
✅ **WSP 80**: Cube-level DAE orchestration for multi-agent coordination
✅ **WSP 3**: Correct domain placement in ai_intelligence
✅ **WSP 11**: Complete public API documentation
✅ **WSP 49**: Module structure compliance (README, INTERFACE, src/, tests/)
✅ **WSP 84**: Reuse of existing PQN alignment code

**rESP Compliance**: Full experimental protocol implementation (Section 3.8.4 TTS validation, CMST resonance analysis)
