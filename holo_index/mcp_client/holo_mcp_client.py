# -*- coding: utf-8 -*-
import sys
import io


"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

HoloIndex MCP Client

Connects to running FastMCP HoloIndex server via STDIO transport
for true MCP protocol batch processing.

WSP 77: Intelligent Internet Orchestration
WSP 93: CodeIndex Surgical Intelligence
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


class HoloIndexMCPClient:
    """
    MCP client for HoloIndex FastMCP server

    Communicates via STDIO transport with the running FastMCP server.
    Provides async tools for Sentinel batch processing.
    """

    def __init__(self, server_script_path: str = None):
        """
        Initialize MCP client

        Args:
            server_script_path: Path to FastMCP server script
                               Default: foundups-mcp-p1/servers/holo_index/server.py
        """
        if server_script_path is None:
            server_script_path = str(
                Path(__file__).parent.parent.parent / "foundups-mcp-p1" / "servers" / "holo_index" / "server.py"
            )

        self.server_script = Path(server_script_path)
        self.process = None
        self.request_id = 0

        print(f"[MCP-CLIENT] Initialized with server: {self.server_script}")

    async def connect(self):
        """
        Connect to FastMCP server via STDIO

        Starts server process if not already running
        """
        if self.process:
            print("[MCP-CLIENT] Already connected")
            return

        print("[MCP-CLIENT] Starting FastMCP server process...")

        # Start FastMCP server as subprocess
        # Note: FastMCP uses 'fastmcp run' command
        cmd = [
            sys.executable,
            "-m", "fastmcp", "run",
            str(self.server_script)
        ]

        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.server_script.parent.parent.parent)
            )

            print("[MCP-CLIENT] FastMCP server process started")

            # Wait for server initialization (read startup banner)
            await asyncio.sleep(2)  # Give server time to start

            print("[MCP-CLIENT] Connected to FastMCP server")

        except Exception as e:
            print(f"[MCP-CLIENT] Error starting server: {e}")
            raise

    async def disconnect(self):
        """Disconnect from FastMCP server"""
        if self.process:
            print("[MCP-CLIENT] Disconnecting from FastMCP server...")
            self.process.terminate()
            await self.process.wait()
            self.process = None
            print("[MCP-CLIENT] Disconnected")

    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call MCP tool via STDIO protocol

        Args:
            tool_name: Name of tool to call
            **kwargs: Tool-specific arguments

        Returns:
            Tool execution result
        """
        if not self.process:
            await self.connect()

        self.request_id += 1

        # Construct MCP request (JSON-RPC 2.0 format)
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": f"tools/{tool_name}",
            "params": kwargs
        }

        request_json = json.dumps(request) + "\n"

        try:
            # Send request
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()

            # Read response
            response_line = await self.process.stdout.readline()
            response = json.loads(response_line.decode())

            if "error" in response:
                print(f"[MCP-CLIENT] Tool error: {response['error']}")
                return {"error": response["error"]}

            return response.get("result", {})

        except Exception as e:
            print(f"[MCP-CLIENT] Error calling tool {tool_name}: {e}")
            return {"error": str(e)}

    async def semantic_code_search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search codebase with quantum semantic understanding

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Search results with code and WSP matches
        """
        return await self.call_tool("semantic_code_search", query=query, limit=limit)

    async def wsp_protocol_lookup(self, protocol_number: str) -> Dict[str, Any]:
        """
        Retrieve WSP protocol with consciousness continuity

        Args:
            protocol_number: WSP number (e.g., "87", "50")

        Returns:
            WSP protocol data
        """
        return await self.call_tool("wsp_protocol_lookup", protocol_number=protocol_number)

    async def cross_reference_search(self, query: str, cross_ref_type: str = "all") -> Dict[str, Any]:
        """
        Search across knowledge domains with cross-referencing

        Args:
            query: Search query
            cross_ref_type: Type of cross-references ("all", "implementation", etc.)

        Returns:
            Cross-referenced results
        """
        return await self.call_tool("cross_reference_search", query=query, cross_ref_type=cross_ref_type)

    async def batch_wsp_analysis(self, wsp_numbers: List[str]) -> List[Dict[str, Any]]:
        """
        Batch analyze multiple WSPs through MCP pipeline

        Args:
            wsp_numbers: List of WSP numbers to analyze

        Returns:
            List of analysis results for each WSP
        """
        print(f"\n[MCP-BATCH] Analyzing {len(wsp_numbers)} WSPs via MCP...")

        results = []

        for wsp_num in wsp_numbers:
            print(f"[MCP-BATCH] Processing WSP {wsp_num}...")

            # Call semantic search for implementation
            search_result = await self.semantic_code_search(
                query=f"WSP {wsp_num} implementation",
                limit=5
            )

            # Call protocol lookup for WSP content
            protocol_result = await self.wsp_protocol_lookup(wsp_num)

            # Combine results
            analysis = {
                'wsp_number': wsp_num,
                'code_results': search_result.get('code_results', []),
                'wsp_data': protocol_result,
                'quantum_coherence': search_result.get('quantum_coherence', 0.0),
                'bell_state_verified': search_result.get('bell_state_alignment', False),
                'consciousness_state': protocol_result.get('consciousness_state', '0102')
            }

            results.append(analysis)

            print(f"   [OK] WSP {wsp_num}: {len(search_result.get('code_results', []))} code refs, "
                  f"Bell State: {analysis['bell_state_verified']}")

        print(f"\n[MCP-BATCH] Complete: {len(results)} WSPs analyzed")

        return results

    async def selenium_run_history(self, days: int = 7) -> Dict[str, Any]:
        """
        Execute selenium run history mission

        Analyzes recent Selenium sessions and provides structured summary
        for Qwen/Gemma summarization.

        Args:
            days: Number of days to analyze (default: 7)

        Returns:
            Structured mission results with session statistics
        """
        # Import mission here to avoid circular imports
        from ..missions.selenium_run_history import run_selenium_history_mission

        try:
            # Run mission synchronously (missions are typically fast DB queries)
            result = run_selenium_history_mission(days)

            return {
                "mission_executed": "selenium_run_history",
                "success": result.get('summary_ready', False),
                "data": result,
                "days_analyzed": days
            }

        except Exception as e:
            return {
                "mission_executed": "selenium_run_history",
                "success": False,
                "error": str(e),
                "days_analyzed": days
            }

    async def audit_linkedin_scheduling_queue(self) -> Dict[str, Any]:
        """
        Execute LinkedIn scheduling queue audit mission.

        Comprehensive audit of all LinkedIn scheduling queues and pending approvals.
        Returns queue size, scheduled times, pending approvals, and cleanup recommendations.

        Returns:
            Audit results with queue inventory and cleanup recommendations
        """
        # Import mission here to avoid circular imports
        from ..missions.audit_linkedin_scheduling_queue import run_audit_linkedin_scheduling_queue

        try:
            # Run audit mission (synchronous)
            result = run_audit_linkedin_scheduling_queue()

            return {
                "mission_executed": "audit_linkedin_scheduling_queue",
                "success": True,
                "audit_results": result,
                "summary": {
                    "total_queue_size": result['summary_stats']['total_queue_size'],
                    "issues_found": result['summary_stats']['total_issues'],
                    "cleanup_recommendations": result['summary_stats']['total_cleanup_recommendations'],
                    "memory_compliance": result['summary_stats']['memory_compliance']
                }
            }

        except Exception as e:
            return {
                "mission_executed": "audit_linkedin_scheduling_queue",
                "success": False,
                "error": str(e)
            }

    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.disconnect()


