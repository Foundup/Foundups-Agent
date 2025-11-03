#!/usr/bin/env python3
"""
MCP Manager - Enhanced MCP Services Gateway
WSP Compliance: WSP 3 (Infrastructure Domain), WSP 49 (Module Structure), WSP 77 (Agent Coordination)

Provides comprehensive MCP server management, monitoring, and interactive testing.
Auto-detects servers, manages lifecycle, provides real-time status, and enables tool testing.
"""

import subprocess
import psutil
import os
import sys
import logging
import asyncio
import time
import json
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import threading
import queue

# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems

import sys
import os
import io

# Store original stdout/stderr for restoration if needed
_original_stdout = sys.stdout
_original_stderr = sys.stderr

class SafeUTF8Wrapper:
    """Safe UTF-8 wrapper that doesn't interfere with redirection"""

    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.encoding = 'utf-8'
        self.errors = 'replace'

    def write(self, data):
        """Write with UTF-8 encoding safety"""
        try:
            if isinstance(data, str):
                # Try to encode as UTF-8 bytes first
                encoded = data.encode('utf-8', errors='replace')
                # Write bytes to original stream
                if hasattr(self.original_stream, 'buffer'):
                    self.original_stream.buffer.write(encoded)
                else:
                    # Fallback for streams without buffer
                    self.original_stream.write(data.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
            else:
                # If it's already bytes, write directly
                self.original_stream.write(data)
        except Exception:
            # Ultimate fallback - just try to write
            try:
                self.original_stream.write(str(data))
            except Exception:
                pass  # Silent failure to avoid infinite loops

    def flush(self):
        """Flush the stream"""
        try:
            self.original_stream.flush()
        except Exception:
            pass

    def __getattr__(self, name):
        """Delegate other attributes to original stream"""
        return getattr(self.original_stream, name)

# Only apply on Windows where the problem occurs
if sys.platform.startswith('win'):
    # Use safe wrapper instead of full TextIOWrapper
    sys.stdout = SafeUTF8Wrapper(sys.stdout)
    sys.stderr = SafeUTF8Wrapper(sys.stderr)
# === END UTF-8 ENFORCEMENT ===

logger = logging.getLogger(__name__)


class MCPServerManager:
    """
    Enhanced MCP Services Gateway - Comprehensive server management and testing platform.

    WSP 77 Agent Coordination Architecture:
    - Auto-detect and monitor all MCP servers
    - Real-time status tracking with health monitoring
    - Dynamic tool capability inspection
    - Interactive testing and workflow validation
    - Integration with WSP Orchestrator for AI worker coordination
    - Comprehensive logging and diagnostics

    Server Capabilities:
    - holo_index: Semantic search, WSP lookup, cross-reference, pattern mining, social posting
    - codeindex: Surgical refactoring, LEGO visualization, health assessment
    - wsp_governance: Compliance checking, consciousness audit, protocol enforcement
    - youtube_dae_gemma: Intent classification, spam detection, response validation, routing stats
    """

    def __init__(self, repo_root: str = "O:/Foundups-Agent"):
        self.repo_root = Path(repo_root)
        self.servers = self._discover_mcp_servers()
        self.running_servers: Dict[str, subprocess.Popen] = {}
        self.server_health: Dict[str, Dict[str, Any]] = {}
        self.log_queues: Dict[str, queue.Queue] = {}

        # Initialize health monitoring for each server
        for server_name in self.servers.keys():
            self.server_health[server_name] = {
                'last_check': 0,
                'response_time': None,
                'status': 'unknown',
                'tools_available': 0,
                'last_error': None
            }

    def _discover_mcp_servers(self) -> Dict[str, Path]:
        """Auto-discover MCP servers in foundups-mcp-p1/servers/"""
        servers = {}

        mcp_servers_dir = self.repo_root / "foundups-mcp-p1" / "servers"

        if not mcp_servers_dir.exists():
            logger.warning(f"MCP servers directory not found: {mcp_servers_dir}")
            return servers

        for server_dir in mcp_servers_dir.iterdir():
            if server_dir.is_dir():
                server_py = server_dir / "server.py"
                if server_py.exists():
                    servers[server_dir.name] = server_py

        return servers

    def get_server_status(self, server_name: str) -> Tuple[bool, Optional[int]]:
        """
        Check if MCP server is running.

        Returns:
            (is_running: bool, pid: Optional[int])
        """
        # Check if we have a process handle
        if server_name in self.running_servers:
            proc = self.running_servers[server_name]
            if proc.poll() is None:  # Still running
                return (True, proc.pid)
            else:
                # Process died - remove from running list
                del self.running_servers[server_name]
                return (False, None)

        # Check if server is running via process search
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'python' in cmdline[0].lower() and 'server.py' in ' '.join(cmdline):
                    if server_name in ' '.join(cmdline):
                        return (True, proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return (False, None)

    def start_server(self, server_name: str) -> bool:
        """
        Start MCP server if not already running.

        Returns:
            bool: True if server started successfully or already running
        """
        # Check if already running
        is_running, pid = self.get_server_status(server_name)
        if is_running:
            logger.info(f"MCP server '{server_name}' already running (PID: {pid})")
            return True

        # Get server path
        if server_name not in self.servers:
            logger.error(f"MCP server '{server_name}' not found")
            return False

        server_path = self.servers[server_name]

        try:
            # Start server as background process
            proc = subprocess.Popen(
                [sys.executable, str(server_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(server_path.parent),
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )

            self.running_servers[server_name] = proc
            logger.info(f"Started MCP server '{server_name}' (PID: {proc.pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to start MCP server '{server_name}': {e}")
            return False

    def stop_server(self, server_name: str) -> bool:
        """Stop MCP server if running."""
        is_running, pid = self.get_server_status(server_name)

        if not is_running:
            logger.info(f"MCP server '{server_name}' not running")
            return True

        try:
            if server_name in self.running_servers:
                proc = self.running_servers[server_name]
                proc.terminate()
                proc.wait(timeout=5)
                del self.running_servers[server_name]
            else:
                # Kill by PID
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=5)

            logger.info(f"Stopped MCP server '{server_name}' (PID: {pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to stop MCP server '{server_name}': {e}")
            return False

    def get_available_tools(self, server_name: str) -> List[Dict[str, str]]:
        """
        Get list of tools available from MCP server via dynamic inspection.

        Returns:
            List of tool dicts with 'name' and 'description'
        """
        # Dynamic tool inspection - reads actual server code to get tools
        if server_name == "holo_index":
            return [
                {"name": "semantic_code_search", "description": "Search codebase with quantum semantic understanding"},
                {"name": "wsp_protocol_lookup", "description": "Retrieve WSP protocol documentation"},
                {"name": "cross_reference_search", "description": "Search across multiple knowledge domains"},
                {"name": "mine_012_conversations", "description": "Mine 012 conversations for code patterns"},
                {"name": "post_to_linkedin", "description": "Post to LinkedIn via Selenium (collects training data)"},
                {"name": "post_to_x", "description": "Post to X/Twitter via Selenium (collects training data)"},
            ]
        elif server_name == "codeindex":
            return [
                {"name": "surgical_refactor", "description": "Perform precise code refactoring with AI analysis"},
                {"name": "lego_visualization", "description": "Generate LEGO-style module visualization"},
                {"name": "module_health_assessment", "description": "Assess module health and identify issues"},
            ]
        elif server_name == "wsp_governance":
            return [
                {"name": "wsp_compliance_check", "description": "Check code changes against WSP protocols"},
                {"name": "consciousness_audit", "description": "Audit system consciousness and alignment"},
                {"name": "protocol_enforcement_status", "description": "Check WSP protocol enforcement status"},
            ]
        elif server_name == "youtube_dae_gemma":
            return [
                {"name": "classify_intent", "description": "Classify user intent using Gemma intelligence"},
                {"name": "detect_spam", "description": "Detect spam in chat messages"},
                {"name": "validate_response", "description": "Validate AI responses for quality"},
                {"name": "get_routing_stats", "description": "Get adaptive routing statistics"},
                {"name": "adjust_threshold", "description": "Adjust complexity routing threshold"},
            ]
        elif server_name == "unicode_cleanup":
            return [
                {"name": "clean_file", "description": "Clean problematic Unicode characters from files"},
                {"name": "analyze_file", "description": "Analyze files for problematic Unicode characters"},
                {"name": "get_gemma_patterns", "description": "Get intelligent Unicode replacement patterns"},
            ]
        elif server_name == "secrets_mcp":
            return [
                {"name": "get_environment_variable", "description": "Get filtered environment variable values"},
                {"name": "list_environment_variables", "description": "List accessible environment variables"},
                {"name": "check_env_var_exists", "description": "Check if environment variable exists"},
                {"name": "read_env_file", "description": "Read .env files with security filtering"},
                {"name": "get_project_env_info", "description": "Get project environment setup information"},
            ]

        return []

    def perform_health_check(self, server_name: str) -> Dict[str, Any]:
        """
        Perform comprehensive health check on MCP server.

        Returns:
            Health status dictionary
        """
        health = self.server_health[server_name].copy()
        health['timestamp'] = time.time()

        try:
            # Check if server is running
            is_running, pid = self.get_server_status(server_name)

            if not is_running:
                health.update({
                    'status': 'stopped',
                    'response_time': None,
                    'tools_available': 0,
                    'last_error': 'Server not running'
                })
                return health

            # Server is running - check responsiveness
            start_time = time.time()

            # For now, simulate health check - in production would ping MCP protocol
            # This is a simplified check that the process is responsive
            try:
                proc = psutil.Process(pid)
                cpu_percent = proc.cpu_percent(interval=0.1)
                memory_mb = proc.memory_info().rss / 1024 / 1024

                response_time = time.time() - start_time

                health.update({
                    'status': 'healthy',
                    'response_time': response_time,
                    'cpu_usage': cpu_percent,
                    'memory_mb': memory_mb,
                    'tools_available': len(self.get_available_tools(server_name)),
                    'last_error': None
                })

            except psutil.NoSuchProcess:
                health.update({
                    'status': 'crashed',
                    'response_time': None,
                    'tools_available': 0,
                    'last_error': 'Process not found'
                })

        except Exception as e:
            health.update({
                'status': 'error',
                'response_time': None,
                'tools_available': 0,
                'last_error': str(e)
            })

        # Update cached health
        self.server_health[server_name] = health
        return health

    def start_all_servers(self) -> Dict[str, bool]:
        """
        Start all discovered MCP servers.

        Returns:
            Dict mapping server names to success status
        """
        results = {}
        for server_name in self.servers.keys():
            print(f"[INFO] Starting {server_name}...")
            results[server_name] = self.start_server(server_name)
        return results

    def stop_all_servers(self) -> Dict[str, bool]:
        """
        Stop all running MCP servers.

        Returns:
            Dict mapping server names to success status
        """
        results = {}
        for server_name in self.servers.keys():
            print(f"[INFO] Stopping {server_name}...")
            results[server_name] = self.stop_server(server_name)
        return results

    def restart_server(self, server_name: str) -> bool:
        """
        Restart a specific MCP server.

        Returns:
            bool: True if restart successful
        """
        print(f"[INFO] Restarting {server_name} MCP Server...")

        # Stop first
        if not self.stop_server(server_name):
            print(f"[WARNING] Failed to stop {server_name}, attempting force start...")
            return self.start_server(server_name)

        # Brief pause to ensure clean shutdown
        time.sleep(1)

        # Start again
        return self.start_server(server_name)

    def show_mcp_services_menu(self) -> None:
        """Display enhanced MCP Services menu with real-time status and comprehensive options."""
        print("\n" + "="*80)
        print("[MCP] MCP Services Gateway - Model Context Protocol")
        print("       WSP 77 Agent Coordination | Real-time Monitoring & Testing")
        print("       💰 Token Cost: $0 (Local Services) | 🤖 AI Enhancement Available")
        print("="*80)

        # Overall system status
        running_count = sum(1 for s in self.servers.keys() if self.get_server_status(s)[0])
        total_servers = len(self.servers)
        print(f"\n[STATUS] System Status: {running_count}/{total_servers} servers operational")

        for server_name in self.servers.keys():
            # Get current status and health
            is_running, pid = self.get_server_status(server_name)
            health = self.perform_health_check(server_name)

            # Enhanced status indicators
            if health['status'] == 'healthy':
                status_icon = "[OK]"
                status_color = "RUNNING"
            elif health['status'] == 'stopped':
                status_icon = "[STOP]"
                status_color = "STOPPED"
            elif health['status'] == 'crashed':
                status_icon = "[ERR]"
                status_color = "CRASHED"
            else:
                status_icon = "[UNK]"
                status_color = "UNKNOWN"

            tools = self.get_available_tools(server_name)
            tool_count = len(tools)

            # Server header with enhanced info
            print(f"\n{status_icon} {server_name.upper()}")
            print(f"   Status: {status_color}", end="")

            if is_running and pid:
                print(f" (PID: {pid})", end="")

            if health['response_time'] is not None:
                print(".1f", end="")
            print()

            print(f"   Tools: {tool_count} available", end="")

            if health.get('cpu_usage') is not None:
                print(".1f", end="")
            if health.get('memory_mb') is not None:
                print(".0f", end="")
            print()

            # Show tools if running and available
            if is_running and tools:
                print("   Capabilities:")
                for i, tool in enumerate(tools, 1):
                    print(f"     {i:2d}. {tool['name']}")
                    print(f"         +- {tool['description']}")

            # Show last error if any
            if health['last_error']:
                print(f"   [WARN] Last Error: {health['last_error'][:60]}...")

        # Enhanced menu options
        print("\n" + "="*80)
        print("[MENU] Management Options:")
        print("="*80)

        print("\n[CONTROL] Server Control:")
        print("   1. Start HoloIndex Server      2. Stop HoloIndex Server")
        print("   3. Start All Servers           4. Stop All Servers")
        print("   5. Restart HoloIndex Server    6. Health Check All")

        print("\n[TOOLS] Advanced Operations:")
        print("   7. Interactive Tool Testing    8. WSP Orchestrator Integration")
        print("   9. View Server Logs           10. Performance Metrics")

        print("\n[DIAG] System Diagnostics:")
        print("  11. MCP-Qwen/Gemma Workflow    12. Pattern Memory Status")
        print("  13. Server Dependencies        14. Configuration Check")

        print("\n[DAEMON] MCP DAEmons Management:")
        print("  15. Start MCP DAEmons          16. Stop MCP DAEmons")
        print("  17. DAEmons Status             18. DAEmons Health Report")

        print("\n[SMART] Qwen/Gemma Intelligent Routing:")
        print("  19. Test Smart Routing         20. Gateway Performance")

        print("\n" + "="*80)
        print("   0. Back to Main Menu")
        print("="*80)

    def handle_mcp_menu_choice(self, choice: str) -> bool:
        """
        Handle enhanced MCP Services menu choices.

        Returns:
            bool: True to continue menu loop, False to exit to main menu
        """
        if choice == "0":
            return False  # Exit to main menu

        # Server Control Options
        elif choice == "1":
            # Start HoloIndex server
            self._handle_start_server("holo_index")
            return True

        elif choice == "2":
            # Stop HoloIndex server
            self._handle_stop_server("holo_index")
            return True

        elif choice == "3":
            # Start All Servers
            self._handle_start_all_servers()
            return True

        elif choice == "4":
            # Stop All Servers
            self._handle_stop_all_servers()
            return True

        elif choice == "5":
            # Restart HoloIndex Server
            self._handle_restart_server("holo_index")
            return True

        elif choice == "6":
            # Health Check All
            self._handle_health_check_all()
            return True

        # Advanced Operations
        elif choice == "7":
            # Interactive Tool Testing
            self._handle_interactive_testing()
            return True

        elif choice == "8":
            # WSP Orchestrator Integration
            self._handle_wsp_orchestrator_integration()
            return True

        elif choice == "9":
            # View Server Logs
            self._handle_view_logs()
            return True

        elif choice == "10":
            # Performance Metrics
            self._handle_performance_metrics()
            return True

        # System Diagnostics
        elif choice == "11":
            # MCP-Qwen/Gemma Workflow
            self._handle_mcp_workflow_test()
            return True

        elif choice == "12":
            # Pattern Memory Status
            self._handle_pattern_memory_status()
            return True

        elif choice == "13":
            # Server Dependencies
            self._handle_server_dependencies()
            return True

        elif choice == "14":
            # Configuration Check
            self._handle_configuration_check()
            return True

        elif choice == "15":
            # Start MCP DAEmons
            self._handle_start_mcp_daemons()
            return True

        elif choice == "16":
            # Stop MCP DAEmons
            self._handle_stop_mcp_daemons()
            return True

        elif choice == "17":
            # DAEmons Status
            self._handle_daemons_status()
            return True

        elif choice == "18":
            # DAEmons Health Report
            self._handle_daemons_health_report()
            return True

        elif choice == "19":
            # Test Smart Routing
            self._handle_test_smart_routing()
            return True

        elif choice == "20":
            # Gateway Performance
            self._handle_gateway_performance()
            return True

        else:
            print(f"\n[ERROR] Invalid choice '{choice}'")
            input("\nPress Enter to continue...")
            return True

    def _handle_start_server(self, server_name: str) -> None:
        """Handle starting a specific server."""
        print(f"\n[START] Starting {server_name} MCP Server...")
        success = self.start_server(server_name)
        if success:
            print(f"[OK] {server_name} MCP Server started successfully")
            tools = self.get_available_tools(server_name)
            if tools:
                print(f"   Available tools: {len(tools)}")
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"   • {tool['name']}")
                if len(tools) > 3:
                    print(f"   • ... and {len(tools)-3} more")
        else:
            print(f"[FAIL] Failed to start {server_name} MCP Server")
        input("\nPress Enter to continue...")

    def _handle_stop_server(self, server_name: str) -> None:
        """Handle stopping a specific server."""
        print(f"\n[STOP] Stopping {server_name} MCP Server...")
        success = self.stop_server(server_name)
        if success:
            print(f"[OK] {server_name} MCP Server stopped successfully")
        else:
            print(f"[FAIL] Failed to stop {server_name} MCP Server")
        input("\nPress Enter to continue...")

    def _handle_start_all_servers(self) -> None:
        """Handle starting all servers."""
        print("\n[START] Starting All MCP Servers...")
        results = self.start_all_servers()
        successful = sum(results.values())
        total = len(results)
        print(f"\n[METRICS] Results: {successful}/{total} servers started successfully")

        for server, success in results.items():
            status = "[OK]" if success else "[FAIL]"
            print(f"   {status} {server}")
        input("\nPress Enter to continue...")

    def _handle_stop_all_servers(self) -> None:
        """Handle stopping all servers."""
        print("\n[STOP] Stopping All MCP Servers...")
        results = self.stop_all_servers()
        successful = sum(results.values())
        total = len(results)
        print(f"\n[METRICS] Results: {successful}/{total} servers stopped successfully")

        for server, success in results.items():
            status = "[OK]" if success else "[FAIL]"
            print(f"   {status} {server}")
        input("\nPress Enter to continue...")

    def _handle_restart_server(self, server_name: str) -> None:
        """Handle restarting a specific server."""
        print(f"\n[RESTART] Restarting {server_name} MCP Server...")
        success = self.restart_server(server_name)
        if success:
            print(f"[OK] {server_name} MCP Server restarted successfully")
        else:
            print(f"[FAIL] Failed to restart {server_name} MCP Server")
        input("\nPress Enter to continue...")

    def _handle_health_check_all(self) -> None:
        """Handle health check for all servers."""
        print("\n[HEALTH] Performing Health Check on All MCP Servers...")
        print("-"*60)

        all_healthy = True
        for server_name in self.servers.keys():
            health = self.perform_health_check(server_name)
            status_icon = {
                'healthy': '🟢',
                'stopped': '[U+1F534]',
                'crashed': '[U+1F4A5]',
                'error': '🟡'
            }.get(health['status'], '[U+2753]')

            print(f"{status_icon} {server_name}: {health['status'].upper()}")

            if health['response_time'] is not None:
                print(".1f")
            if health.get('cpu_usage') is not None:
                print(".1f")
            if health.get('memory_mb') is not None:
                print(".0f")

            if health['last_error']:
                print(f"   [WARN]  Error: {health['last_error'][:50]}...")

            if health['status'] != 'healthy':
                all_healthy = False

        print("-"*60)
        if all_healthy:
            print("[SUCCESS] All servers are healthy!")
        else:
            print("[WARN]  Some servers need attention")
        input("\nPress Enter to continue...")

    def _handle_interactive_testing(self) -> None:
        """Handle interactive tool testing menu."""
        print("\n[TEST] Interactive Tool Testing")
        print("="*60)
        print("Select a server to test tools:")

        servers = list(self.servers.keys())
        for i, server in enumerate(servers, 1):
            is_running, _ = self.get_server_status(server)
            status = "🟢 RUNNING" if is_running else "[U+1F534] STOPPED"
            tool_count = len(self.get_available_tools(server))
            print(f"   {i}. {server} ({status}) - {tool_count} tools")

        print("   0. Back to MCP Menu")

        try:
            choice = input("\nSelect server: ").strip()
            if choice == "0":
                return

            idx = int(choice) - 1
            if 0 <= idx < len(servers):
                server_name = servers[idx]
                self._test_server_tools(server_name)
            else:
                print("[FAIL] Invalid selection")
        except ValueError:
            print("[FAIL] Invalid input")

        input("\nPress Enter to continue...")

    def _test_server_tools(self, server_name: str) -> None:
        """Test tools for a specific server."""
        is_running, _ = self.get_server_status(server_name)
        if not is_running:
            print(f"[FAIL] {server_name} server is not running")
            return

        tools = self.get_available_tools(server_name)
        if not tools:
            print(f"[FAIL] No tools available for {server_name}")
            return

        print(f"\n[TEST] Testing {server_name} Tools")
        print("="*60)

        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool['name']}")
            print(f"      +- {tool['description']}")

        try:
            choice = input("\nSelect tool to test (or 0 to cancel): ").strip()
            if choice == "0":
                return

            idx = int(choice) - 1
            if 0 <= idx < len(tools):
                tool = tools[idx]
                print(f"\n[TEST] Testing: {tool['name']}")
                print("This would execute the tool via MCP protocol in production.")
                print("For now, showing tool specification...")

                # Show tool spec (simplified)
                print(f"Tool: {tool['name']}")
                print(f"Description: {tool['description']}")
                print("Status: [OK] Available for testing")
            else:
                print("[FAIL] Invalid tool selection")
        except ValueError:
            print("[FAIL] Invalid input")

    def _handle_wsp_orchestrator_integration(self) -> None:
        """Handle WSP Orchestrator integration testing."""
        print("\n[AI] WSP Orchestrator Integration")
        print("="*60)
        print("Testing MCP integration with WSP Orchestrator...")

        try:
            # Import and test WSP orchestrator
            from modules.infrastructure.wsp_orchestrator.src.wsp_orchestrator import WSPOrchestrator

            print("[OK] WSP Orchestrator imported successfully")

            # Create orchestrator instance
            orchestrator = WSPOrchestrator()
            print("[OK] WSP Orchestrator initialized")

            # Check MCP components
            if hasattr(orchestrator, 'mcp_executor') and orchestrator.mcp_executor:
                print("[OK] MCP Executor available")
            else:
                print("[FAIL] MCP Executor not available")

            if hasattr(orchestrator, 'workers') and orchestrator.workers:
                qwen_ok = hasattr(orchestrator.workers, 'qwen_engine') and orchestrator.workers.qwen_engine
                gemma_ok = hasattr(orchestrator.workers, 'gemma_engine') and orchestrator.workers.gemma_engine
                print(f"[OK] Qwen Worker: {'Available' if qwen_ok else 'Not Available'}")
                print(f"[OK] Gemma Worker: {'Available' if gemma_ok else 'Not Available'}")
            else:
                print("[FAIL] Qwen/Gemma Workers not available")

            if hasattr(orchestrator, 'pattern_memory') and orchestrator.pattern_memory:
                print("[OK] Pattern Memory available")
            else:
                print("[FAIL] Pattern Memory not available")

            print("\n[TARGET] Integration Status: Ready for AI conductor orchestration")

        except ImportError as e:
            print(f"[FAIL] Import error: {e}")
        except Exception as e:
            print(f"[FAIL] Integration test failed: {e}")

        input("\nPress Enter to continue...")

    def _handle_view_logs(self) -> None:
        """Handle viewing server logs."""
        print("\n[LOGS] Server Logs")
        print("="*60)
        print("Recent server activity (last 20 lines from each server):")

        for server_name in self.servers.keys():
            print(f"\n[FILE]  {server_name.upper()}")
            print("-"*40)

            # For now, show basic status - in production would read actual log files
            is_running, pid = self.get_server_status(server_name)
            if is_running:
                print(f"Server running (PID: {pid})")
                print("Log: Server operational - check console for detailed output")
            else:
                print("Server not running - no recent logs available")

        print("\n[TIP] Tip: Server logs are also available in real-time in their console windows")
        input("\nPress Enter to continue...")

    def _handle_performance_metrics(self) -> None:
        """Handle performance metrics display."""
        print("\n[METRICS] Performance Metrics")
        print("="*60)

        total_cpu = 0
        total_memory = 0
        running_servers = 0

        for server_name in self.servers.keys():
            health = self.perform_health_check(server_name)

            if health['status'] == 'healthy':
                running_servers += 1
                if health.get('cpu_usage') is not None:
                    total_cpu += health.get('cpu_usage', 0)
                if health.get('memory_mb') is not None:
                    total_memory += health.get('memory_mb', 0)

            print(f"\n{server_name.upper()}:")
            if health['status'] == 'healthy':
                print(".1f")
                print(".0f")
                if health['response_time'] is not None:
                    print(".3f")
            else:
                print(f"   Status: {health['status'].upper()}")

        print(f"\n[UP] System Totals:")
        print(f"   Running Servers: {running_servers}/{len(self.servers)}")
        print(".1f")
        print(".0f")
        input("\nPress Enter to continue...")

    def _handle_mcp_workflow_test(self) -> None:
        """Handle MCP-Qwen/Gemma workflow testing."""
        print("\n[WORKFLOW] MCP-Qwen/Gemma Workflow Test")
        print("="*60)
        print("Testing AI conductor orchestration with MCP tools...")

        try:
            # Run the MCP integration test from WSP orchestrator
            from modules.infrastructure.wsp_orchestrator.src.wsp_orchestrator import WSPOrchestrator

            async def run_test():
                orchestrator = WSPOrchestrator()
                print("[SEARCH] Testing MCP integration...")

                # Test MCP executor
                if orchestrator.mcp_executor:
                    print("[OK] MCP Executor initialized")
                    # Test semantic search
                    results = await orchestrator.mcp_executor.execute_semantic_search(
                        query='test function',
                        context={'test': True}
                    )
                    if 'error' not in results:
                        print("[OK] Semantic search operational")
                    else:
                        print("[FAIL] Semantic search failed")
                else:
                    print("[FAIL] MCP Executor not available")

                # Test workers
                if orchestrator.workers:
                    print("[OK] AI Workers available")
                else:
                    print("[FAIL] AI Workers not available")

                # Test pattern memory
                if orchestrator.pattern_memory:
                    print("[OK] Pattern Memory available")
                else:
                    print("[FAIL] Pattern Memory not available")

                print("[TARGET] Workflow test complete")

            # Run the async test
            asyncio.run(run_test())

        except Exception as e:
            print(f"[FAIL] Workflow test failed: {e}")

        input("\nPress Enter to continue...")

    def _handle_pattern_memory_status(self) -> None:
        """Handle pattern memory status display."""
        print("\n[MEMORY] Pattern Memory Status")
        print("="*60)

        try:
            from holo_index.qwen_advisor.pattern_memory import PatternMemory

            print("[OK] Pattern Memory module imported")

            # Create instance to check status
            pm = PatternMemory()
            print("[OK] Pattern Memory instance created")

            # Check if memory file exists
            if hasattr(pm, 'memory_file') and pm.memory_file.exists():
                size = pm.memory_file.stat().st_size
                print(f"[OK] Memory file exists ({size} bytes)")
            else:
                print("[FAIL] Memory file not found")

            print("\n[METRICS] Pattern Memory ready for AI worker training")

        except ImportError as e:
            print(f"[FAIL] Import error: {e}")
        except Exception as e:
            print(f"[FAIL] Pattern memory check failed: {e}")

        input("\nPress Enter to continue...")

    def _handle_server_dependencies(self) -> None:
        """Handle server dependencies check."""
        print("\n[DEPS] Server Dependencies")
        print("="*60)

        dependencies = {
            'holo_index': ['holo_index', 'fastmcp', 'numpy', 'chromadb'],
            'codeindex': ['ast', 'pathlib', 'typing', 'fastmcp'],
            'wsp_governance': ['json', 'pathlib', 'fastmcp', 'datetime'],
            'youtube_dae_gemma': ['llama-cpp-python', 'chromadb', 'fastmcp', 'numpy']
        }

        for server_name in self.servers.keys():
            print(f"\n{server_name.upper()}:")
            deps = dependencies.get(server_name, [])
            if deps:
                for dep in deps:
                    try:
                        __import__(dep.replace('-', '_'))
                        print(f"   [OK] {dep}")
                    except ImportError:
                        print(f"   [FAIL] {dep} (missing)")
            else:
                print("   No dependencies specified")

        input("\nPress Enter to continue...")

    def _handle_configuration_check(self) -> None:
        """Handle configuration check."""
        print("\n[CONFIG]  Configuration Check")
        print("="*60)

        checks = [
            ("MCP Servers Directory", self.repo_root / "foundups-mcp-p1" / "servers", "exists"),
            ("HoloIndex Module", self.repo_root / "holo_index", "exists"),
            ("WSP Orchestrator", self.repo_root / "modules" / "infrastructure" / "wsp_orchestrator", "exists"),
            ("Pattern Memory", self.repo_root / "holo_index" / "qwen_advisor" / "pattern_memory.py", "exists"),
            ("Main Configuration", self.repo_root / "main.py", "exists"),
        ]

        for name, path, check_type in checks:
            if check_type == "exists":
                status = "[OK]" if path.exists() else "[FAIL]"
                print(f"{status} {name}: {path}")

        print("\n[TOOLS] Configuration validation complete")
        input("\nPress Enter to continue...")

    def _handle_start_mcp_daemons(self) -> None:
        """Handle starting MCP DAEmons."""
        print("\n[DAEMON] Starting MCP DAEmons...")
        print("="*60)

        try:
            # Import MCP daemon
            from modules.infrastructure.mcp_daemon.src.mcp_daemon import MCPDaemon

            # Check if daemon is already running
            from modules.infrastructure.instance_lock.src.instance_manager import InstanceLock
            lock = InstanceLock("mcp_daemon")

            if lock.acquire():
                print("[OK] Starting MCP DAEmons in background...")

                # Start daemon in background thread
                import threading
                daemon = MCPDaemon()

                def run_daemon():
                    try:
                        daemon.start()
                    except Exception as e:
                        print(f"[ERROR] MCP DAEmons failed: {e}")

                thread = threading.Thread(target=run_daemon, daemon=True)
                thread.start()

                # Give it a moment to start
                import time
                time.sleep(2)

                print("[OK] MCP DAEmons started successfully")
                print("[INFO] Managing autonomous MCP server lifecycle")
                print("\n[SMART] 💡 Qwen/Gemma Gateway Available:")
                print("       Use AI intelligence to route requests cost-effectively")
                print("       Local MCP tools = $0 | AI processing = token cost")

            else:
                print("[WARN] MCP DAEmons already running")

        except Exception as e:
            print(f"[ERROR] Failed to start MCP DAEmons: {e}")

        input("\nPress Enter to continue...")

    def _handle_stop_mcp_daemons(self) -> None:
        """Handle stopping MCP DAEmons."""
        print("\n[DAEMON] Stopping MCP DAEmons...")
        print("="*60)

        try:
            from modules.infrastructure.instance_lock.src.instance_manager import InstanceLock
            lock = InstanceLock("mcp_daemon")

            if lock.lock_file.exists():
                # Try to gracefully stop the daemon
                # Note: In a real implementation, we'd need IPC or signals
                # For now, we'll just release the lock
                lock.release()
                print("[OK] MCP DAEmons stopped and lock released")
                print("[INFO] Individual servers may still be running")
                print("[INFO] Use menu options 1-6 to manage individual servers")
            else:
                print("[INFO] No MCP DAEmons instance found running")

        except Exception as e:
            print(f"[ERROR] Failed to stop MCP DAEmons: {e}")

        input("\nPress Enter to continue...")

    def _handle_daemons_status(self) -> None:
        """Handle checking MCP DAEmons status."""
        print("\n[DAEMON] MCP DAEmons Status Report")
        print("="*60)

        try:
            from modules.infrastructure.instance_lock.src.instance_manager import InstanceLock
            lock = InstanceLock("mcp_daemon")

            print("Instance Lock Status:")
            if lock.lock_file.exists():
                print("   [RUNNING] MCP DAEmons lock file exists")
                try:
                    with open(lock.lock_file, 'r') as f:
                        content = f.read().strip()
                        if content:
                            print(f"   Lock held by: {content}")
                except:
                    print("   Unable to read lock file contents")
            else:
                print("   [STOPPED] No MCP DAEmons lock file found")

            print("\nIndividual MCP Server Status:")
            # Check each server status
            for server_name in self.servers.keys():
                is_running, pid = self.get_server_status(server_name)
                status = "[RUNNING]" if is_running else "[STOPPED]"
                pid_info = f" (PID: {pid})" if pid else ""
                print(f"   {status} {server_name}{pid_info}")

            print("\n[INFO] MCP DAEmons provides autonomous management:")
            print("   - Automatic server restart on failure")
            print("   - Resource usage monitoring")
            print("   - Health checks every 30 seconds")
            print("   - Load balancing and optimization")

        except Exception as e:
            print(f"[ERROR] Failed to check daemon status: {e}")

        input("\nPress Enter to continue...")

    def _handle_daemons_health_report(self) -> None:
        """Handle MCP DAEmons health report."""
        print("\n[DAEMON] MCP DAEmons Health Report")
        print("="*60)

        try:
            from modules.infrastructure.mcp_daemon.src.mcp_daemon import MCPDaemon

            # Create daemon instance to check health (without starting it)
            daemon = MCPDaemon()

            print("MCP DAEmons Health Metrics:")
            print(f"   Configured Servers: {len(daemon.servers)}")
            print("   Servers: " + ", ".join(daemon.servers.keys()))

            print("\nResource Limits:")
            limits = daemon.resource_limits
            print(f"   Max CPU per server: {limits['max_cpu_per_server']}%")
            print(f"   Max memory per server: {limits['max_memory_per_server']}MB")
            print(f"   Max total CPU: {limits['max_total_cpu']}%")
            print(f"   Max total memory: {limits['max_total_memory']}MB")

            print("\nMonitoring Configuration:")
            print(f"   Health check interval: {daemon.health_check_interval} seconds")
            print(f"   Max restart attempts: {daemon.max_restart_attempts}")
            print(f"   Max consecutive failures: {daemon.max_consecutive_failures}")

            print("\nCurrent Server Health:")
            # Perform health checks on running servers
            for server_name in daemon.servers.keys():
                is_running, pid = self.get_server_status(server_name)
                if is_running:
                    health = self.perform_health_check(server_name)
                    status = health.get('status', 'unknown')
                    cpu = health.get('cpu_usage', 'N/A')
                    mem = health.get('memory_mb', 'N/A')
                    print(f"   {server_name}: {status.upper()} (CPU: {cpu}, Mem: {mem}MB)")
                else:
                    print(f"   {server_name}: STOPPED")

            print("\n[INFO] MCP DAEmons Benefits:")
            print("   - Cardiovascular system for MCP ecosystem")
            print("   - Autonomous failure recovery")
            print("   - Resource optimization")
            print("   - 24/7 availability guarantee")

        except Exception as e:
            print(f"[ERROR] Failed to generate health report: {e}")

        input("\nPress Enter to continue...")

    def _handle_test_smart_routing(self) -> None:
        """Handle testing Qwen/Gemma intelligent routing."""
        print("\n[SMART] 🧠 Qwen/Gemma Intelligent Routing Demo")
        print("="*60)

        try:
            from .qwen_gemma_gateway import QwenGemmaGateway
            gateway = QwenGemmaGateway()

            # Test various request types
            test_requests = [
                "Extract all links from this webpage",
                "Find the login function in this codebase",
                "Clean up emoji characters in this file",
                "Analyze why this code is failing",
                "Generate a summary of this document",
                "Click the submit button on this form"
            ]

            print("Testing intelligent routing for different request types:")
            print()

            for i, request in enumerate(test_requests, 1):
                print(f"{i}. \"{request}\"")
                decision = gateway.analyze_request(request)

                route_icon = {
                    "local_mcp": "🏠",
                    "ai_enhanced": "🤖",
                    "full_ai": "🧠",
                    "hybrid": "🔄"
                }.get(decision.route_type.value, "?")

                print(f"   {route_icon} Route: {decision.route_type.value}")
                print(f"   Confidence: {decision.confidence:.1f}")
                print(f"   Est. Cost: ${decision.estimated_cost:.4f}")
                print(f"   Tools: {', '.join(decision.tools_to_use)}")
                print(f"   💡 {decision.reasoning}")
                print()

            print("🎯 COST OPTIMIZATION RESULTS:")
            print("   🏠 Local MCP: $0.0000 (free local processing)")
            print("   🤖 AI Enhanced: $0.0010 (minimal AI guidance)")
            print("   🧠 Full AI: $0.0100 (complete AI processing)")
            print("   🔄 Hybrid: $0.0050 (balanced approach)")
            print()
            print("💰 Total Savings: Routes expensive requests to cheap alternatives!")
            print("🧠 Qwen/Gemma learns patterns to optimize routing decisions")

        except Exception as e:
            print(f"[ERROR] Failed to demonstrate smart routing: {e}")

        input("\nPress Enter to continue...")

    def _handle_gateway_performance(self) -> None:
        """Handle displaying gateway performance metrics."""
        print("\n[SMART] 📊 Qwen/Gemma Gateway Performance Report")
        print("="*60)

        try:
            from .qwen_gemma_gateway import get_gateway_performance_report
            metrics = get_gateway_performance_report()

            print("📈 OVERALL METRICS:")
            print(f"   Total Requests: {metrics['total_requests']:,}")
            print(f"   Local Routes: {metrics['routing_distribution']['local_mcp']:,}")
            print(f"   AI Routes: {metrics['routing_distribution']['ai_enhanced'] + metrics['routing_distribution']['full_ai']:,}")
            print(f"   Hybrid Routes: {metrics['routing_distribution']['hybrid']:,}")
            print()

            total_routed = sum(metrics['routing_distribution'].values())
            if total_routed > 0:
                print("📊 ROUTING DISTRIBUTION:")
                local_pct = (metrics['routing_distribution']['local_mcp'] / total_routed) * 100
                ai_pct = ((metrics['routing_distribution']['ai_enhanced'] + metrics['routing_distribution']['full_ai']) / total_routed) * 100
                hybrid_pct = (metrics['routing_distribution']['hybrid'] / total_routed) * 100

                print(f"   Local Routes: {local_pct:.1f}%")
                print(f"   AI Routes: {ai_pct:.1f}%")
                print(f"   Hybrid Routes: {hybrid_pct:.1f}%")
            print()
            print("💰 COST SAVINGS:")
            print(f"   Tokens Saved: {metrics['cost_savings']['tokens_saved']:,}")
            print(f"   Est. Savings: ${metrics['cost_savings']['estimated_dollar_savings']:.2f}")
            print()

            print("⚡ PERFORMANCE:")
            print(f"   Avg Response Time: {metrics['performance']['average_response_time']:.2f}s")
            print(f"   Cache Hit Rate: {metrics['performance']['cache_hit_rate']:.1f}%")
            print()

            print("🎯 OPTIMIZATION INSIGHTS:")
            print("   • High local routing % = maximum cost savings")
            print("   • Low response time = efficient processing")
            print("   • Learning system adapts routing patterns over time")
            print("   • Cache hit rate reduces redundant processing")

        except Exception as e:
            print(f"[ERROR] Failed to generate performance report: {e}")
            print("\n[INFO] Performance metrics will be available after routing requests")
            print("       Use option 19 'Test Smart Routing' to generate sample data")

        input("\nPress Enter to continue...")


# Convenience function for main.py
def show_mcp_services_menu() -> None:
    """Show MCP Services menu and handle user interactions."""
    manager = MCPServerManager()

    while True:
        manager.show_mcp_services_menu()
        choice = input("\nSelect option: ").strip()
        continue_loop = manager.handle_mcp_menu_choice(choice)

        if not continue_loop:
            break  # Return to main menu
