#!/usr/bin/env python3
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

Test HoloDAE Coordinator - Verifies the new modular architecture works correctly

WSP Compliance: WSP 6 (Test Coverage), WSP 80 (DAE Orchestration)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
import tempfile
import io
from contextlib import redirect_stdout
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holo_index.qwen_advisor import HoloDAECoordinator
from holo_index.qwen_advisor.output_formatter import HoloOutputFormatter, TelemetryLogger
from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator


class TestHoloDAECoordinator(unittest.TestCase):
    """Test the new modular HoloDAE Coordinator"""

    def setUp(self):
        """Initialize coordinator for each test"""
        self.coordinator = HoloDAECoordinator()

    def test_coordinator_initialization(self):
        """Test that coordinator initializes with all components"""
        self.assertIsNotNone(self.coordinator.qwen_orchestrator)
        self.assertIsNotNone(self.coordinator.mps_arbitrator)
        self.assertIsNotNone(self.coordinator.file_watcher)
        self.assertIsNotNone(self.coordinator.context_analyzer)
        self.assertFalse(self.coordinator.monitoring_active)

    def test_handle_holoindex_request_basic(self):
        """Test basic HoloIndex request handling"""
        # Mock search results
        sample_results = {
            'code': [{'location': 'test.py', 'content': 'def test(): pass'}],
            'wsps': [{'path': 'WSP_80.md', 'content': 'DAE Orchestration'}]
        }

        # Handle request
        result = self.coordinator.handle_holoindex_request('test query', sample_results)

        # Verify response structure
        self.assertIsInstance(result, str)
        self.assertIn('[HOLODAE-INTELLIGENCE]', result)
        self.assertIn('[0102-ARBITRATION]', result)
        self.assertIn('[EXECUTION]', result)

    def test_monitoring_controls(self):
        """Test monitoring start/stop functionality"""
        # Initially not active
        self.assertFalse(self.coordinator.monitoring_active)

        # Start monitoring (may print to stdout)
        result = self.coordinator.start_monitoring()
        self.assertTrue(result)  # Should return True
        self.assertTrue(self.coordinator.monitoring_active)

        # Stop monitoring
        result = self.coordinator.stop_monitoring()
        self.assertTrue(result)
        self.assertFalse(self.coordinator.monitoring_active)

    def test_get_status_summary(self):
        """Test status summary generation"""
        status = self.coordinator.get_status_summary()

        # Verify required keys exist
        required_keys = ['monitoring_active', 'qwen_status', 'arbitration_status', 'files_watched', 'current_work_context']
        for key in required_keys:
            self.assertIn(key, status)

        # Verify types
        self.assertIsInstance(status['monitoring_active'], bool)
        self.assertIsInstance(status['qwen_status'], dict)
        self.assertIsInstance(status['arbitration_status'], dict)

    def test_qwen_orchestration_integration(self):
        """Test that Qwen orchestrator is properly integrated"""
        # Test with empty results
        result = self.coordinator.handle_holoindex_request('empty query', {'code': [], 'wsps': []})

        # Should still produce a structured response (may be different format for no files)
        self.assertIsInstance(result, str)
        self.assertIn('[HOLODAE-ANALYZE]', result)  # Different message when no files
        self.assertIn('[0102-ARBITRATION]', result)

    def test_arbitration_decision_making(self):
        """Test that MPS arbitration produces decisions"""
        sample_results = {
            'code': [{'location': 'large_file.py', 'content': 'x = 1\n' * 1500}],  # Simulate large file
            'wsps': []
        }

        result = self.coordinator.handle_holoindex_request('large file query', sample_results)

        # Should contain arbitration decisions
        self.assertIn('[0102-ARBITRATION]', result)
        self.assertIn('Arbitration Decisions:', result)


    def test_mcp_activity_logging(self):
        """MCP-enabled modules should register activity in the coordinator log"""
        sample_results = {
            'code': [{'location': 'modules/ai_intelligence/ric_dae/src/__init__.py', 'content': 'from . import *'}],
            'wsps': []
        }

        self.coordinator.handle_holoindex_request('ric_dae mcp query', sample_results)

        self.assertTrue(self.coordinator.mcp_action_log, 'Expected MCP log entries after ricDAE query')
        latest = self.coordinator.mcp_action_log[0]
        self.assertIn('timestamp', latest)
        if latest.get('module'):
            self.assertIn('ric_dae', latest['module'])

    def test_show_mcp_helpers(self):
        """Ensure MCP helper displays render without raising errors"""
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.coordinator.show_mcp_hook_status()
        self.assertIn('MCP Hook Map', buf.getvalue())

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.coordinator.show_mcp_action_log()
        self.assertIn('MCP Action Log', buf.getvalue())


class TestEnhancedFeatures(unittest.TestCase):
    """Test suite for enhanced output and telemetry features"""

    def test_clean_output_formatting(self):
        """Test SUMMARY/TODO/DETAILS structured output"""
        formatter = HoloOutputFormatter(verbose=False)

        module_metrics = {
            'modules/test/module': {
                'display_name': 'modules/test/module',
                'health_label': '[COMPLETE]',
                'size_label': '[CRITICAL] 948 lines',
                'recommendations': ['WSP 62 (Modularity)'],
                'module_alerts': ['Size violation']
            }
        }

        output = formatter.format_analysis(
            query='test query',
            search_results={'code': ['file1.py'], 'wsps': []},
            module_metrics=module_metrics,
            alerts=['Module size violation']
        )

        # Verify structure
        self.assertIn('[SUMMARY]', output)
        self.assertIn('[TODO]', output)
        self.assertIn('Refactor large files (948 lines)', output)

    def test_telemetry_logging_to_jsonl(self):
        """Test JSON telemetry events logged correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TelemetryLogger('test-session')
            logger.log_dir = Path(tmpdir)
            logger.log_dir.mkdir(exist_ok=True)
            logger.log_file = logger.log_dir / 'test.jsonl'

            # Log events
            logger.log_search_request('query', code_hits=5, wsp_hits=2)
            logger.log_module_status(
                module='test/module',
                wsp_clause='WSP 62',
                severity='critical',
                evidence={'lines': 1000},
                next_action='refactor'
            )

            # Verify JSONL format
            with open(logger.log_file, 'r') as f:
                lines = f.readlines()

            self.assertEqual(len(lines), 2)
            event = json.loads(lines[0])
            self.assertEqual(event['event'], 'search_request')

    def test_module_map_orphan_detection(self):
        """Test module map generation and orphan detection"""
        coordinator = HoloDAECoordinator()

        # Test orphan detection logic
        self.assertFalse(coordinator._check_is_imported('fake/module', 'orphan'))
        self.assertFalse(coordinator._check_has_tests('fake/module', 'orphan'))

    def test_doc_tracking_compliance(self):
        """Test document hint and read tracking for compliance"""
        coordinator = HoloDAECoordinator()

        # Track doc read
        coordinator.track_doc_read('test/README.md')
        self.assertIn('test/README.md', coordinator.docs_read)


if __name__ == '__main__':
    unittest.main()
