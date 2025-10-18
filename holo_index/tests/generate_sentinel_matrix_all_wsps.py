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

TSUNAMI WAVE: Generate Complete Sentinel Opportunity Matrix

Batch process ALL 93 WSPs through validated Phase 5 pipeline
to create complete Sentinel augmentation roadmap.

Expected time: ~4 seconds (93 × 0.04s)
vs Manual: 186-372 minutes

WSP 93: CodeIndex Surgical Intelligence
This IS the tsunami pipe - proven, fast, complete.
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from holo_index.tests.test_phase5_integrated_wsp_analysis import IntegratedWSPAnalyzer


def get_all_wsp_numbers() -> List[str]:
    """
    Get all WSP numbers from WSP_framework/src directory

    Returns list of WSP numbers (e.g., ["1", "2", "3", "22a", ...])
    """
    wsp_dir = Path("O:/Foundups-Agent/WSP_framework/src")
    wsp_files = list(wsp_dir.glob("WSP_*.md"))

    wsp_numbers = []
    for wsp_file in wsp_files:
        # Extract number from filename: WSP_87_Code_Navigation_Protocol.md -> 87
        # Handle both WSP_87 and WSP_22a formats
        filename = wsp_file.stem  # WSP_87_Code_Navigation_Protocol
        parts = filename.split('_')

        if len(parts) >= 2:
            wsp_num = parts[1]  # "87" or "22a"
            wsp_numbers.append(wsp_num)

    # Sort: numbers first, then alpha suffixes
    def sort_key(wsp):
        # Extract numeric part
        num_part = ''.join(c for c in wsp if c.isdigit())
        alpha_part = ''.join(c for c in wsp if c.isalpha())
        return (int(num_part) if num_part else 999, alpha_part)

    wsp_numbers.sort(key=sort_key)

    return wsp_numbers


def generate_complete_matrix():
    """
    TSUNAMI WAVE: Generate Sentinel Opportunity Matrix for all 93 WSPs

    This is the full barrel - complete system transformation
    """
    print("\n" + "=" * 70)
    print("TSUNAMI WAVE: COMPLETE SENTINEL OPPORTUNITY MATRIX")
    print("   93 WSPs -> Complete Augmentation Roadmap")
    print("=" * 70)

    # Initialize analyzer
    print("\n[INIT] Loading Phase 5 validated pipeline...")
    analyzer = IntegratedWSPAnalyzer()
    print("   [OK] Pipeline ready - riding the wave!")

    # Get all WSP numbers
    print("\n[DISCOVERY] Finding all WSPs...")
    wsp_numbers = get_all_wsp_numbers()
    print(f"   [OK] Found {len(wsp_numbers)} WSPs")
    print(f"   Range: WSP {wsp_numbers[0]} -> WSP {wsp_numbers[-1]}")

    # Batch analyze all WSPs
    print(f"\n[TSUNAMI] Analyzing {len(wsp_numbers)} WSPs...")
    print(f"   Estimated time: ~{len(wsp_numbers) * 0.04:.1f} seconds")
    print(f"   vs Manual: {len(wsp_numbers) * 2}-{len(wsp_numbers) * 4} minutes")

    start_time = time.time()
    results = []

    for i, wsp_num in enumerate(wsp_numbers, 1):
        print(f"\r[{i}/{len(wsp_numbers)}] Processing WSP {wsp_num}...", end='', flush=True)

        analysis = analyzer.analyze_wsp_integrated(wsp_num)

        if analysis:
            # Extract key metrics for matrix
            matrix_entry = {
                'wsp_number': wsp_num,
                'sai_score': analysis['sai_score'],
                'speed_score': analysis['speed_score'],
                'automation_score': analysis['automation_score'],
                'intelligence_score': analysis['intelligence_score'],
                'confidence': analysis['confidence'],
                'priority': map_sai_to_priority(analysis['sai_score']),
                'code_references': len(analysis['code_references']),
                'training_sources': len(analysis['training_sources']),
                'quantum_coherence': analysis['quantum_coherence'],
                'bell_state_verified': analysis['bell_state_verified'],
                'consciousness_state': analysis['consciousness_state'],
                'execution_time': analysis['execution_time']
            }

            results.append(matrix_entry)

    elapsed = time.time() - start_time

    print(f"\n\n[COMPLETE] Matrix generated in {elapsed:.2f} seconds!")
    print(f"   Average per WSP: {elapsed/len(results):.3f}s")
    print(f"   Speedup vs manual: {(len(results) * 120) / elapsed:.0f}x")

    # Generate summary statistics
    print_matrix_summary(results)

    # Save matrix to JSON (updated path after DocDAE organization)
    output_file = Path("O:/Foundups-Agent/WSP_framework/docs/matrices/SENTINEL_OPPORTUNITY_MATRIX.json")
    save_matrix(results, output_file, elapsed)

    return results