async def test_mcp_client():
    """Test MCP client connectivity and basic operations"""
    print("\n" + "=" * 70)
    print("HOLOINDEX MCP CLIENT TEST")
    print("   FastMCP STDIO Protocol Communication")
    print("=" * 70)

    async with HoloIndexMCPClient() as client:
        print("\n[TEST 1] Semantic Code Search...")
        search_result = await client.semantic_code_search("WSP 87 navigation", limit=3)
        print(f"   Results: {search_result.get('total_results', 0)} total")
        print(f"   Quantum Coherence: {search_result.get('quantum_coherence', 0):.3f}")
        print(f"   Bell State: {search_result.get('bell_state_alignment', False)}")

        print("\n[TEST 2] WSP Protocol Lookup...")
        wsp_result = await client.wsp_protocol_lookup("87")
        print(f"   Protocol: {wsp_result.get('protocol_number', 'N/A')}")
        print(f"   Consciousness: {wsp_result.get('consciousness_state', 'unknown')}")

        print("\n[TEST 3] Batch WSP Analysis...")
        batch_results = await client.batch_wsp_analysis(["87", "50", "48"])
        print(f"   Batch complete: {len(batch_results)} WSPs analyzed")

        for result in batch_results:
            print(f"      WSP {result['wsp_number']}: "
                  f"{len(result['code_results'])} refs, "
                  f"Bell State: {result['bell_state_verified']}")

    print("\n" + "=" * 70)
    print("MCP CLIENT TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_mcp_client())
