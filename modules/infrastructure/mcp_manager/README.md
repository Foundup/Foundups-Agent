# MCP Manager

**WSP Domain**: `infrastructure` (WSP 3)

## Purpose

Provides auto-discovery, startup, and management of MCP (Model Context Protocol) servers for 0102.

## Key Features

- **Auto-Discovery**: Automatically finds MCP servers in `foundups-mcp-p1/servers/`
- **Auto-Start**: Starts servers on demand (first tool use)
- **Status Tracking**: Shows which servers are running and available tools
- **Simple Interface**: Single menu option in main.py for all MCP services

## Architecture (First Principles)

**Problem**: 0102 needs access to MCP tools without manual server management
**Solution**: Auto-manage servers, provide simple gateway menu

**Occam's Razor**: One menu option -> Status + Tools -> Auto-start on use

## Usage

From main.py menu:
```
14. MCP Services (HoloIndex: [DOT]RUNNING | 6 tools)     | --mcp
```

## Available MCP Servers

### HoloIndex MCP Server
- **Tools**: 6 (semantic search, WSP lookup, 012.txt mining, LinkedIn/X posting)
- **Auto-Start**: Yes
- **Status Tracking**: Real-time PID monitoring

## WSP Compliance

- **WSP 3**: Infrastructure domain (server management)
- **WSP 49**: Full module structure
- **WSP 84**: Auto-management (don't duplicate manual work)
