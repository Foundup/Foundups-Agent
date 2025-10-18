#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

Integrate all feed scripts with HoloIndex discovery_feeder
This consolidates feeding mechanisms into the main discovery system
"""

import sys
import os
# Add project root to path so we can import holo_index and tools
# Script is at: modules/infrastructure/feed_integration/scripts/
# Project root is: ../../../../.. (4 levels up from scripts dir)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
sys.path.insert(0, project_root)

from holo_index.adaptive_learning.discovery_feeder import DiscoveryFeeder
from feed_scripts_to_holoindex import create_scripts_discovery
from datetime import datetime

def integrate_all_feeds():
    """Integrate various feed systems into main discovery_feeder"""

    # Initialize the main discovery feeder
    feeder = DiscoveryFeeder()

    print("Integrating feed systems into HoloIndex discovery_feeder...")

    # 1. Feed scripts catalog
    print("\nFeeding scripts catalog...")
    scripts_data = create_scripts_discovery()

    for discovery in scripts_data['discoveries']:
        # Convert to discovery_feeder format
        feed_entry = {
            'title': discovery['title'],
            'query': discovery.get('description', ''),
            'problem_solved': f"Find and use {discovery['title']}",
            'solution_found': discovery.get('location', discovery.get('usage_example', '')),
            'search_keywords': discovery.get('semantic_keywords', []),
            'category': discovery.get('category', 'scripts'),
            'confidence': 0.9,
            'source': 'scripts_catalog'
        }

        if feeder.feed_discovery(feed_entry):
            print(f"  Fed: {discovery['title']}")

    # 2. Feed session logging discoveries (if they exist)
    session_log_path = "modules/communication/livechat/memory/conversation/"
    if os.path.exists(session_log_path):
        print("\nFeeding session logging discoveries...")
        session_discovery = {
            'title': 'Session Logging System',
            'query': 'session logs chat history fact check',
            'problem_solved': 'Access and search chat session history',
            'solution_found': session_log_path,
            'search_keywords': ['session', 'logs', 'chat', 'history', 'fact-check', 'FC'],
            'category': 'livechat',
            'confidence': 0.95,
            'source': 'session_logging'
        }
        feeder.feed_discovery(session_discovery)
        print("  Fed session logging system")

    # 3. Save all discoveries
    feeder.save_all()
    metrics = feeder.get_metrics()

    print("\nIntegration Complete!")
    print(f"  Total discoveries: {metrics.get('total_discoveries', 'unknown')}")
    print(f"  Patterns learned: {metrics.get('patterns_learned', 'unknown')}")
    print(f"  Discovery sources: scripts_catalog, session_logging")

    print("\nBenefits of consolidation:")
    print("  - Single source of truth (discovery_feeder.py)")
    print("  - Unified discovery format")
    print("  - Pattern learning across all feeds")
    print("  - No duplicate feed systems")

    return metrics

if __name__ == "__main__":
    integrate_all_feeds()