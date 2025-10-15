#!/usr/bin/env python3
"""
Test semantic concept matching for Bell State verification
"""

import asyncio
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

async def test_semantic_bell_state():
    """Test the new semantic concept matching Bell State verification"""
    print("[TEST] Testing semantic Bell State verification...")

    try:
        from servers.holo_index.server import holo_server

        # Test with stream_resolver search
        result = await holo_server.semantic_code_search('stream_resolver', limit=3)

        print(f"[RESULTS] Found {len(result['code_results'])} code, {len(result['wsp_results'])} wsp")
        print(f"[RESULTS] Bell State alignment: {result['bell_state_alignment']}")

        # Test semantic concept extraction
        print("\n[SEMANTIC] Testing concept extraction...")

        if result['code_results']:
            code_item = result['code_results'][0]
            code_concepts = holo_server._extract_semantic_concepts(code_item)
            print(f"[CODE] Content: {code_item['content'][:100]}...")
            print(f"[CODE] Concepts: {sorted(code_concepts)}")

        if result['wsp_results']:
            wsp_item = result['wsp_results'][0]
            wsp_concepts = holo_server._extract_semantic_concepts(wsp_item)
            print(f"\n[WSP] Content: {wsp_item['content'][:100]}...")
            print(f"[WSP] Concepts: {sorted(wsp_concepts)}")

        # Test concept overlap
        if result['code_results'] and result['wsp_results']:
            code_concepts = holo_server._extract_semantic_concepts(result['code_results'][0])
            wsp_concepts = holo_server._extract_semantic_concepts(result['wsp_results'][0])

            overlap = code_concepts & wsp_concepts
            union = code_concepts | wsp_concepts

            if union:
                similarity = len(overlap) / len(union)
                print(f"\n[OVERLAP] Shared concepts: {sorted(overlap)}")
                print(f"[OVERLAP] Semantic similarity: {similarity:.2f}")
                print(f"[OVERLAP] Bell State threshold met: {similarity > 0.3}")

        print("\n[SUCCESS] Semantic Bell State verification test completed!")

    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_semantic_bell_state())
