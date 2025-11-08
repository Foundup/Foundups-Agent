#!/usr/bin/env python3
"""
MCP Sanity Ping - Quick validation of MCP server wiring
Run this to test if MCP integration is working without full server startup
"""

import sys
import os

def test_mcp_imports():
    """Test basic MCP imports"""
    try:
        import fastmcp
        print("FastMCP available")
        return True
    except ImportError:
        print("FastMCP not available - run: pip install fastmcp>=2.12.3")
        return False

def test_holo_index():
    """Test HoloIndex semantic search"""
    try:
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from holo_index.core.holo_index import HoloIndex
        holo = HoloIndex(quiet=True)

        # Quick count check
        code_count = holo.get_code_entry_count()
        wsp_count = holo.get_wsp_entry_count()

        print(f"HoloIndex loaded: {code_count} code entries, {wsp_count} WSP docs")

        # Quick search test
        if code_count > 0:
            results = holo.search("test", limit=1)
            code_hits = len(results.get('code', []))
            wsp_hits = len(results.get('wsps', []))
            print(f"Search works: {code_hits} code hits, {wsp_hits} WSP hits")

        return True

    except Exception as e:
        print(f"HoloIndex test failed: {e}")
        return False

def test_mcp_server():
    """Test MCP server can be imported"""
    try:
        from servers.holo_index.server import HoloIndexMCPServer
        print("MCP server import successful")
        return True
    except Exception as e:
        print(f"MCP server import failed: {e}")
        return False

def main():
    print("MCP Sanity Ping")
    print("=" * 40)

    tests = [
        ("FastMCP Import", test_mcp_imports),
        ("HoloIndex Core", test_holo_index),
        ("MCP Server", test_mcp_server)
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\nTesting {name}...")
        if test_func():
            passed += 1
        else:
            print(f"   Failed: {name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("All systems go! MCP is ready.")
        print("To start server: fastmcp run servers/holo_index/server.py")
        return 0
    else:
        print("Some issues detected. Check error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
