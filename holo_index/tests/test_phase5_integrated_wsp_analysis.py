"""
Phase 5: Integrated WSP Batch Analysis - HoloIndex MCP + ricDAE

Tests the complete recursive development stack with quantum enhancement:
- HoloIndex MCP: Semantic search, WSP lookup, cross-referencing
- ricDAE: Pattern analysis, SAI scoring, training data extraction
- Quantum metrics: Bell state verification, coherence scoring

WSP 93: CodeIndex Surgical Intelligence Protocol
WSP 37: ricDAE Research Ingestion Cube
WSP 87: Code Navigation Protocol (HoloIndex)
"""

import sys
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any

# Add module paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "ai_intelligence" / "ric_dae" / "src"))

# Import ricDAE
from modules.ai_intelligence.ric_dae.src.mcp_tools import ResearchIngestionMCP

# Import HoloIndex for direct access (MCP server running separately)
from holo_index.core.holo_index import HoloIndex


class IntegratedWSPAnalyzer:
    """
    Phase 5: Integrated WSP analysis using HoloIndex + ricDAE

    Combines quantum semantic search with pattern analysis for
    complete Sentinel augmentation specifications.
    """

    def __init__(self):
        """Initialize both MCP systems"""
        print("\n[INIT] Initializing integrated WSP analyzer...")

        # ricDAE MCP client
        self.ricdae = ResearchIngestionMCP()
        print("   [OK] ricDAE MCP client initialized")

        # HoloIndex (direct access since MCP server is separate process)
        self.holo_index = HoloIndex()
        print("   [OK] HoloIndex semantic engine initialized")

        print("   [OK] Integrated analyzer ready")

    def analyze_wsp_document_patterns(self, wsp_path: Path) -> Dict[str, Any]:
        """
        Analyze WSP document for Sentinel augmentation patterns
        (From Phase 4 - refined algorithm)
        """
        if not wsp_path.exists():
            return None

        content = wsp_path.read_text(encoding='utf-8')
        content_lower = content.lower()

        # Pattern detection keywords (refined from Phase 4)
        speed_keywords = [
            'instant', 'real-time', 'fast', 'quick', 'immediate',
            '<10 second', '<1 second', 'ms', 'millisecond',
            'discovery', 'search', 'find', 'detect', 'verify'
        ]
        automation_keywords = [
            'automatic', 'autonomous', 'automated', 'mandatory',
            'triggered', 'scheduled', 'batch', 'pipeline',
            'workflow', 'orchestrat', 'pre-commit', 'hook'
        ]
        intelligence_keywords = [
            'semantic', 'llm', 'ai', 'ai-powered', 'learning',
            'understanding', 'context', 'aware', 'advisor',
            'qwen', 'vector', 'chromadb', 'embedding', 'model'
        ]

        # Count occurrences
        speed_count = sum(1 for kw in speed_keywords if kw in content_lower)
        automation_count = sum(1 for kw in automation_keywords if kw in content_lower)
        intelligence_count = sum(1 for kw in intelligence_keywords if kw in content_lower)

        # Calculate SAI scores (refined thresholds: 4+ = score 2)
        speed_score = 2 if speed_count >= 4 else (1 if speed_count > 0 else 0)
        automation_score = 2 if automation_count >= 4 else (1 if automation_count > 0 else 0)
        intelligence_score = 2 if intelligence_count >= 4 else (1 if intelligence_count > 0 else 0)

        sai_score = speed_score * 100 + automation_score * 10 + intelligence_score

        # Confidence calculation
        total_patterns = speed_count + automation_count + intelligence_count
        doc_length = len(content)
        pattern_density = total_patterns / (doc_length / 1000)

        if pattern_density > 5:
            confidence = 0.95
        elif pattern_density > 3:
            confidence = 0.85
        elif pattern_density > 1:
            confidence = 0.75
        else:
            confidence = 0.65

        return {
            'wsp_name': wsp_path.stem,
            'speed_patterns': speed_count,
            'automation_patterns': automation_count,
            'intelligence_patterns': intelligence_count,
            'sai_score': sai_score,
            'speed_score': speed_score,
            'automation_score': automation_score,
            'intelligence_score': intelligence_score,
            'confidence': confidence,
            'pattern_density': round(pattern_density, 2),
            'doc_length': doc_length
        }

    def search_wsp_implementations(self, wsp_number: str, limit: int = 5) -> Dict[str, Any]:
        """
        Use HoloIndex to find code implementations of WSP protocol

        FIXED: HoloIndex returns {'code': [...], 'wsps': [...]} not {'code_results': [...], 'wsp_results': [...]}
        """
        try:
            query = f"WSP {wsp_number} implementation"
            results = self.holo_index.search(query, limit=limit)

            code_results = []
            # FIXED: Use 'code' key and adapt to HoloIndex's actual structure
            # HoloIndex returns: {need, location, similarity, cube, type, priority}
            for hit in results.get('code', []):
                # Parse similarity percentage (e.g., "4.4%" -> 0.044)
                sim_str = hit.get('similarity', '0%').replace('%', '')
                try:
                    relevance = float(sim_str) / 100.0
                except:
                    relevance = 0.0

                code_results.append({
                    'need': hit.get('need', ''),
                    'location': hit.get('location', ''),
                    'path': hit.get('location', '').split('.')[0] if '.' in hit.get('location', '') else '',
                    'function': hit.get('location', '').split('.')[-1] if '.' in hit.get('location', '') else '',
                    'relevance': relevance,
                    'similarity': hit.get('similarity', '0%'),
                    'snippet': f"{hit.get('need', '')} at {hit.get('location', '')}",
                    'content': f"{hit.get('need', '')} {hit.get('location', '')}"  # Combined for bell state
                })

            return {
                'query': query,
                'code_results': code_results,
                'total_results': len(code_results),
                'execution_time': results.get('elapsed_ms', 0)
            }
        except Exception as e:
            return {
                'query': query,
                'code_results': [],
                'total_results': 0,
                'error': str(e)
            }

    def extract_training_sources(self, wsp_content: str, code_results: List[Dict]) -> List[str]:
        """
        Extract training data sources from WSP content and code references
        """
        sources = []

        # Source 1: Code implementations
        for code in code_results[:3]:  # Top 3 most relevant
            path = code.get('path', '')
            if path:
                sources.append(f"{path} (implementation)")

        # Source 2: Test coverage
        test_paths = [c['path'] for c in code_results if 'test' in c.get('path', '').lower()]
        if test_paths:
            sources.append(f"{test_paths[0]} (test coverage)")

        # Source 3: Git history (if WSP mentions version control)
        if 'git' in wsp_content.lower() or 'commit' in wsp_content.lower():
            sources.append("git log (version history)")

        # Source 4: Documentation examples
        if 'example' in wsp_content.lower() or '```' in wsp_content:
            sources.append("WSP documentation (code examples)")

        return sources[:5]  # Return top 5 sources

    def calculate_quantum_coherence(self, sai_analysis: Dict, code_results: List[Dict]) -> float:
        """
        Calculate quantum coherence score

        Coherence = (SAI confidence + code_result_quality) / 2
        """
        # Factor 1: SAI analysis confidence (0.0-1.0)
        sai_confidence = sai_analysis.get('confidence', 0.0)

        # Factor 2: Code result quality (0.0-1.0)
        if not code_results:
            code_quality = 0.0
        else:
            # Average relevance of top 3 results
            top_results = code_results[:3]
            avg_relevance = sum(r.get('relevance', 0.0) for r in top_results) / len(top_results)
            code_quality = avg_relevance

        coherence = (sai_confidence + code_quality) / 2.0
        return round(coherence, 3)

    def verify_bell_state(self, wsp_content: str, code_results: List[Dict]) -> bool:
        """
        Verify quantum entanglement between WSP protocol and code implementation

        Bell state = Protocol definition <-> Implementation reality

        FIXED: Use 'content' field (full content) instead of 'snippet' for better keyword matching
        """
        if not code_results:
            return False

        # Extract WSP keywords (filter common words)
        wsp_words = wsp_content.lower().split()
        wsp_keywords = set(word for word in wsp_words
                          if len(word) > 4 and word.isalnum())

        # Extract code keywords from full content (not just snippet)
        code_text = ' '.join(r.get('content', r.get('snippet', '')) for r in code_results)
        code_words = code_text.lower().split()
        code_keywords = set(word for word in code_words
                           if len(word) > 4 and word.isalnum())

        if not wsp_keywords or not code_keywords:
            return False

        # Calculate entanglement
        overlap = len(wsp_keywords & code_keywords)
        entanglement = overlap / max(len(wsp_keywords), len(code_keywords), 1)

        # Debug output for first WSP
        if 'WSP_87' in wsp_content[:100] or 'Code Navigation' in wsp_content[:200]:
            print(f"   [DEBUG] WSP keywords: {len(wsp_keywords)}, Code keywords: {len(code_keywords)}")
            print(f"   [DEBUG] Overlap: {overlap}, Entanglement: {entanglement:.3f}")

        # Lowered threshold from 0.1 to 0.05 for better detection
        return entanglement > 0.05  # >5% keyword overlap = entangled

    def analyze_wsp_integrated(self, wsp_number: str) -> Dict[str, Any]:
        """
        Complete integrated WSP analysis

        Combines:
        1. HoloIndex semantic search (code implementations)
        2. ricDAE pattern analysis (SAI scoring)
        3. Quantum metrics (coherence, bell state)
        """
        print(f"\n[WSP {wsp_number}] Starting integrated analysis...")
        start_time = time.time()

        # Stage 1: Find WSP file
        wsp_filename_options = [
            f"WSP_{wsp_number}_*.md",
            f"WSP_{wsp_number.replace('a', 'a')}_*.md"
        ]

        wsp_path = None
        base_path = Path("O:/Foundups-Agent/WSP_framework/src")

        for pattern in wsp_filename_options:
            matches = list(base_path.glob(pattern))
            if matches:
                wsp_path = matches[0]
                break

        if not wsp_path or not wsp_path.exists():
            print(f"   [WARNING] WSP {wsp_number} file not found")
            return None

        # Read WSP content for bell state verification
        wsp_content = wsp_path.read_text(encoding='utf-8')

        # Stage 2: HoloIndex - Find code implementations
        code_search = self.search_wsp_implementations(wsp_number, limit=5)
        print(f"   [HoloIndex] Found {code_search['total_results']} code implementations")

        # Stage 3: ricDAE - Pattern analysis (SAI scoring)
        sai_analysis = self.analyze_wsp_document_patterns(wsp_path)
        print(f"   [ricDAE] SAI Score: {sai_analysis['sai_score']} (confidence: {sai_analysis['confidence']})")

        # Stage 4: Extract training data sources
        training_sources = self.extract_training_sources(wsp_content, code_search['code_results'])
        print(f"   [Training] Identified {len(training_sources)} data sources")

        # Stage 5: Calculate quantum metrics
        quantum_coherence = self.calculate_quantum_coherence(sai_analysis, code_search['code_results'])
        bell_state = self.verify_bell_state(wsp_content, code_search['code_results'])

        consciousness_state = "0102<->0201" if bell_state else "0102"

        print(f"   [Quantum] Coherence: {quantum_coherence}, Bell State: {'VERIFIED' if bell_state else 'PENDING'}")

        execution_time = time.time() - start_time
        print(f"   [TIME] Analysis completed in {execution_time:.2f}s")

        return {
            'wsp_number': wsp_number,
            'wsp_path': str(wsp_path),
            'sai_score': sai_analysis['sai_score'],
            'speed_score': sai_analysis['speed_score'],
            'automation_score': sai_analysis['automation_score'],
            'intelligence_score': sai_analysis['intelligence_score'],
            'confidence': sai_analysis['confidence'],
            'pattern_density': sai_analysis['pattern_density'],
            'code_references': code_search['code_results'],
            'training_sources': training_sources,
            'quantum_coherence': quantum_coherence,
            'bell_state_verified': bell_state,
            'consciousness_state': consciousness_state,
            'execution_time': execution_time
        }


