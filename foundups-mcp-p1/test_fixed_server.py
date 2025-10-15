#!/usr/bin/env python3
"""
Test the fixed HoloIndex MCP server
"""

import asyncio
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

async def test_fixed_server():
    """Test the fixed HoloIndex MCP server"""
    print("[TEST] Testing fixed HoloIndex MCP server...")

    try:
        from servers.holo_index.server import holo_server
        print("[PASS] Server imported successfully")

        # Test HoloIndex directly first
        print("[SEARCH] Testing HoloIndex search directly...")
        direct_result = holo_server.holo_index.search('stream_resolver', limit=3)
        print(f"[DIRECT] Found {len(direct_result.get('code', []))} code, {len(direct_result.get('wsps', []))} WSP results")

        # Test semantic search by calling the underlying function
        print("[SEARCH] Testing semantic search through MCP...")
        # Find the semantic_code_search function
        search_func = None
        for attr_name in dir(holo_server):
            attr = getattr(holo_server, attr_name)
            if hasattr(attr, 'func') and 'semantic_code_search' in str(attr):
                search_func = attr.func
                break

        if search_func:
            result = await search_func(holo_server, 'stream_resolver', limit=3)
        else:
            print("[ERROR] Could not find semantic_code_search function")
            return None

        print(f"[RESULT] Total results: {result['total_results']}")
        print(f"[RESULT] Code results: {len(result['code_results'])}")
        print(f"[RESULT] WSP results: {len(result['wsp_results'])}")
        print(f"[RESULT] Bell State alignment: {result['bell_state_alignment']}")
        print(f"[RESULT] Quantum coherence: {result['quantum_coherence']}")

        # Show sample results
        if result['code_results']:
            print("[SAMPLE] First code result:")
            code = result['code_results'][0]
            print(f"  Path: {code.get('path', 'N/A')}")
            print(f"  Function: {code.get('function', 'N/A')}")
            print(f"  Relevance: {code.get('relevance', 'N/A')}")

        if result['wsp_results']:
            print("[SAMPLE] First WSP result:")
            wsp = result['wsp_results'][0]
            print(f"  Path: {wsp.get('path', 'N/A')}")
            print(f"  Protocol: {wsp.get('protocol', 'N/A')}")
            print(f"  Relevance: {wsp.get('relevance', 'N/A')}")

        # Test Bell State verification directly
        print("[BELL] Testing Bell State verification...")
        bell_state = await holo_server._verify_bell_state_alignment(
            result['code_results'],
            result['wsp_results']
        )
        print(f"[RESULT] Bell State calculation: {bell_state}")

        print("[SUCCESS] Fixed HoloIndex MCP server test completed!")
        return result

    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_fixed_server())
    if result and result['total_results'] > 0:
        print(f"\n[SUCCESS] Server is working! Found {result['total_results']} results")
        sys.exit(0)
    else:
        print("\n[FAILURE] Server test failed")
        sys.exit(1)
