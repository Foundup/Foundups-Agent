# FoundUps SDK Module Interface Documentation

## Public API

### Classes

#### `FoundUpsClient`
Main SDK client for FoundUps platform access.

**Constructor:**
```python
FoundUpsClient(base_url: str, api_key: Optional[str] = None, timeout: int = 30) -> FoundUpsClient
```

**Methods:**
```python
health_check() -> Dict[str, Any]
system_status() -> Dict[str, Any]
search(query: str, limit: int = 5, include_content: bool = False) -> SearchResponse
analyze(query: str, advisor: bool = True) -> AnalysisResult
check_module(module_name: str) -> Dict[str, Any]
get_wsp_guidance(topic: str) -> List[str]
```

#### `SearchResponse`
Search results container.

#### `AnalysisResult`
AI analysis results container.

### Convenience Functions

#### `quick_search(base_url: str, query: str, limit: int = 5) -> SearchResponse`
Quick search without client instantiation.

#### `quick_analyze(base_url: str, query: str, advisor: bool = True) -> AnalysisResult`
Quick analysis without client instantiation.

## Configuration

### Environment Variables
- `FOUNDUP_URL`: Default FoundUps instance URL
- `FOUNDUP_API_KEY`: Optional authentication key

### Error Handling
- `FoundUpsError`: Base exception for SDK errors
