#!/usr/bin/env python3
"""
Generate 93 WSP Sentinel Opportunity Matrix and launch P0 augmentation wave
"""

import sys
import json
from pathlib import Path

# Add paths
sys.path.append('../..')
sys.path.append('../../../..')

def generate_matrix():
    """Generate the complete WSP Sentinel Opportunity Matrix"""
    print('🌊 Generating 93 WSP Sentinel Opportunity Matrix...')

    try:
        from modules.ai_intelligence.ric_dae.src.ricdae_wsp_analyzer import RicDAEWSPAnalyzer

        analyzer = RicDAEWSPAnalyzer()
        matrix = analyzer.generate_sentinel_opportunity_matrix()

        print(f'✅ Matrix generated: {len(matrix)} WSPs analyzed')

        # Save matrix
        matrix_file = Path('../../../WSP_framework/docs/matrices/WSP_Sentinel_Opportunity_Matrix.json')
        with open(matrix_file, 'w') as f:
            json.dump(matrix, f, indent=2)
        print(f'💾 Matrix saved to {matrix_file}')

        # Show P0 protocols
        p0_protocols = [wsp for wsp in matrix if wsp.get('priority') == 'P0']
        print(f'\n🏄 P0 Wave Protocols ({len(p0_protocols)}):')
        for wsp in p0_protocols:
            wsp_num = wsp.get('wsp_number', 'Unknown')
            sai_score = wsp.get('sai_score', 0)
            opportunity = wsp.get('opportunity', 'Unknown')
            print(f'  {wsp_num}: {sai_score} SAI - {opportunity}')

        print('\n⚡ Ready for P0 augmentation wave!')
        return matrix, p0_protocols

    except Exception as e:
        print(f'[ERROR] Matrix generation failed: {str(e)}')
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    matrix, p0_protocols = generate_matrix()
    if matrix and p0_protocols:
        print(f'\n[COMPLETE] Generated matrix with {len(p0_protocols)} P0 protocols ready for augmentation')
    else:
        print('\n[FAILED] Matrix generation failed')
