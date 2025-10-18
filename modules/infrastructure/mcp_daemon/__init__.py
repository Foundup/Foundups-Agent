# -*- coding: utf-8 -*-
"""
MCP DAEmons Module
==================

The cardiovascular system for DAEs - autonomous MCP server management.

This module provides:
- MCPDaemon class for managing MCP servers
- Health monitoring and automatic recovery
- Resource optimization and load balancing
- Inter-server coordination

WSP Compliance: WSP 80 (Cube-Level DAE), WSP 77 (Agent Coordination Protocol)
"""

from .src.mcp_daemon import MCPDaemon, MCPServerInfo, MCPHealthMetrics

__all__ = ['MCPDaemon', 'MCPServerInfo', 'MCPHealthMetrics']
