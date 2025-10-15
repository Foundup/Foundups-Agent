#!/usr/bin/env python3
"""Qwen Orphan Analyzer - Batch Analysis of Orphaned Modules

This script uses Qwen (1.5B model) to analyze orphaned Python modules and categorize them.

WSP Compliance: WSP 93 (CodeIndex), WSP 87 (Code Navigation), WSP 50 (Pre-Action Verification)
"""

import json
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add holo_index to path
sys.path.insert(0, str(Path(__file__).parent / 'holo_index'))

from qwen_advisor.llm_engine import QwenInferenceEngine


class QwenOrphanAnalyzer:
    """Analyzes orphaned modules using Qwen 1.5B model."""

    def __init__(self):
        """Initialize Qwen analyzer."""
        self.llm = QwenInferenceEngine()
        self.analysis_results = []

    async def analyze_orphan(self, orphan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single orphan module.

        Args:
            orphan: Orphan metadata including path, imports, docstring

        Returns:
            Analysis result with categorization and recommendations
        """
        # Build analysis prompt for Qwen
        prompt = self._build_analysis_prompt(orphan)

        # Get Qwen's analysis
        try:
            response = await self.llm.generate_async(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3  # Low temperature for consistent categorization
            )

            # Parse Qwen's response
            analysis = self._parse_qwen_response(response, orphan)

            return analysis

        except Exception as e:
            return {
                'orphan_id': orphan['orphan_id'],
                'filename': orphan['filename'],
                'error': str(e),
                'category': 'ERROR',
                'recommendation': 'Manual review required - Qwen analysis failed'
            }

    def _build_analysis_prompt(self, orphan: Dict[str, Any]) -> str:
        """Build analysis prompt for Qwen."""

        prompt = f"""Analyze this orphaned Python module and categorize it.

FILE: {orphan['relative_path']}
DOMAIN: {orphan['domain']}/{orphan['module']}
SIZE: {orphan['file_size']} bytes
LOCATION: {"src/" if orphan['in_src'] else "root"} {"(archived)" if orphan['is_archived'] else ""}
IS_SCRIPT: {orphan['is_script']}
LOOKS_LIKE_DAE: {orphan['looks_like_dae']}

IMPORTS ({len(orphan['imports'])} modules):
{', '.join(orphan['imports'][:10]) if orphan['imports'] else 'None'}

DOCSTRING:
{orphan['docstring']}

PREVIEW (first 500 chars):
{orphan.get('content_preview', 'No preview')}

TASK: Categorize this orphan into ONE category:
1. INTEGRATE - Should be imported by active code (fills functionality gap)
2. ARCHIVE - Experimental/POC code worth keeping for reference
3. DELETE - Broken, duplicate, or deprecated code with no value
4. STANDALONE - Complete script that should be its own entry point

ALSO PROVIDE:
- Purpose: What does this code do? (1 sentence)
- Priority: P0 (critical), P1 (high), P2 (medium), P3 (low)
- Effort: Hours to integrate (if INTEGRATE) or 0 (if not)
- Reason: Why this categorization? (1-2 sentences)

OUTPUT FORMAT (JSON):
{{
  "category": "INTEGRATE|ARCHIVE|DELETE|STANDALONE",
  "purpose": "Brief description",
  "priority": "P0|P1|P2|P3",
  "effort_hours": 0-40,
  "recommendation": "Why this decision",
  "cluster_likely": true|false
}}

RESPOND WITH ONLY THE JSON:"""

        return prompt

    def _parse_qwen_response(self, response: str, orphan: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Qwen's JSON response."""
        try:
            # Extract JSON from response (Qwen might include extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                # Fallback parsing
                analysis = {
                    'category': 'ARCHIVE',
                    'purpose': 'Parse error - needs manual review',
                    'priority': 'P3',
                    'effort_hours': 0,
                    'recommendation': 'Qwen response could not be parsed',
                    'cluster_likely': False
                }

            # Add orphan metadata
            analysis.update({
                'orphan_id': orphan['orphan_id'],
                'filename': orphan['filename'],
                'relative_path': orphan['relative_path'],
                'domain': orphan['domain'],
                'module': orphan['module'],
                'qwen_raw_response': response[:200]  # Keep first 200 chars for debugging
            })

            return analysis

        except Exception as e:
            return {
                'orphan_id': orphan['orphan_id'],
                'filename': orphan['filename'],
                'relative_path': orphan['relative_path'],
                'error': f'Parse error: {str(e)}',
                'category': 'ERROR',
                'qwen_raw_response': response[:200]
            }

    async def analyze_batch(self, batch_file: Path) -> List[Dict[str, Any]]:
        """Analyze a batch of orphans.

        Args:
            batch_file: Path to JSON file with batch data

        Returns:
            List of analysis results
        """
        # Load batch
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)

        orphans = batch_data['orphans']
        batch_id = batch_data['batch_id']

        print(f'\n=== QWEN BATCH {batch_id} ANALYSIS ===')
        print(f'Orphans to analyze: {len(orphans)}')
        print()

        results = []

        for i, orphan in enumerate(orphans, 1):
            print(f'[{i}/{len(orphans)}] Analyzing: {orphan["filename"]}')

            # Analyze orphan
            analysis = await self.analyze_orphan(orphan)
            results.append(analysis)

            # Show result
            category = analysis.get('category', 'ERROR')
            purpose = analysis.get('purpose', 'Unknown')
            print(f'  -> {category}: {purpose[:60]}')

            # Small delay to avoid overwhelming Qwen
            await asyncio.sleep(0.5)

        return results

    async def save_results(self, results: List[Dict[str, Any]], output_file: Path):
        """Save analysis results to JSON."""
        output = {
            'analysis_timestamp': datetime.now().isoformat(),
            'analyzer': 'Qwen 1.5B',
            'total_analyzed': len(results),
            'categories': {
                'INTEGRATE': len([r for r in results if r.get('category') == 'INTEGRATE']),
                'ARCHIVE': len([r for r in results if r.get('category') == 'ARCHIVE']),
                'DELETE': len([r for r in results if r.get('category') == 'DELETE']),
                'STANDALONE': len([r for r in results if r.get('category') == 'STANDALONE']),
                'ERROR': len([r for r in results if r.get('category') == 'ERROR'])
            },
            'results': results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f'\nResults saved to: {output_file}')
        print(f'\nCategory Breakdown:')
        for cat, count in output['categories'].items():
            print(f'  {cat}: {count}')


async def main():
    """Main execution."""
    analyzer = QwenOrphanAnalyzer()

    # Analyze batch 1
    batch_file = Path('docs/qwen_batch_1_input.json')

    if not batch_file.exists():
        print(f'ERROR: Batch file not found: {batch_file}')
        return

    # Run analysis
    results = await analyzer.analyze_batch(batch_file)

    # Save results
    output_file = Path('docs/qwen_batch_1_output.json')
    await analyzer.save_results(results, output_file)

    print('\n=== QWEN BATCH 1 ANALYSIS COMPLETE ===')


if __name__ == '__main__':
    asyncio.run(main())
