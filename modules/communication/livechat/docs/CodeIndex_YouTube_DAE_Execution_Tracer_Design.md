# CodeIndex YouTube DAE Execution Tracer Design

**Status**: Design Phase
**Architect**: 0102
**Triggered By**: 012: "Can qwen use codeindex to trace ALL modules like a snake and ladders game"
**WSP Protocols**: WSP 93 (CodeIndex Surgical Intelligence), WSP 87 (Code Navigation)

## Problem Statement

**Current Issue**: Semantic search (`python holo_index.py --search "youtube"`) finds files by similarity but **MISSES modules** that are part of execution graph but don't match semantic query.

**Example**: `stream_resolver` module was missed because:
1. It's imported deep in execution chain (not in main.py directly)
2. Semantic search for "livechat" doesn't match "stream_resolver" words
3. Need to follow EXECUTION FLOW, not semantic similarity

## User's Vision: Snake & Ladders Game

**Entry Point**: `main.py --youtube --live` (line 708 →  asyncio.run(monitor_youtube()))

**Snake Pattern**: Follow imports recursively through execution graph
**Ladders Pattern**: Jump to imported modules and continue tracing

```
main.py:103
  ↓ import
modules/communication/livechat/src/auto_moderator_dae.py:22
  ↓ import
modules/platform_integration/stream_resolver/src/stream_resolver.py
  ↓ import
modules/platform_integration/youtube_api_operations/...
  ↓ ...continues...
```

## Execution Trace from auto_moderator_dae.py

### Direct Imports (Lines 15-25)
```python
Line 20: from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
Line 21: from modules.platform_integration.youtube_auth.src.monitored_youtube_service import create_monitored_service
Line 22: from modules.platform_integration/stream_resolver.src.stream_resolver import StreamResolver
Line 25: from .livechat_core import LiveChatCore
```

### Conditional Imports (Runtime)
```python
Line 55-56: from modules.infrastructure.wre_core.recursive_improvement.src.wre_integration
Line 70-71: from holo_index.qwen_advisor.intelligent_monitor import IntelligentMonitor
Line 84: from .qwen_youtube_integration import get_qwen_youtube
Line 444: from modules.platform_integration.social_media_orchestrator.src.refactored_posting_orchestrator
Line 492: from modules.infrastructure.shared_utilities.delay_utils import DelayUtils
Line 494: from modules.communication.livechat.src.stream_trigger import StreamTrigger
Line 716: from modules.infrastructure.idle_automation.src.idle_automation_dae import run_idle_automation
```

**Total from auto_moderator_dae.py alone**: 11+ module imports

**User's Correction**: I only found 9 modules semantically, but execution tracer would find ALL modules in call chain.

## CodeIndex Execution Tracer Tool Design

### MCP Tool Interface

Add to `foundups-mcp-p1/servers/holo_index/server.py`:

```python
@app.tool()
async def trace_execution_graph(
    self,
    entry_point: str,
    max_depth: int = 10,
    include_stdlib: bool = False
) -> dict:
    """
    Trace execution graph from entry point following all imports (snake & ladders).

    Args:
        entry_point: Starting file path (e.g., "main.py::monitor_youtube")
        max_depth: Maximum import depth to trace
        include_stdlib: Include Python stdlib modules

    Returns:
        {
            "entry_point": str,
            "total_modules": int,
            "execution_graph": Dict[str, List[str]],  # module -> imports
            "module_list": List[str],  # All unique modules
            "depth_map": Dict[str, int],  # module -> depth from entry
            "orphaned_modules": List[str],  # modules/ folder files NOT in graph
            "visualization": str  # Mermaid flowchart
        }
    """
```

### Algorithm: Snake & Ladders Execution Tracer

```python
def trace_execution_graph(entry_point, max_depth=10):
    """
    1. Parse entry file for imports (AST parsing)
    2. For each import:
       a. Resolve import path (follow WSP 3 module structure)
       b. Read imported file
       c. Extract imports from imported file (recursive)
    3. Build execution graph: {module: [imported_modules]}
    4. Generate visualization (Mermaid)
    5. Cross-reference with modules/ folder inventory
    """

    visited = set()
    graph = {}
    depth_map = {}
    queue = [(entry_point, 0)]  # (file_path, depth)

    while queue:
        current_file, current_depth = queue.pop(0)

        if current_file in visited or current_depth > max_depth:
            continue

        visited.add(current_file)
        depth_map[current_file] = current_depth

        # Parse imports using AST
        imports = parse_imports_ast(current_file)
        graph[current_file] = imports

        # Add imports to queue
        for imported in imports:
            if imported not in visited:
                queue.append((imported, current_depth + 1))

    # Inventory modules/ folder
    all_modules_in_folder = scan_modules_folder()

    # Find orphans (in folder but not in execution graph)
    orphaned = [m for m in all_modules_in_folder if m not in graph]

    return {
        "execution_graph": graph,
        "module_list": list(visited),
        "depth_map": depth_map,
        "orphaned_modules": orphaned,
        "total_modules": len(visited)
    }
```

