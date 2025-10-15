#!/usr/bin/env python3
"""
Update WSP Matrix with MCP Utility Ratings
"""

import json
import sys
from pathlib import Path

# Add paths
sys.path.append('../..')
sys.path.append('../../../..')

def update_wsp_matrix_with_mcp_ratings():
    """Add MCP utility ratings to all WSPs in the matrix"""

    matrix_path = Path('../../../WSP_framework/docs/matrices/WSP_Sentinel_Opportunity_Matrix.json')

    try:
        # Load existing matrix
        with open(matrix_path, 'r') as f:
            wsp_matrix = json.load(f)

        print(f'[MCP RATING] Processing {len(wsp_matrix)} WSPs...')

        # MCP utility ratings by WSP number
        mcp_ratings = {
            # Perfect SAI 222 WSPs - Maximum MCP utility
            '3': {'mcp_utility': 0.98, 'routing_relevance': 0.95, 'category': 'enterprise_domain'},
            '21': {'mcp_utility': 0.97, 'routing_relevance': 0.94, 'category': 'communication'},
            '22a': {'mcp_utility': 0.97, 'routing_relevance': 0.94, 'category': 'communication'},
            '34': {'mcp_utility': 0.96, 'routing_relevance': 0.93, 'category': 'intelligence'},
            '36': {'mcp_utility': 0.96, 'routing_relevance': 0.93, 'category': 'consciousness'},
            '37': {'mcp_utility': 0.96, 'routing_relevance': 0.93, 'category': 'scoring'},
            '48': {'mcp_utility': 0.95, 'routing_relevance': 0.92, 'category': 'improvement'},
            '50': {'mcp_utility': 0.95, 'routing_relevance': 0.92, 'category': 'intelligence'},
            '60': {'mcp_utility': 0.94, 'routing_relevance': 0.91, 'category': 'physics'},

            # High SAI WSPs (200-221) - High MCP utility
            '61': {'mcp_utility': 0.87, 'routing_relevance': 0.84, 'category': 'physics'},
            '62': {'mcp_utility': 0.86, 'routing_relevance': 0.83, 'category': 'refactoring'},
            '75': {'mcp_utility': 0.88, 'routing_relevance': 0.85, 'category': 'efficiency'},
            '80': {'mcp_utility': 0.95, 'routing_relevance': 0.92, 'category': 'orchestration'},
            '84': {'mcp_utility': 0.85, 'routing_relevance': 0.82, 'category': 'intelligence'},
            '87': {'mcp_utility': 0.89, 'routing_relevance': 0.86, 'category': 'consciousness'},
            '93': {'mcp_utility': 0.92, 'routing_relevance': 0.89, 'category': 'intelligence'},
            '95': {'mcp_utility': 0.83, 'routing_relevance': 0.80, 'category': 'intelligence'},
            '97': {'mcp_utility': 0.82, 'routing_relevance': 0.79, 'category': 'intelligence'},

            # Medium SAI WSPs (170-199) - Medium MCP utility
            '67': {'mcp_utility': 0.78, 'routing_relevance': 0.75, 'category': 'anticipation'},
            '39': {'mcp_utility': 0.85, 'routing_relevance': 0.82, 'category': 'consciousness'},
            '38': {'mcp_utility': 0.83, 'routing_relevance': 0.80, 'category': 'activation'},
            '13': {'mcp_utility': 0.76, 'routing_relevance': 0.73, 'category': 'system'},
            '30': {'mcp_utility': 0.74, 'routing_relevance': 0.71, 'category': 'orchestration'},
            '33': {'mcp_utility': 0.72, 'routing_relevance': 0.69, 'category': 'workflow'},

            # Lower SAI WSPs - Base MCP utility
            '26': {'mcp_utility': 0.68, 'routing_relevance': 0.65, 'category': 'tokenization'},
            '27': {'mcp_utility': 0.70, 'routing_relevance': 0.67, 'category': 'architecture'},
            '28': {'mcp_utility': 0.65, 'routing_relevance': 0.62, 'category': 'cluster'},
            '59': {'mcp_utility': 0.63, 'routing_relevance': 0.60, 'category': 'integration'},
            '53': {'mcp_utility': 0.61, 'routing_relevance': 0.58, 'category': 'environment'},
        }

        # Update each WSP with MCP ratings
        updated_count = 0
        for wsp in wsp_matrix:
            wsp_num = wsp.get('wsp_number', '')
            if wsp_num in mcp_ratings:
                wsp.update(mcp_ratings[wsp_num])
                updated_count += 1
            else:
                # Default rating for unrated WSPs
                sai_score = wsp.get('sai_score', 0)
                base_utility = min(sai_score / 222.0, 0.6)  # Max 0.6 for unrated
                wsp.update({
                    'mcp_utility': round(base_utility, 3),
                    'routing_relevance': round(base_utility * 0.9, 3),
                    'category': 'general'
                })

        # Save updated matrix
        with open(matrix_path, 'w') as f:
            json.dump(wsp_matrix, f, indent=2)

        # Generate summary
        high_mcp = [w for w in wsp_matrix if w.get('mcp_utility', 0) >= 0.8]
        med_mcp = [w for w in wsp_matrix if 0.6 <= w.get('mcp_utility', 0) < 0.8]
        low_mcp = [w for w in wsp_matrix if w.get('mcp_utility', 0) < 0.6]

        print(f'[MCP RATING COMPLETE]')
        print(f'  Updated WSPs: {updated_count}')
        print(f'  High MCP Utility (>=0.8): {len(high_mcp)}')
        print(f'  Medium MCP Utility (0.6-0.8): {len(med_mcp)}')
        print(f'  Low MCP Utility (<0.6): {len(low_mcp)}')

        # Show top MCP utility WSPs
        top_mcp = sorted(wsp_matrix, key=lambda x: x.get('mcp_utility', 0), reverse=True)[:5]
        print(f'\\n[TOP 5 MCP UTILITY WSPs]:')
        for wsp in top_mcp:
            wsp_num = wsp.get('wsp_number', 'Unknown')
            mcp_util = wsp.get('mcp_utility', 0)
            category = wsp.get('category', 'Unknown')
            print(f'  WSP {wsp_num}: {mcp_util} MCP utility ({category})')

        return wsp_matrix

    except Exception as e:
        print(f'[ERROR] Failed to update WSP matrix: {e}')
        return None

if __name__ == "__main__":
    matrix = update_wsp_matrix_with_mcp_ratings()
    if matrix:
        print(f'\\n[SUCCESS] MCP ratings added to {len(matrix)} WSPs')
        print('Ready for Gemma-3 adaptive routing system!')
    else:
        print('\\n[FAILED] MCP rating update failed')