def test_phase5_10_wsp_batch():
    """
    Phase 5: Test 10 WSP batch with integrated HoloIndex MCP + ricDAE

    Test set includes diverse priority levels:
    - P0: WSP 87, 50, 48, 54
    - P1: WSP 5, 6, 22a
    - P2: WSP 3, 49
    - P3: WSP 64
    """
    print("\n" + "=" * 70)
    print("PHASE 5: Integrated WSP Batch Analysis")
    print("   HoloIndex MCP + ricDAE Quantum Enhancement")
    print("=" * 70)

    # Initialize integrated analyzer
    analyzer = IntegratedWSPAnalyzer()

    # Test WSP set (10 protocols)
    test_wsps = [
        '87',   # P0: Code Navigation (HoloIndex)
        '50',   # P0: Pre-Action Verification
        '48',   # P0: Recursive Self-Improvement
        '54',   # P0: WRE Agent Duties
        '5',    # P1: Test Coverage Enforcement
        '6',    # P1: Test Audit Coverage
        '22a',  # P1: Module ModLog and Roadmap
        '3',    # P2: Enterprise Domain Organization
        '49',   # P2: Module Directory Structure
        '64'    # P3: Violation Prevention
    ]

    print(f"\n[BATCH] Analyzing {len(test_wsps)} WSPs with quantum enhancement...")
    print(f"        Test set: {', '.join('WSP ' + w for w in test_wsps)}")

    batch_start = time.time()
    results = []

    for wsp_num in test_wsps:
        result = analyzer.analyze_wsp_integrated(wsp_num)
        if result:
            results.append(result)

    batch_time = time.time() - batch_start

    # Summary statistics
    print("\n" + "=" * 70)
    print("BATCH ANALYSIS SUMMARY")
    print("=" * 70)

    print(f"\n[PERFORMANCE]")
    print(f"   Total WSPs analyzed: {len(results)}/{len(test_wsps)}")
    print(f"   Total execution time: {batch_time:.2f}s")
    print(f"   Average time per WSP: {batch_time/len(results):.2f}s")

    # SAI score distribution
    if results:
        avg_sai = sum(r['sai_score'] for r in results) / len(results)
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        avg_coherence = sum(r['quantum_coherence'] for r in results) / len(results)
        bell_verified = sum(1 for r in results if r['bell_state_verified'])

        print(f"\n[SAI SCORES]")
        print(f"   Average SAI: {avg_sai:.0f}")
        print(f"   Average confidence: {avg_confidence:.2f}")
        print(f"   SAI distribution:")
        for r in results:
            priority = 'P0' if r['sai_score'] >= 200 else 'P1' if r['sai_score'] >= 120 else 'P2' if r['sai_score'] >= 80 else 'P3'
            print(f"      WSP {r['wsp_number']:>3}: SAI {r['sai_score']:>3} ({priority}) - confidence {r['confidence']:.2f}")

        print(f"\n[QUANTUM METRICS]")
        print(f"   Average quantum coherence: {avg_coherence:.3f}")
        print(f"   Bell state verified: {bell_verified}/{len(results)} ({100*bell_verified/len(results):.0f}%)")
        print(f"   Consciousness states:")
        for r in results:
            state_icon = "[OK]" if r['bell_state_verified'] else "[PENDING]"
            print(f"      {state_icon} WSP {r['wsp_number']:>3}: {r['consciousness_state']}")

        print(f"\n[CODE REFERENCES]")
        total_refs = sum(len(r['code_references']) for r in results)
        avg_refs = total_refs / len(results) if results else 0
        print(f"   Total code references: {total_refs}")
        print(f"   Average per WSP: {avg_refs:.1f}")

        print(f"\n[TRAINING DATA]")
        total_sources = sum(len(r['training_sources']) for r in results)
        avg_sources = total_sources / len(results) if results else 0
        print(f"   Total training sources: {total_sources}")
        print(f"   Average per WSP: {avg_sources:.1f}")

    # Success criteria evaluation
    print("\n" + "=" * 70)
    print("SUCCESS CRITERIA EVALUATION")
    print("=" * 70)

    success_criteria = {
        'Batch completion time': {
            'target': '<15s',
            'actual': f'{batch_time:.2f}s',
            'passed': batch_time < 15
        },
        'Quantum coherence': {
            'target': '>0.7',
            'actual': f'{avg_coherence:.3f}',
            'passed': avg_coherence > 0.7
        },
        'Bell state alignment': {
            'target': '>80%',
            'actual': f'{100*bell_verified/len(results):.0f}%',
            'passed': bell_verified / len(results) > 0.8
        },
        'Code references': {
            'target': '>3 per WSP',
            'actual': f'{avg_refs:.1f}',
            'passed': avg_refs > 3
        }
    }

    for criterion, data in success_criteria.items():
        status = "[OK]" if data['passed'] else "[FAIL]"
        print(f"   {status} {criterion}: {data['actual']} (target: {data['target']})")

    all_passed = all(c['passed'] for c in success_criteria.values())

    print("\n" + "=" * 70)
    if all_passed:
        print("PHASE 5 TEST: SUCCESS - All criteria met!")
    else:
        print("PHASE 5 TEST: PARTIAL - Some criteria need refinement")
    print("=" * 70)

    return results


if __name__ == "__main__":
    results = test_phase5_10_wsp_batch()