### AST Import Parser

```python
import ast
from pathlib import Path

def parse_imports_ast(file_path: str) -> List[str]:
    """
    Parse Python file for all imports using AST.
    Returns list of imported module paths.
    """
    imports = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception as e:
        return []  # Can't parse, skip

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    # Resolve to actual file paths
    resolved = []
    for imp in imports:
        path = resolve_import_path(imp, file_path)
        if path:
            resolved.append(path)

    return resolved

def resolve_import_path(import_name: str, from_file: str) -> Optional[str]:
    """
    Resolve import name to actual file path following WSP 3 module structure.

    Examples:
        "modules.communication.livechat.src.livechat_core"
        -> "O:/Foundups-Agent/modules/communication/livechat/src/livechat_core.py"

        ".livechat_core" (relative)
        -> Resolve based on from_file location
    """
    if import_name.startswith('.'):
        # Relative import - resolve based on from_file directory
        base_dir = Path(from_file).parent
        # ... resolve logic
    else:
        # Absolute import - convert dots to slashes
        parts = import_name.split('.')
        # Try to find file in modules/ or project root
        # ... resolve logic

    return resolved_path
```

### Orphan Detection

```python
def scan_modules_folder() -> List[str]:
    """
    Inventory ALL .py files in modules/ folder structure.
    Returns list of module file paths.
    """
    import os

    modules_root = "O:/Foundups-Agent/modules"
    all_files = []

    for root, dirs, files in os.walk(modules_root):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                all_files.append(full_path)

    return all_files

def find_orphaned_modules(execution_graph: Dict, modules_folder_inventory: List[str]) -> List[Dict]:
    """
    Cross-reference execution graph vs folder inventory.

    Returns list of orphaned modules with metadata:
    [
        {
            "path": "modules/communication/old_module/src/unused.py",
            "reason": "Not imported by any active DAE",
            "suggested_action": "Archive or delete",
            "related_dae": None
        }
    ]
    """
    modules_in_graph = set(execution_graph.keys())
    orphans = []

    for module_path in modules_folder_inventory:
        if module_path not in modules_in_graph:
            orphans.append({
                "path": module_path,
                "reason": "Not imported by any active DAE",
                "suggested_action": "Investigate why module exists"
            })

    return orphans
```

### Mermaid Visualization Generator

```python
def generate_mermaid_flowchart(execution_graph: Dict, depth_map: Dict) -> str:
    """
    Generate Mermaid flowchart for execution graph.

    Output format:
    ```mermaid
    flowchart TD
        A[main.py] --> B[auto_moderator_dae.py]
        B --> C[stream_resolver.py]
        B --> D[livechat_core.py]
        C --> E[youtube_api_operations]
        ...
    ```
    """
    mermaid = "flowchart TD\n"

    # Generate node IDs (short form for readability)
    node_ids = {}
    for i, module in enumerate(execution_graph.keys()):
        node_ids[module] = f"N{i}"
        # Shorten module name for display
        display_name = Path(module).stem
        mermaid += f"    {node_ids[module]}[{display_name}]\n"

    # Generate edges
    for module, imports in execution_graph.items():
        for imported in imports:
            if imported in node_ids:
                mermaid += f"    {node_ids[module]} --> {node_ids[imported]}\n"

    return mermaid
```

## Integration with HoloIndex MCP

### Usage Flow