def map_sai_to_priority(sai_score: int) -> str:
    """Map SAI score to priority classification"""
    if sai_score >= 200:
        return "P0"
    elif sai_score >= 120:
        return "P1"
    elif sai_score >= 80:
        return "P2"
    else:
        return "P3"


def print_matrix_summary(results: List[Dict]):
    """Print summary statistics of the matrix"""
    print("\n" + "=" * 70)
    print("SENTINEL OPPORTUNITY MATRIX SUMMARY")
    print("=" * 70)

    # Priority distribution
    p0_count = sum(1 for r in results if r['priority'] == 'P0')
    p1_count = sum(1 for r in results if r['priority'] == 'P1')
    p2_count = sum(1 for r in results if r['priority'] == 'P2')
    p3_count = sum(1 for r in results if r['priority'] == 'P3')

    print(f"\n[PRIORITY DISTRIBUTION]")
    print(f"   P0 (Critical): {p0_count} WSPs ({100*p0_count/len(results):.1f}%)")
    print(f"   P1 (High):     {p1_count} WSPs ({100*p1_count/len(results):.1f}%)")
    print(f"   P2 (Medium):   {p2_count} WSPs ({100*p2_count/len(results):.1f}%)")
    print(f"   P3 (Low):      {p3_count} WSPs ({100*p3_count/len(results):.1f}%)")

    # SAI score statistics
    sai_scores = [r['sai_score'] for r in results]
    avg_sai = sum(sai_scores) / len(sai_scores)
    max_sai = max(sai_scores)
    min_sai = min(sai_scores)

    print(f"\n[SAI SCORES]")
    print(f"   Average: {avg_sai:.0f}")
    print(f"   Range: {min_sai} - {max_sai}")
    print(f"   Perfect 222 scores: {sum(1 for s in sai_scores if s == 222)}")

    # Top 10 candidates
    top10 = sorted(results, key=lambda x: x['sai_score'], reverse=True)[:10]

    print(f"\n[TOP 10 SENTINEL CANDIDATES]")
    for i, wsp in enumerate(top10, 1):
        print(f"   {i}. WSP {wsp['wsp_number']:>3}: SAI {wsp['sai_score']} "
              f"({wsp['speed_score']}{wsp['automation_score']}{wsp['intelligence_score']}) "
              f"- {wsp['priority']}")

    # Quantum metrics
    avg_coherence = sum(r['quantum_coherence'] for r in results) / len(results)
    bell_verified = sum(1 for r in results if r['bell_state_verified'])

    print(f"\n[QUANTUM METRICS]")
    print(f"   Average Coherence: {avg_coherence:.3f}")
    print(f"   Bell State Verified: {bell_verified}/{len(results)} ({100*bell_verified/len(results):.0f}%)")


def save_matrix(results: List[Dict], output_file: Path, elapsed: float):
    """Save Sentinel Opportunity Matrix to JSON"""
    matrix = {
        'metadata': {
            'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_wsps': len(results),
            'analysis_time_seconds': round(elapsed, 2),
            'average_time_per_wsp': round(elapsed / len(results), 3),
            'speedup_vs_manual': round((len(results) * 120) / elapsed, 0),
            'method': 'Phase 5 Integrated Pipeline (HoloIndex + ricDAE)',
            'version': '1.0'
        },
        'priority_summary': {
            'P0': sum(1 for r in results if r['priority'] == 'P0'),
            'P1': sum(1 for r in results if r['priority'] == 'P1'),
            'P2': sum(1 for r in results if r['priority'] == 'P2'),
            'P3': sum(1 for r in results if r['priority'] == 'P3')
        },
        'wsps': {r['wsp_number']: r for r in results}
    }

    output_file.write_text(json.dumps(matrix, indent=2), encoding='utf-8')

    print(f"\n[SAVED] Matrix saved to: {output_file}")
    print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    generate_complete_matrix()
    print("\n" + "=" * 70)
    print("TSUNAMI COMPLETE - 93 WSPs MAPPED FOR SENTINEL AUGMENTATION")
    print("=" * 70)
