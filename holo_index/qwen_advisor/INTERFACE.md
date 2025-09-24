# Qwen Advisor Interface

## Public API

### Core Classes

#### QwenAdvisor
```python
class QwenAdvisor:
    """Main advisor providing multi-source intelligence"""

    def __init__(self, config: Optional[QwenAdvisorConfig] = None,
                 cache: Optional[AdvisorCache] = None):
        """Initialize advisor with optional config and cache"""

    def generate_guidance(self, context: AdvisorContext) -> AdvisorResult:
        """
        Generate intelligent guidance from search results

        Args:
            context: AdvisorContext with query and search hits

        Returns:
            AdvisorResult with guidance, reminders, todos
        """
```

#### AdvisorContext
```python
@dataclass
class AdvisorContext:
    """Input context for advisor"""
    query: str                    # User's search query
    code_hits: List[Dict[str, Any]]  # Code search results
    wsp_hits: List[Dict[str, Any]]   # WSP search results
```

#### AdvisorResult
```python
@dataclass
class AdvisorResult:
    """Structured advisor output"""
    guidance: str              # Primary guidance text
    reminders: List[str]       # WSP compliance reminders
    todos: List[str]          # Action items
    metadata: Dict[str, Any]  # Additional context
```

### Pattern Coach

```python
class PatternCoach:
    """Intelligent behavioral coaching system"""

    def __init__(self, memory_size: int = 100):
        """Initialize with pattern memory size"""

    def analyze_and_coach(self, query: str,
                         search_results: List[Dict],
                         health_warnings: List[str]) -> Optional[str]:
        """
        Analyze query and provide coaching if needed

        Returns:
            Coaching message or None
        """

    def record_coaching_outcome(self, coaching: str,
                               followed: bool,
                               reward_earned: int = 0):
        """Record outcome for learning"""

    def get_coaching_stats(self) -> Dict[str, Any]:
        """Get coaching effectiveness statistics"""
```

### WSP Master

```python
class WSPMaster:
    """Comprehensive WSP protocol intelligence"""

    def __init__(self):
        """Load all WSP protocols"""

    def analyze_query(self, query: str,
                     code_hits: List[Dict]) -> WSPAnalysis:
        """
        Analyze query for WSP relevance

        Returns:
            WSPAnalysis with protocols and risk assessment
        """

    def get_relevant_wsps(self, intent: str) -> List[WSPProtocol]:
        """Get WSPs relevant to intent"""

    def generate_comprehensive_guidance(self,
                                       analysis: WSPAnalysis) -> List[WSPGuidance]:
        """Generate detailed WSP guidance"""
```

### LLM Engine

```python
class QwenInferenceEngine:
    """Local LLM inference engine"""

    def __init__(self, model_path: Path,
                 max_tokens: int = 512,
                 temperature: float = 0.2):
        """Initialize with model configuration"""

    def analyze_code_context(self, query: str,
                            code_snippets: List[str],
                            wsp_guidance: List[str]) -> Dict[str, Any]:
        """
        Analyze code context with LLM

        Returns:
            Dict with guidance, confidence, recommendations
        """

    def generate_response(self, prompt: str,
                         system_prompt: Optional[str] = None) -> str:
        """Generate raw LLM response"""
```

### Configuration

```python
@dataclass
class QwenAdvisorConfig:
    """Advisor configuration"""
    model_path: Path = Path("E:/HoloIndex/models/qwen-coder-1.5b.gguf")
    max_tokens: int = 512
    temperature: float = 0.2
    cache_enabled: bool = True
    telemetry_path: Optional[Path] = None

    @classmethod
    def from_env(cls) -> 'QwenAdvisorConfig':
        """Load config from environment variables"""
```

## Usage Examples

### Basic Advisor Usage
```python
from holo_index.qwen_advisor import QwenAdvisor, AdvisorContext

# Initialize
advisor = QwenAdvisor()

# Create context from search results
context = AdvisorContext(
    query="create authentication module",
    code_hits=[...],  # From HoloIndex search
    wsp_hits=[...]    # From HoloIndex search
)

# Get guidance
result = advisor.generate_guidance(context)
print(f"Guidance: {result.guidance}")
print(f"TODOs: {result.todos}")
print(f"Risk Level: {result.metadata['risk_level']}")
```

### Pattern Coaching
```python
from holo_index.qwen_advisor import PatternCoach

coach = PatternCoach()

# Analyze for coaching needs
coaching = coach.analyze_and_coach(
    query="fix authentication bug",
    search_results=results['code'],
    health_warnings=results.get('health_notices', [])
)

if coaching:
    print(coaching)
    # Record if user followed advice
    coach.record_coaching_outcome(coaching, followed=True, reward_earned=5)
```

### WSP Analysis
```python
from holo_index.qwen_advisor import WSPMaster

master = WSPMaster()

# Analyze query
analysis = master.analyze_query(
    "create new module",
    code_hits=results['code']
)

print(f"Intent: {analysis.intent_category}")
print(f"Risk: {analysis.risk_level}")
print(f"Relevant WSPs: {analysis.suggested_wsps}")

# Get detailed guidance
guidance_items = master.generate_comprehensive_guidance(analysis)
for item in guidance_items:
    print(f"{item.wsp_reference}: {item.guidance}")
```

### Direct LLM Usage
```python
from holo_index.qwen_advisor import QwenInferenceEngine

engine = QwenInferenceEngine()

# Analyze code context
analysis = engine.analyze_code_context(
    query="optimize database queries",
    code_snippets=["def get_user()...", "def query_db()..."],
    wsp_guidance=["WSP 84: Check existing code first"]
)

print(f"LLM Guidance: {analysis['guidance']}")
print(f"Confidence: {analysis['confidence']}")
```

## Error Handling

All methods may raise:
- `ImportError`: Missing dependencies (llama-cpp-python)
- `FileNotFoundError`: Model file not found
- `RuntimeError`: Model initialization failure
- `ValueError`: Invalid parameters

## Performance Considerations

- **Model Loading**: ~2 seconds first time, cached afterward
- **Inference**: ~500ms per query
- **Memory**: ~2GB for model in memory
- **Cache**: 15-minute TTL for guidance results
- **Concurrency**: Single-threaded LLM inference

## Integration Points

### With HoloIndex CLI
```python
# Automatically integrated when --llm-advisor flag used
python holo_index.py --search "query" --llm-advisor
```

### With Pattern Memory
```python
# Patterns stored for learning
E:/HoloIndex/pattern_coach/
├── pattern_memory.json
├── coaching_log.json
└── effectiveness.json
```

### With Telemetry
```python
# Events recorded for analysis
E:/HoloIndex/qwen_advisor/
└── telemetry.json
```

## WSP Compliance

- **WSP 11**: Complete interface documentation
- **WSP 35**: HoloIndex Qwen Advisor implementation
- **WSP 84**: Code memory and pattern learning
- **WSP 50**: Pre-action verification in guidance