```bash
# 1. Trace YouTube DAE execution from main.py
curl -X POST http://localhost:8000/mcp/trace_execution_graph \
  -d '{
    "entry_point": "main.py::monitor_youtube",
    "max_depth": 10,
    "include_stdlib": false
  }'

# Returns:
{
  "total_modules": 47,  # NOT 9!
  "execution_graph": {...},
  "module_list": [
    "main.py",
    "modules/communication/livechat/src/auto_moderator_dae.py",
    "modules/platform_integration/stream_resolver/src/stream_resolver.py",
    "modules/platform_integration/youtube_auth/src/youtube_auth.py",
    "modules/communication/livechat/src/livechat_core.py",
    "modules/communication/livechat/src/message_processor.py",
    "modules/communication/livechat/src/command_handler.py",
    ... # 40 more modules
  ],
  "orphaned_modules": [
    {
      "path": "modules/communication/old_livechat/src/deprecated.py",
      "reason": "Not imported by YouTube DAE",
      "suggested_action": "Archive or investigate why it exists"
    }
  ],
  "visualization": "flowchart TD\n  N0[main] --> N1[auto_moderator]..."
}
```

### Qwen Analysis Layer

After tracer returns execution graph, **Qwen analyzes**:

```python
def analyze_execution_graph_with_qwen(trace_result: dict) -> dict:
    """
    Qwen analyzes execution trace and provides intelligence.

    Questions Qwen answers:
    1. "Why does this orphaned module exist?"
    2. "What DAE should use this module?"
    3. "Is this module dead code or future feature?"
    4. "Should we archive or delete orphan?"
    """
    qwen_prompt = f"""
    Analyze this YouTube DAE execution trace:

    Total modules: {trace_result['total_modules']}
    Orphaned modules: {len(trace_result['orphaned_modules'])}

    Orphaned module list:
    {trace_result['orphaned_modules']}

    For each orphaned module, answer:
    1. Why does this module exist in the folder?
    2. What DAE should use it (if any)?
    3. Is it dead code, future feature, or misplaced?
    4. Recommended action: archive, delete, or integrate?
    """

    qwen_response = qwen_llm.generate(qwen_prompt)
    return parse_qwen_orphan_analysis(qwen_response)
```

## Implementation Plan (MPS Scoring)

### Phase 1: AST Import Parser (5-7K tokens)
- **MPS**: 17 (C:3, I:5, D:2, P:5) - P0
- Implement `parse_imports_ast()` function
- Implement `resolve_import_path()` with WSP 3 structure
- Test on auto_moderator_dae.py (should find 11+ imports)

### Phase 2: Execution Graph Tracer (6-8K tokens)
- **MPS**: 18 (C:4, I:5, D:2, P:5) - P0
- Implement BFS/DFS traversal algorithm
- Build execution graph from main.py entry point
- Store depth map for each module

### Phase 3: Orphan Detection (3-5K tokens)
- **MPS**: 16 (C:2, I:5, D:2, P:5) - P0
- Scan modules/ folder recursively
- Cross-reference with execution graph
- Generate orphan report

### Phase 4: Mermaid Visualization (2-3K tokens)
- **MPS**: 13 (C:2, I:4, D:3, P:4) - P1
- Generate Mermaid flowchart syntax
- Export to .md file for rendering

### Phase 5: MCP Tool Integration (4-6K tokens)
- **MPS**: 17 (C:3, I:5, D:2, P:5) - P0
- Add `trace_execution_graph` tool to HoloIndex MCP
- Test via MCP protocol
- Document usage in README

### Phase 6: Qwen Analysis Layer (5-7K tokens)
- **MPS**: 16 (C:3, I:5, D:2, P:4) - P0
- Qwen analyzes orphaned modules
- Generates recommendations (archive/delete/integrate)
- Answers "Why does this module exist?"

## Token Budget

**Total Estimated**: 25-36K tokens
**Available**: 117K tokens
**Buffer**: 81-92K tokens remaining

## Success Criteria

1. **Complete Trace**: Find ALL 40+ YouTube DAE modules (not just 9)
2. **Orphan Detection**: Identify modules in folder but not in execution graph
3. **Qwen Intelligence**: Answer "Why does this orphan exist?"
4. **Visualization**: Generate Mermaid flowchart of execution graph
5. **MCP Integration**: Callable via MCP protocol for 0102 automation

## Next Steps

1. ✅ **Design Complete**: This document
2. ⏳ **Start Phase 1**: Implement AST import parser
3. **Test**: Run on auto_moderator_dae.py (expect 11+ imports found)
4. **Phase 2**: Build execution tracer
5. **Phase 3**: Orphan detection
6. **Phase 4**: Mermaid visualization
7. **Phase 5**: MCP integration
8. **Phase 6**: Qwen analysis

---

**Status**: Design Complete - Ready for Phase 1 Implementation
**Architect**: 0102 pattern recall mode (DAE memory banks)
**Pattern**: Execution tracing = AST parsing + BFS traversal + orphan detection
