# MCP DAEmons Public API Interface

## Overview

MCP DAEmons provides a comprehensive API for autonomous MCP server management. All interfaces follow WSP 77 (Agent Coordination Protocol) for consistent integration.

## Core Classes

### MCPDaemon

Main daemon class providing autonomous MCP server management.

#### Constructor
```python
MCPDaemon()
```

**Parameters**: None

**Returns**: Configured MCPDaemon instance

**Raises**:
- `RuntimeError`: If another daemon instance is already running

#### Methods

##### Lifecycle Management

###### `start() -> None`
Starts the MCP DAEmons and begins autonomous operation.

**Behavior**:
- Initializes all configured MCP servers
- Starts health monitoring loops
- Begins autonomous management

**Raises**: Various exceptions during initialization

###### `stop() -> None`
Stops the MCP DAEmons and performs cleanup.

**Behavior**:
- Signals all monitoring threads to stop
- Stops all managed MCP servers
- Releases instance lock
- Performs cleanup

##### Server Management

###### `start_server(server_name: str) -> bool`
Starts a specific MCP server.

**Parameters**:
- `server_name` (str): Name of the server to start (e.g., "holo_index")

**Returns**: `True` if successful, `False` otherwise

**Behavior**:
- Checks if server is already running
- Starts server process with configured environment
- Begins health monitoring for the server

###### `stop_server(server_name: str) -> bool`
Stops a specific MCP server.

**Parameters**:
- `server_name` (str): Name of the server to stop

**Returns**: `True` if successful, `False` otherwise

**Behavior**:
- Sends SIGTERM to server process
- Waits up to 10 seconds for graceful shutdown
- Force kills if necessary

###### `start_all_servers() -> None`
Starts all configured MCP servers.

**Behavior**: Iterates through all configured servers and starts each one.

###### `stop_all_servers() -> None`
Stops all MCP servers.

**Behavior**: Iterates through all servers and stops each one.

##### Monitoring & Status

###### `get_server_status() -> Dict[str, Any]`
Gets comprehensive status of all managed servers.

**Returns**: Dictionary with server status information:

```python
{
    "server_name": {
        "running": bool,
        "pid": int or None,
        "start_time": str or None,
        "cpu_usage": float,
        "memory_mb": float,
        "health_checks": int,
        "consecutive_failures": int,
        "request_count": int,
        "error_count": int
    }
}
```

###### `update_health_metrics() -> None`
Updates global health metrics for the MCP ecosystem.

**Behavior**:
- Calculates aggregate CPU/memory usage
- Counts active vs failed servers
- Updates performance metrics
- Maintains historical metrics (last 100 entries)

## Data Classes

### MCPServerInfo

Represents information about a managed MCP server.

**Attributes**:
- `name` (str): Server identifier
- `command` (str): Executable command
- `args` (List[str]): Command arguments
- `env` (Dict[str, str]): Environment variables
- `process` (Optional[subprocess.Popen]): Running process
- `start_time` (Optional[datetime]): When server was started
- `health_checks` (int): Number of successful health checks
- `last_health_check` (Optional[datetime]): Last health check time
- `consecutive_failures` (int): Consecutive failure count
- `cpu_usage` (float): Current CPU usage percentage
- `memory_mb` (float): Current memory usage in MB
- `request_count` (int): Total requests processed
- `error_count` (int): Total errors encountered

### MCPHealthMetrics

Represents health metrics for the entire MCP ecosystem.

**Attributes**:
- `total_servers` (int): Total number of configured servers
- `active_servers` (int): Number of currently running servers
- `failed_servers` (int): Number of servers in failed state
- `total_cpu_usage` (float): Aggregate CPU usage across all servers
- `total_memory_mb` (float): Aggregate memory usage across all servers
- `total_requests` (int): Total requests processed across all servers
- `total_errors` (int): Total errors across all servers
- `average_response_time` (float): Average response time (future feature)

## Configuration

### Environment Variables
- None required (all configuration loaded from setup_mcp_servers.py)

### Configuration Files
- **Server Config**: `foundups-mcp-p1/setup_mcp_servers.py`
- **Instance Lock**: Uses `modules.infrastructure.instance_lock`

### Resource Limits (Configurable)
```python
resource_limits = {
    'max_cpu_per_server': 50.0,      # Max CPU % per server
    'max_memory_per_server': 500.0,  # Max memory MB per server
    'max_total_cpu': 80.0,            # Max total CPU % across all servers
    'max_total_memory': 2048.0,       # Max total memory MB across all servers
}
```

## Error Handling

### Common Exceptions

#### `RuntimeError: MCP DAEmons already running`
**Cause**: Another daemon instance is already active
**Solution**: Stop the existing daemon first or use instance management tools

#### `subprocess.CalledProcessError`
**Cause**: Failed to execute MCP server command
**Solution**: Check server configuration and system PATH

#### `psutil.AccessDenied`
**Cause**: Insufficient permissions to monitor processes
**Solution**: Run daemon with appropriate permissions

### Logging

All operations are logged with structured logging:
- **INFO**: Normal operations and health summaries
- **WARNING**: Resource usage alerts and recoverable errors
- **ERROR**: Critical failures and unrecoverable errors

## Integration Examples

### Basic Usage
```python
from modules.infrastructure.mcp_daemon import MCPDaemon

# Start autonomous management
daemon = MCPDaemon()
daemon.start()  # Runs indefinitely

# In another process/thread, check status
status = daemon.get_server_status()
print(f"Active servers: {sum(1 for s in status.values() if s['running'])}")
```

### Health Monitoring Integration
```python
# Get real-time health metrics
daemon.update_health_metrics()
metrics = daemon.health_metrics

print(f"System Health: {metrics.active_servers}/{metrics.total_servers} servers")
print(f"Resource Usage: CPU {metrics.total_cpu_usage:.1f}%, Memory {metrics.total_memory_mb:.1f}MB")
```

### Server-Specific Management
```python
# Start specific server
success = daemon.start_server("holo_index")
if success:
    print("HoloIndex server started successfully")

# Stop specific server
success = daemon.stop_server("unicode_cleanup")
if success:
    print("Unicode cleanup server stopped")
```

## WSP Compliance

- **WSP 80**: Cube-Level DAE Architecture
- **WSP 77**: Agent Coordination Protocol
- **WSP 90**: UTF-8 Enforcement
- **WSP 26-29**: DAE Lifecycle Management
- **WSP 15**: Module Prioritization System (health monitoring priority)

## Future Extensions

The API is designed for future enhancements:
- **Metrics Dashboard**: Real-time health visualization
- **Predictive Maintenance**: AI-powered failure prediction
- **Dynamic Scaling**: Automatic server scaling based on demand
- **Advanced Coordination**: Inter-DAE communication protocols
