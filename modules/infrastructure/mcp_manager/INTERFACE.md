# MCP Manager - Public API

## Functions

### `show_mcp_services_menu()`
Display MCP Services interactive menu and handle user interactions.

**Usage**:
```python
from modules.infrastructure.mcp_manager.src.mcp_manager import show_mcp_services_menu

# In main.py menu
show_mcp_services_menu()
```

**Returns**: None (interactive menu loop)

## Classes

### `MCPServerManager`
Core manager for MCP server lifecycle.

**Methods**:
- `get_server_status(server_name: str) -> Tuple[bool, Optional[int]]`
- `start_server(server_name: str) -> bool`
- `stop_server(server_name: str) -> bool`
- `get_available_tools(server_name: str) -> List[Dict[str, str]]`

## Integration Example

```python
# main.py integration
elif choice == "14":
    # MCP Services Gateway
    from modules.infrastructure.mcp_manager.src.mcp_manager import show_mcp_services_menu
    show_mcp_services_menu()
```

## Tool Access (Future)

Future versions will provide direct tool invocation:
```python
manager = MCPServerManager()
manager.call_tool("holo_index", "semantic_code_search", query="DAE architecture")
```
