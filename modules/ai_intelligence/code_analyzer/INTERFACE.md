# INTERFACE (WSP 11)

## Code Analyzer - AI Intelligence Module

### Public API

#### CodeAnalyzer Class

**Primary Methods:**

1. **`analyze_file(file_path: str) -> CodeAnalysisResult`**
   - Analyze a single Python file for code quality and WSP compliance
   - Returns: CodeAnalysisResult with complexity, quality, compliance scores

2. **`analyze_directory(directory_path: str) -> List[CodeAnalysisResult]`**
   - Analyze all Python files in a directory recursively
   - Returns: List of CodeAnalysisResult objects

3. **`trace_execution_graph(entry_point: str, max_depth: int = 10, modules_root: Optional[str] = None) -> ExecutionGraphResult`**
   - **NEW**: Trace execution graph from entry point following ALL imports (snake & ladders pattern)
   - Implements "CodeIndex" pattern for complete DAE execution mapping
   - Returns: ExecutionGraphResult with execution graph, orphan detection, Mermaid visualization

**Convenience Functions:**

- **`analyze_code(file_path: str) -> CodeAnalysisResult`**
  - Convenience wrapper for single file analysis

- **`analyze_module(module_path: str) -> List[CodeAnalysisResult]`**
  - Convenience wrapper for directory analysis

### Parameters

#### trace_execution_graph Parameters:
- **entry_point** (str): Starting file path (e.g., "main.py" or "main.py::monitor_youtube")
- **max_depth** (int, optional): Maximum import depth to trace (default: 10)
- **modules_root** (str, optional): Root directory containing modules/ folder (auto-detected if None)

#### analyze_file Parameters:
- **file_path** (str): Absolute path to Python file to analyze

#### analyze_directory Parameters:
- **directory_path** (str): Absolute path to directory to analyze

### Returns

#### ExecutionGraphResult (trace_execution_graph):
```python
@dataclass
class ExecutionGraphResult:
    entry_point: str              # Entry point file path
    total_modules: int            # Number of modules discovered
    execution_graph: Dict[str, List[str]]  # module -> list of imports
    module_list: List[str]        # All modules in execution order
    depth_map: Dict[str, int]     # module -> depth from entry
    orphaned_modules: List[Dict]  # modules in folder but not in graph
    mermaid_flowchart: str        # Mermaid visualization
```

#### CodeAnalysisResult (analyze_file, analyze_directory):
```python
@dataclass
class CodeAnalysisResult:
    file_path: str
    complexity_score: float       # Cyclomatic complexity
    quality_score: float          # Code quality (0-100)
    compliance_score: float       # WSP compliance (0-100)
    issues: List[str]             # Identified issues
    recommendations: List[str]    # Improvement recommendations
    wsp_compliance: Dict[str, bool]  # WSP standards check
```

### Errors

- **FileNotFoundError**: Entry point or file path does not exist
- **SyntaxError**: Python file has syntax errors (gracefully handled, returns 0 scores)
- **PermissionError**: Insufficient permissions to read file/directory

### Examples

#### Example 1: Trace YouTube DAE Execution Graph

```python
from code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

# Trace all modules imported by main.py (YouTube DAE)
result = analyzer.trace_execution_graph("main.py", max_depth=10)

print(f"Total modules: {result.total_modules}")
print(f"Orphaned modules: {len(result.orphaned_modules)}")

# Print first 10 modules
for module in result.module_list[:10]:
    depth = result.depth_map[module]
    print(f"[{depth}] {module}")

# Print orphaned modules
for orphan in result.orphaned_modules[:5]:
    print(f"Orphan: {orphan['module']}")
    print(f"  Reason: {orphan['reason']}")
```

**Expected Output:**
```
Total modules: 35
Orphaned modules: 464
[0] main.py
[1] O:\Foundups-Agent\modules\communication\livechat\src\auto_moderator_dae.py
[1] O:\Foundups-Agent\modules\platform_integration\stream_resolver\src\stream_resolver.py
...
```

#### Example 2: Analyze Single File

```python
from code_analyzer import analyze_code

result = analyze_code("modules/communication/livechat/src/message_processor.py")

print(f"Quality Score: {result.quality_score}")
print(f"Compliance Score: {result.compliance_score}")
print(f"Issues: {result.issues}")
print(f"Recommendations: {result.recommendations}")
```

#### Example 3: Analyze Entire Module

```python
from code_analyzer import analyze_module

results = analyze_module("modules/communication/livechat/")

# Print summary
for result in results:
    print(f"{result.file_path}: {result.compliance_score}% compliant")
```

#### Example 4: Generate Mermaid Visualization

```python
from code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
result = analyzer.trace_execution_graph("main.py")

# Save Mermaid flowchart
with open("execution_graph.md", "w") as f:
    f.write("```mermaid\n")
    f.write(result.mermaid_flowchart)
    f.write("```\n")

print("Mermaid flowchart saved to execution_graph.md")
```

### Integration Points

- **HoloIndex MCP**: Exposes execution tracing via MCP protocol for Qwen coordination
- **WSP 93 CodeIndex**: Implements surgical intelligence for DAE execution mapping
- **WSP 50 Pre-Action Verification**: Enables "search before act" pattern
- **WSP 3 Module Organization**: Validates enterprise domain structure

### Use Cases

1. **DAE Execution Mapping**: Map all modules used by YouTube/LinkedIn/Twitter DAEs
2. **Orphan Detection**: Find modules in folder structure but never imported
3. **Dependency Analysis**: Understand module dependency chains
4. **Architecture Validation**: Verify WSP 3 compliance across execution graph
5. **Refactoring Safety**: Identify modules safe to refactor (orphans vs active)

---

**Module maintained by 0102 pArtifact Agent following WSP protocols**
**Enhanced with execution tracing (snake & ladders pattern) for complete DAE mapping**
