# -*- coding: utf-8 -*-
"""
HoloIndex CLI Holo Request Module - WSP 77 Compliant Agent Coordination

Handles Qwen/Holo orchestration and search request processing.
Returns structured output for throttler integration.

WSP Compliance: WSP 77 (Agent Coordination), WSP 87 (Size Limits)
"""

import logging
from typing import Dict, Any, Optional


def run_holo_request(holo, args, advisor=None) -> Dict[str, Any]:
    """
    Run HoloIndex search request with optional Qwen orchestration.

    Args:
        holo: HoloIndex instance
        args: Parsed CLI arguments
        advisor: Optional QwenAdvisor instance

    Returns:
        Dict with 'results', 'orchestrated_response', 'metadata'
    """
    results = None
    orchestrated_response = None
    metadata = {}

    # QWEN ROUTING: Route through orchestrator for intelligent filtering if available
    qwen_orchestrator = None
    try:
        from .qwen_advisor.orchestration.qwen_orchestrator import QwenOrchestrator
        qwen_orchestrator = QwenOrchestrator()
        results = holo.search(args.search, limit=args.limit, doc_type_filter=args.doc_type)

        # Route through QWEN orchestrator for intelligent output filtering
        orchestrated_response = qwen_orchestrator.orchestrate_holoindex_request(args.search, results)

        metadata['orchestrator_used'] = True

    except Exception as e:
        # Fallback to direct search if QWEN not available
        logging.debug(f"QWEN orchestrator not available, using direct search: {e}")
        results = holo.search(args.search, limit=args.limit, doc_type_filter=args.doc_type)

        metadata['orchestrator_used'] = False
        metadata['orchestrator_error'] = str(e)

    return {
        'results': results,
        'orchestrated_response': orchestrated_response,
        'metadata': metadata
    }
