# -*- coding: utf-8 -*-
"""
HoloIndex CLI Adaptive Pipeline Module - WSP 75 Compliant Token-Based Development

Handles optional adaptive learning processing.
Returns structured output for throttler integration.

WSP Compliance: WSP 75 (Token-Based Development), WSP 84 (Enhance Existing)
"""

import logging
from typing import Dict, Any, Optional


def run_adaptive_pipeline(holo, args, results, throttler, adaptive_orchestrator=None) -> Dict[str, Any]:
    """
    Run adaptive learning pipeline if enabled.

    Args:
        holo: HoloIndex instance
        args: Parsed CLI arguments
        results: Search results
        throttler: AgenticOutputThrottler instance
        adaptive_orchestrator: Optional AdaptiveLearningOrchestrator instance

    Returns:
        Dict with adaptive results and metadata
    """
    if not adaptive_orchestrator or not getattr(args, 'adaptive', False):
        return {'enabled': False}

    try:
        throttler.add_section('system', '[INFO] Phase 3: Processing with adaptive learning...', priority=5, tags=['system', 'phase3'])

        # Convert search results to the format expected by adaptive learning
        raw_results = []
        for hit in results.get('code', []):
            raw_results.append({
                'content': hit.get('content', ''),
                'score': hit.get('score', 0.5),
                'metadata': hit
            })

        # Generate a basic advisor response for adaptive processing
        raw_response = "Based on the search results, here are the most relevant findings for your query."
        if results.get('wsps'):
            raw_response += f" Found {len(results['wsps'])} WSP protocol references."

        # Process through adaptive learning system (with timeout to prevent hangs)
        import asyncio
        try:
            adaptive_result = asyncio.run(asyncio.wait_for(
                adaptive_orchestrator.process_adaptive_request(
                    query=args.search,
                    raw_results=raw_results,
                    raw_response=raw_response,
                    context={
                        'search_limit': args.limit,
                        'advisor_enabled': True,
                        'wsp_results_count': len(results.get('wsps', [])),
                        'code_results_count': len(results.get('code', []))
                    }
                ),
                timeout=10.0  # 10 second timeout to prevent hangs
            ))
        except asyncio.TimeoutError:
            throttler.add_section('system', '[WARN] Adaptive learning timed out - using basic processing', priority=7, tags=['system', 'warning'])
            adaptive_result = None

        # Add adaptive learning results to search results (if available)
        if adaptive_result:
            results['adaptive_learning'] = {
                'query_optimization_score': adaptive_result.query_processing.optimization_score,
                'search_ranking_stability': adaptive_result.search_optimization.performance_metrics.get('ranking_stability', 0.0),
                'response_improvement_score': adaptive_result.response_optimization.quality_metrics.get('improvement_score', 0.0),
                'memory_efficiency': adaptive_result.memory_optimization.memory_efficiency,
                'system_adaptation_score': adaptive_result.overall_performance.get('system_adaptation_score', 0.0),
                'processing_time': adaptive_result.processing_metadata.get('total_processing_time', 0),
                'enhanced_query': adaptive_result.query_processing.enhanced_query,
                'optimized_response': adaptive_result.response_optimization.optimized_response
            }

            throttler.add_section('adaptive', f'[RECURSIVE] Query enhanced: "{args.search}" -> "{adaptive_result.query_processing.enhanced_query}"', priority=4, tags=['learning', 'optimization'])
            throttler.add_section('adaptive', f'[TARGET] Adaptation Score: {adaptive_result.overall_performance.get("system_adaptation_score", 0.0):.2f}', priority=6, tags=['learning', 'metrics'])

            # Add adaptive learning summary (WSP 87 - prevent noisy output)
            throttler.add_section('adaptive', f'[DEBUG] CODE INDEX: {adaptive_result.query_processing.get("optimization_score", 0.0):.2f} optimization score', priority=7, tags=['debug', 'adaptive'])
            throttler.add_section('adaptive', f'[DEBUG] CODE INDEX: Memory efficiency: {adaptive_result.memory_optimization.get("memory_efficiency", 0.0):.2f}', priority=7, tags=['debug', 'adaptive'])

            return {
                'enabled': True,
                'result': adaptive_result,
                'enhanced_query': adaptive_result.query_processing.enhanced_query,
                'optimized_response': adaptive_result.response_optimization.optimized_response
            }
        else:
            # Fallback when adaptive learning times out
            results['adaptive_learning'] = {
                'status': 'timeout',
                'fallback_processing': True
            }

            return {'enabled': True, 'status': 'timeout'}

    except Exception as e:
        throttler.add_section('system', f'[WARN] Adaptive learning failed: {e}', priority=7, tags=['system', 'warning'])
        logging.exception("Adaptive learning failed")
        return {'enabled': True, 'error': str(e)}
