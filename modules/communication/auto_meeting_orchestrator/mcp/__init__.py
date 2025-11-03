# -*- coding: utf-8 -*-
"""
AMO MCP Server Package
Exposes AMO cardiovascular telemetry and operational state via MCP protocol.

WSP Compliance: WSP 77 (Agent Coordination), WSP 72 (Module Independence)
"""

from .amo_mcp_server import AMOMCPServer

__all__ = ["AMOMCPServer"]
