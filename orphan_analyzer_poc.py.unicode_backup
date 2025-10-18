#!/usr/bin/env python3
"""Orphan Analyzer POC - Rule-Based Analysis for Qwen/Gemma Training

This POC demonstrates the analysis pattern that Qwen/Gemma will follow via MCP.
Uses rule-based heuristics to categorize orphaned modules.

WSP Compliance: WSP 93 (CodeIndex), WSP 87 (Code Navigation)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class OrphanAnalyzerPOC:
    """POC analyzer using heuristics (template for Qwen/Gemma MCP)."""

    def __init__(self):
        """Initialize analyzer."""
        self.results = []

    def analyze_orphan(self, orphan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze single orphan using rule-based heuristics."""

        # Extract features
        filename = orphan['filename']
        relative_path = orphan['relative_path']
        is_archived = orphan['is_archived']
        is_script = orphan['is_script']
        looks_like_dae = orphan['looks_like_dae']
        in_src = orphan['in_src']
        imports = orphan.get('imports', [])
        docstring = orphan.get('docstring', '')
        domain = orphan.get('domain', '')
        module = orphan.get('module', '')

        # Rule-based categorization
        category, reason, priority, effort = self._categorize(
            filename, relative_path, is_archived, is_script,
            looks_like_dae, in_src, imports, docstring, domain, module
        )

        # Determine purpose from filename and imports
        purpose = self._infer_purpose(filename, imports, docstring)

        # Check if likely part of cluster
        cluster_likely = self._check_cluster_membership(imports, relative_path)

        return {
            'orphan_id': orphan['orphan_id'],
            'filename': filename,
            'relative_path': relative_path,
            'domain': domain,
            'module': module,
            'category': category,
            'purpose': purpose,
            'priority': priority,
            'effort_hours': effort,
            'recommendation': reason,
            'cluster_likely': cluster_likely,
            'import_count': len(imports),
            'key_imports': imports[:5]
        }

    def _categorize(self, filename, path, archived, is_script, is_dae,
                   in_src, imports, docstring, domain, module):
        """Categorize orphan using heuristics."""

        # RULE 1: Already archived → ARCHIVE
        if archived or '_archive' in path:
            return 'ARCHIVE', 'Already in _archive folder - confirmed archival', 'P3', 0

        # RULE 2: Test files → ARCHIVE (they shouldn't be in production anyway)
        if 'test' in filename.lower() or 'test' in path.lower():
            return 'ARCHIVE', 'Test file - not part of production execution', 'P3', 0

        # RULE 3: Scripts folder → STANDALONE or DELETE
        if is_script:
            if 'run_' in filename or 'setup_' in filename:
                return 'STANDALONE', 'Standalone script - check if still needed', 'P2', 2
            else:
                return 'DELETE', 'Utility script likely superseded by main.py', 'P3', 0

        # RULE 4: Looks like DAE → STANDALONE (potential new entry point)
        if is_dae:
            return 'STANDALONE', 'Appears to be DAE entry point - evaluate for main.py integration', 'P1', 8

        # RULE 5: In src/ folder → INTEGRATE (should be imported by module)
        if in_src:
            # Check module domain for priority
            if domain in ['communication', 'platform_integration']:
                priority = 'P0'
                effort = 4
                reason = f'Core {domain} functionality - likely needed by active code'
            elif domain in ['ai_intelligence', 'infrastructure']:
                priority = 'P1'
                effort = 6
                reason = f'{domain.replace("_", " ").title()} module - evaluate integration'
            else:
                priority = 'P2'
                effort = 4
                reason = 'Module component - check if imported by active files'

            return 'INTEGRATE', reason, priority, effort

        # RULE 6: Has many imports → INTEGRATE or STANDALONE
        if len(imports) > 5:
            return 'INTEGRATE', 'Complex module with dependencies - likely functional', 'P1', 8

        # RULE 7: Experimental or POC keywords → ARCHIVE
        experimental_keywords = ['experiment', 'poc', 'demo', 'test', 'temp', 'old', 'backup']
        if any(kw in filename.lower() or kw in path.lower() for kw in experimental_keywords):
            return 'ARCHIVE', 'Experimental/POC code - archive for reference', 'P3', 0

        # RULE 8: Duplicate pattern (v2, _old, _new, _fixed) → DELETE
        duplicate_patterns = ['_v2', '_old', '_new', '_fixed', '_backup', '_copy']
        if any(pattern in filename.lower() for pattern in duplicate_patterns):
            return 'DELETE', 'Appears to be duplicate/old version - verify and delete', 'P2', 1

        # RULE 9: Core functionality keywords → INTEGRATE
        core_keywords = ['handler', 'processor', 'manager', 'engine', 'controller', 'service']
        if any(kw in filename.lower() for kw in core_keywords):
            return 'INTEGRATE', 'Core functionality module - check integration points', 'P1', 6

        # DEFAULT: Archive for manual review
        return 'ARCHIVE', 'Unclear purpose - archive and review manually', 'P2', 2

    def _infer_purpose(self, filename, imports, docstring):
        """Infer module purpose from filename, imports, and docstring."""

        # Extract from docstring if available
        if docstring and len(docstring) > 10 and 'parse error' not in docstring.lower():
            # Take first sentence
            first_sentence = docstring.split('.')[0].strip()
            if first_sentence:
                return first_sentence[:100]

        # Infer from filename
        name = filename.replace('.py', '').replace('_', ' ')

        # Check for common patterns
        if 'handler' in name:
            return f'Handles {name.replace("handler", "").strip()} operations'
        elif 'processor' in name:
            return f'Processes {name.replace("processor", "").strip()} data'
        elif 'manager' in name:
            return f'Manages {name.replace("manager", "").strip()} resources'
        elif 'engine' in name:
            return f'Engine for {name.replace("engine", "").strip()} functionality'
        elif 'orchestrator' in name:
            return f'Orchestrates {name.replace("orchestrator", "").strip()} workflow'

        # Infer from imports
        if any('youtube' in imp.lower() for imp in imports):
            return f'YouTube-related functionality: {name}'
        elif any('linkedin' in imp.lower() for imp in imports):
            return f'LinkedIn integration: {name}'
        elif any('twitter' in imp.lower() or 'x_' in imp for imp in imports):
            return f'Twitter/X functionality: {name}'

        return f'Module: {name}'

    def _check_cluster_membership(self, imports, path):
        """Check if orphan likely belongs to cluster."""

        # Known cluster indicators
        cluster_indicators = [
            'ai_router', 'personality_core', 'prompt_engine',  # AI Router Cluster
            'conversation_manager', 'personality_engine', 'learning_engine',  # 0102 Cluster
            'gemma_adaptive', 'holodae_gemma',  # Gemma Cluster
        ]

        # Check imports
        for imp in imports:
            if any(indicator in imp.lower() for indicator in cluster_indicators):
                return True

        # Check path
        if any(indicator in path.lower() for indicator in cluster_indicators):
            return True

        return False

    def analyze_batch(self, batch_file: Path) -> List[Dict[str, Any]]:
        """Analyze batch of orphans."""

        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)

        orphans = batch_data['orphans']
        batch_id = batch_data['batch_id']

        print(f'\n=== ORPHAN ANALYSIS POC - BATCH {batch_id} ===')
        print(f'Orphans to analyze: {len(orphans)}')
        print(f'Method: Rule-based heuristics (template for Qwen/Gemma MCP)')
        print()

        results = []

        for i, orphan in enumerate(orphans, 1):
            print(f'[{i}/{len(orphans)}] {orphan["filename"]}')

            analysis = self.analyze_orphan(orphan)
            results.append(analysis)

            # Show result
            print(f'  -> {analysis["category"]} ({analysis["priority"]}): {analysis["purpose"][:60]}')

        return results

    def save_results(self, results: List[Dict[str, Any]], output_file: Path):
        """Save analysis results."""

        # Category breakdown
        categories = {}
        for result in results:
            cat = result['category']
            categories[cat] = categories.get(cat, 0) + 1

        output = {
            'analysis_timestamp': datetime.now().isoformat(),
            'analyzer': 'Rule-Based POC (template for Qwen/Gemma)',
            'total_analyzed': len(results),
            'categories': categories,
            'priority_breakdown': {
                'P0': len([r for r in results if r['priority'] == 'P0']),
                'P1': len([r for r in results if r['priority'] == 'P1']),
                'P2': len([r for r in results if r['priority'] == 'P2']),
                'P3': len([r for r in results if r['priority'] == 'P3'])
            },
            'cluster_candidates': len([r for r in results if r['cluster_likely']]),
            'results': results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f'\nResults saved: {output_file}')
        print(f'\nCategory Breakdown:')
        for cat, count in categories.items():
            print(f'  {cat}: {count}')

        print(f'\nPriority Breakdown:')
        for pri, count in output['priority_breakdown'].items():
            print(f'  {pri}: {count}')

        print(f'\nCluster Candidates: {output["cluster_candidates"]}')


def main():
    """Execute analysis."""
    analyzer = OrphanAnalyzerPOC()

    batch_file = Path('docs/qwen_batch_1_input.json')

    if not batch_file.exists():
        print(f'ERROR: Batch file not found: {batch_file}')
        return

    # Analyze batch
    results = analyzer.analyze_batch(batch_file)

    # Save results
    output_file = Path('docs/orphan_analysis_batch_1_poc.json')
    analyzer.save_results(results, output_file)

    print('\n=== ANALYSIS COMPLETE ===')
    print('This POC demonstrates the pattern for Qwen/Gemma MCP integration')
    print('Next: Deploy actual Qwen (1.5B) + Gemma (270M) via MCP for real analysis')


if __name__ == '__main__':
    main()
