#!/usr/bin/env python3
"""
Debug Bell State verification to understand why it's failing
"""

import asyncio
import sys
import os
import re

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

async def debug_bell_state():
    """Debug Bell State verification"""
    print("[DEBUG] Testing Bell State verification with actual data...")

    try:
        from servers.holo_index.server import holo_server

        # Get search results
        result = await holo_server.semantic_code_search('stream_resolver', limit=3)

        print(f"Code results: {len(result['code_results'])}")
        print(f"WSP results: {len(result['wsp_results'])}")
        print(f"Current Bell State result: {result['bell_state_alignment']}")

        # Debug the Bell State calculation manually
        code_results = result['code_results']
        wsp_results = result['wsp_results']

        print(f"\n[DEBUG] Bell State inputs: {len(code_results)} code, {len(wsp_results)} wsp")

        if not code_results or not wsp_results:
            print("[DEBUG] Bell State fails: missing code or wsp results")
            return

        # Extract WSP keywords
        wsp_keywords = set()
        for wsp in wsp_results:
            content = wsp.get('content', '').lower()
            print(f"[DEBUG] WSP content sample: {content[:100]}...")

            # Extract protocol numbers
            protocols = re.findall(r'wsp\s*\d+', content)
            wsp_keywords.update(protocols)
            print(f"[DEBUG] Found protocols: {protocols}")

            # Add key WSP terms
            key_terms = ['protocol', 'standard', 'compliance', 'governance', 'consciousness']
            found_terms = [term for term in key_terms if term in content]
            wsp_keywords.update(found_terms)
            print(f"[DEBUG] Found key terms: {found_terms}")

        print(f"[DEBUG] Total WSP keywords: {wsp_keywords}")

        # Extract code keywords
        code_keywords = set()
        for code in code_results:
            content = code.get('content', '').lower()
            print(f"[DEBUG] Code content sample: {content[:100]}...")

            # Look for WSP references in code
            wsp_refs = re.findall(r'wsp\s*\d+', content)
            code_keywords.update(wsp_refs)
            print(f"[DEBUG] Found WSP refs in code: {wsp_refs}")

            # Add implementation terms
            impl_terms = ['implement', 'protocol', 'standard', 'compliance', 'consciousness']
            found_impl = [term for term in impl_terms if term in content]
            code_keywords.update(found_impl)
            print(f"[DEBUG] Found impl terms: {found_impl}")

        print(f"[DEBUG] Total code keywords: {code_keywords}")

        # Calculate overlap
        overlap = len(wsp_keywords & code_keywords)
        total_wsp = len(wsp_keywords)

        print(f"[DEBUG] Keyword overlap: {overlap}/{total_wsp}")

        if total_wsp > 0:
            entanglement_score = overlap / total_wsp
            print(f"[DEBUG] Entanglement score: {entanglement_score}")
            bell_state = entanglement_score > 0.5
            print(f"[DEBUG] Bell State alignment: {bell_state}")
        else:
            print("[DEBUG] Bell State fails: no WSP keywords found")

        # Show what would be needed for Bell State alignment
        print("
[ANALYSIS] To achieve Bell State alignment (>50% overlap):")
        print(f"  Current overlap: {overlap}/{total_wsp} = {overlap/max(total_wsp,1)*100:.1f}%")

        missing_terms = wsp_keywords - code_keywords
        if missing_terms:
            print(f"  Missing in code: {missing_terms}")
            print("  Suggestion: Code should reference these WSP terms")

    except Exception as e:
        print(f"[ERROR] Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_bell_state())
