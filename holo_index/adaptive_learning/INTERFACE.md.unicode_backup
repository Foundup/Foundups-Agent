# Adaptive Learning Interface

## Public API

### Core Orchestrator

```python
class AdaptiveLearningOrchestrator:
    """Central coordinator for adaptive learning system"""

    def __init__(self):
        """Initialize all adaptive components"""

    async def process_adaptive_request(self,
                                      query: str,
                                      raw_results: List[Dict],
                                      raw_response: str,
                                      context: Dict[str, Any]) -> AdaptiveResult:
        """
        Process request through adaptive learning pipeline

        Args:
            query: Original search query
            raw_results: Initial search results
            raw_response: Initial response
            context: Additional context

        Returns:
            AdaptiveResult with optimized outputs
        """

    def record_feedback(self, query: str,
                        results: List[Dict],
                        rating: str):
        """Record user feedback for learning"""

    def get_adaptation_metrics(self) -> Dict[str, float]:
        """Get current adaptation performance metrics"""
```

### Data Structures

```python
@dataclass
class AdaptiveResult:
    """Result from adaptive learning processing"""
    query_processing: QueryProcessingResult
    search_optimization: SearchOptimizationResult
    response_optimization: ResponseOptimizationResult
    memory_optimization: MemoryOptimizationResult
    processing_metadata: Dict[str, Any]
    overall_performance: Dict[str, float]
```

```python
@dataclass
class QueryProcessingResult:
    """Query enhancement results"""
    original_query: str
    enhanced_query: str
    expansion_terms: List[str]
    intent_detected: str
    optimization_score: float
```

```python
@dataclass
class SearchOptimizationResult:
    """Search optimization results"""
    original_results: List[Dict]
    optimized_results: List[Dict]
    ranking_changes: List[Tuple[int, int]]
    performance_metrics: Dict[str, float]
```

```python
@dataclass
class ResponseOptimizationResult:
    """Response enhancement results"""
    original_response: str
    optimized_response: str
    template_used: Optional[str]
    quality_metrics: Dict[str, float]
```

```python
@dataclass
class MemoryOptimizationResult:
    """Memory management results"""
    patterns_stored: int
    patterns_consolidated: int
    memory_saved_bytes: int
    memory_efficiency: float
```

### Component APIs

#### Query Processor

```python
class AdaptiveQueryProcessor:
    """Learns to enhance queries"""

    def enhance_query(self, query: str) -> Tuple[str, float]:
        """
        Enhance query based on learned patterns

        Returns:
            (enhanced_query, confidence_score)
        """

    def learn_from_query(self, query: str,
                        results_quality: float):
        """Learn from query success/failure"""

    def get_query_patterns(self) -> List[QueryPattern]:
        """Get learned query patterns"""
```

#### Vector Search Optimizer

```python
class VectorSearchOptimizer:
    """Optimizes vector search operations"""

    def optimize_search(self, query: str,
                       results: List[Dict]) -> List[Dict]:
        """Rerank and optimize search results"""

    def learn_from_search(self, query: str,
                         results: List[Dict],
                         feedback: str):
        """Learn from search feedback"""

    def get_optimization_metrics(self) -> Dict[str, float]:
        """Get search optimization metrics"""
```

#### LLM Response Optimizer

```python
class LLMResponseOptimizer:
    """Enhances LLM responses"""

    def optimize_response(self, query: str,
                         response: str) -> Tuple[str, float]:
        """
        Optimize response based on learned patterns

        Returns:
            (optimized_response, quality_score)
        """

    def learn_from_response(self, query: str,
                           response: str,
                           rating: str):
        """Learn from response feedback"""

    def get_response_templates(self) -> List[ResponseTemplate]:
        """Get learned response templates"""
```

#### Memory Architecture Evolution

```python
class MemoryArchitectureEvolution:
    """Evolves memory management strategies"""

    def consolidate_patterns(self) -> ConsolidationResult:
        """Consolidate similar patterns"""

    def prune_memory(self, threshold: float = 0.3) -> PruningResult:
        """Remove unused patterns"""

    def optimize_access_patterns(self) -> OptimizationResult:
        """Optimize memory access patterns"""

    def get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory usage metrics"""
```

## Usage Examples

### Basic Adaptive Processing

```python
from holo_index.adaptive_learning import AdaptiveLearningOrchestrator
import asyncio

# Initialize
orchestrator = AdaptiveLearningOrchestrator()

# Process with adaptation
async def process_search(query):
    result = await orchestrator.process_adaptive_request(
        query=query,
        raw_results=search_results,
        raw_response=initial_response,
        context={
            'search_limit': 5,
            'advisor_enabled': True
        }
    )

    # Use enhanced results
    print(f"Enhanced Query: {result.query_processing.enhanced_query}")
    print(f"Adaptation Score: {result.overall_performance['system_adaptation_score']}")

    return result

# Run
result = asyncio.run(process_search("find authentication module"))
```

### Recording Feedback

```python
# Record positive feedback
orchestrator.record_feedback(
    query="find authentication module",
    results=result.search_optimization.optimized_results,
    rating="useful"
)

# Record negative feedback
orchestrator.record_feedback(
    query="broken query",
    results=[],
    rating="needs_more"
)
```

### Monitoring Adaptation

```python
# Get metrics
metrics = orchestrator.get_adaptation_metrics()
print(f"Query Optimization: {metrics['query_optimization']:.2%}")
print(f"Search Stability: {metrics['search_ranking_stability']:.2%}")
print(f"Response Quality: {metrics['response_improvement']:.2%}")
print(f"Memory Efficiency: {metrics['memory_efficiency']:.2%}")
```

### Direct Component Usage

```python
from holo_index.adaptive_learning import AdaptiveQueryProcessor

# Use query processor directly
processor = AdaptiveQueryProcessor()
enhanced_query, confidence = processor.enhance_query("auth module")
print(f"Enhanced: {enhanced_query} (confidence: {confidence:.2f})")

# Learn from outcome
processor.learn_from_query(enhanced_query, results_quality=0.8)
```

## Integration Points

### With HoloIndex CLI
Automatically integrated when Phase 3 is available:
```python
# Enabled by default if available
[INFO] Phase 3: Adaptive Learning initialized
[INFO] Phase 3: Processing with adaptive learning...
```

### Storage Locations
```
E:/HoloIndex/adaptive_learning/
├── query_patterns.json      # Learned query patterns
├── search_metrics.json      # Search optimization data
├── response_templates.json  # Response templates
├── memory_evolution.json    # Memory patterns
└── adaptation_metrics.json  # Performance metrics
```

## Performance Considerations

- **Async Processing**: Uses asyncio for non-blocking operations
- **Memory Limit**: Keeps last 1000 patterns by default
- **Pruning**: Automatically prunes patterns below 0.3 utility
- **Learning Rate**: 0.01 default, adjustable
- **Adaptation Interval**: Every 100 queries

## Error Handling

Methods may raise:
- `ImportError`: Missing adaptive learning dependencies
- `RuntimeError`: Async context required
- `ValueError`: Invalid parameters
- `MemoryError`: Pattern memory exceeded

## WSP Compliance

- **WSP 48**: Recursive Self-Improvement implementation
- **WSP 60**: Module Memory Architecture
- **WSP 11**: Complete interface documentation
- **WSP 84**: Pattern memory verification