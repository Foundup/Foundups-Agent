# MCP DAEmons - Model Context Protocol Management Daemon

## Overview

MCP DAEmons is the cardiovascular system for DAEs, providing autonomous management of MCP (Model Context Protocol) servers. Just as YouTube DAEmons and HoloIndex DAEmons provide background infrastructure, MCP DAEmons ensures MCP servers are always available, healthy, and optimized.

## Key Features

- **Automatic Lifecycle Management**: Starts, stops, and restarts MCP servers autonomously
- **Health Monitoring**: Continuous monitoring with automatic failure recovery
- **Resource Optimization**: CPU/memory monitoring and load balancing
- **Inter-Server Coordination**: Manages dependencies between MCP servers
- **Real-time Metrics**: Performance monitoring and alerting
- **Instance Locking**: Prevents multiple daemon instances

## Architecture

```
MCP DAEmons
├── Server Management (start/stop/restart)
├── Health Monitoring (CPU, memory, responsiveness)
├── Resource Optimization (load balancing, scaling)
├── Failure Recovery (automatic restart, circuit breaking)
├── Metrics & Logging (performance tracking, alerts)
└── Coordination (inter-server communication)
```

## Supported MCP Servers

- **holo_index**: Semantic code search and intelligence
- **codeindex**: Code indexing and navigation
- **wsp_governance**: WSP compliance and governance
- **youtube_dae_gemma**: YouTube processing with AI
- **unicode_cleanup**: AI-powered Unicode cleanup

## Usage

### Starting MCP DAEmons

```bash
# From the repository root
python -m modules.infrastructure.mcp_daemon.src.mcp_daemon
```

### Programmatic Usage

```python
from modules.infrastructure.mcp_daemon import MCPDaemon

# Initialize and start
daemon = MCPDaemon()
daemon.start()  # Runs until stopped

# Get server status
status = daemon.get_server_status()
print(f"Active servers: {status}")

# Stop daemon
daemon.stop()
```

## Health Monitoring

MCP DAEmons continuously monitors:

- **Process Health**: Server responsiveness and uptime
- **Resource Usage**: CPU and memory consumption
- **Error Rates**: Request failures and recovery
- **Performance**: Response times and throughput

## Configuration

Configuration is loaded from `foundups-mcp-p1/setup_mcp_servers.py`. The daemon automatically:

- Discovers all configured MCP servers
- Sets up health monitoring intervals
- Configures resource limits
- Establishes failure recovery policies

## WSP Compliance

- **WSP 80**: Cube-Level DAE Architecture
- **WSP 77**: Agent Coordination Protocol
- **WSP 90**: UTF-8 Enforcement
- **WSP 26-29**: DAE Lifecycle Management

## Integration

MCP DAEmons integrates with:

- **Instance Manager**: Prevents multiple daemon instances
- **Health Monitoring**: Real-time metrics collection
- **Resource Manager**: System resource optimization
- **Coordination Layer**: Inter-DAE communication

## Benefits

1. **Reliability**: MCP tools are always available
2. **Performance**: Optimized resource usage across servers
3. **Resilience**: Automatic failure recovery
4. **Scalability**: Load balancing and resource management
5. **Observability**: Comprehensive monitoring and metrics

## Similar to YouTube DAEmons

Just as YouTube DAEmons provide background YouTube processing infrastructure, MCP DAEmons provide the critical infrastructure layer that ensures MCP servers (the tools DAEs depend on) are always running, healthy, and optimized.
