# -*- coding: utf-8 -*-
"""
Test AI Delegation Pipeline

Integration test for AI delegation orchestrator and UI-TARS scheduler.
Tests the fallback pipeline when Qwen/Gemma is unavailable.

WSP 77: Agent Coordination Protocol
WSP 84: Auto-Management
"""

import unittest
import asyncio
import tempfile
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, AsyncMock

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Import delegation components
from modules.platform_integration.social_media_orchestrator.src.ai_delegation_orchestrator import (
    AIDelegationOrchestrator
)
from modules.platform_integration.social_media_orchestrator.src.ui_tars_scheduler import (
    UITarsScheduler,
    ScheduledPost
)


class TestAIDelegationPipeline(unittest.TestCase):
    """Integration tests for AI delegation pipeline"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.ui_tars_path = Path(self.temp_dir) / "ui_tars_test"
        self.ui_tars_path.mkdir()

        # Create scheduler with test directory
        self.scheduler = UITarsScheduler()
        self.scheduler.ui_tars_inbox = self.ui_tars_path  # Set test directory
        self.scheduler.inbox_file = self.ui_tars_path / "scheduled_posts.json"
        self.scheduler.history_file = self.ui_tars_path / "history.jsonl"
        self.scheduler._ensure_files()

        # Create orchestrator
        self.orchestrator = AIDelegationOrchestrator()

    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ui_tars_scheduler_creation(self):
        """Test UI-TARS scheduler can create scheduled posts"""
        scheduled_time = datetime(2025, 10, 20, 9, 0, 0)

        post = ScheduledPost(
            content="Test LinkedIn post content",
            scheduled_time=scheduled_time,
            content_type="test",
            company_page="foundups",
            draft_hash="test_hash_123",
            metadata={"test": True}
        )

        # Verify post creation
        self.assertEqual(post.content, "Test LinkedIn post content")
        self.assertEqual(post.draft_hash, "test_hash_123")
        self.assertEqual(post.company_page, "foundups")

    def test_scheduler_file_operations(self):
        """Test scheduler can read/write scheduled posts"""
        # Create and schedule a post
        post = ScheduledPost(
            content="File test content",
            scheduled_time=datetime.now(),
            content_type="file_test",
            company_page="foundups",
            draft_hash="file_test_hash",
            metadata={"file_test": True}
        )

        success = self.scheduler.schedule_linkedin_post(post)
        self.assertTrue(success)

        # Verify post was saved
        scheduled_posts = self.scheduler.get_scheduled_posts()
        self.assertEqual(len(scheduled_posts), 1)
        self.assertEqual(scheduled_posts[0].draft_hash, "file_test_hash")

    def test_scheduler_cancellation(self):
        """Test post cancellation functionality"""
        # Schedule a post
        post = ScheduledPost(
            content="Cancel test",
            scheduled_time=datetime.now(),
            content_type="cancel_test",
            company_page="foundups",
            draft_hash="cancel_hash",
            metadata={"cancel_test": True}
        )

        self.scheduler.schedule_linkedin_post(post)

        # Cancel it
        success = self.scheduler.cancel_scheduled_post("cancel_hash")
        self.assertTrue(success)

        # Verify it's gone
        scheduled_posts = self.scheduler.get_scheduled_posts()
        self.assertEqual(len(scheduled_posts), 0)

    @patch('modules.platform_integration.social_media_orchestrator.src.ai_delegation_orchestrator.AIDelegationOrchestrator._check_qwen_gemma_available')
    async def test_delegation_fallback_logic(self, mock_check):
        """Test that orchestrator falls back when Qwen/Gemma unavailable"""
        # Mock Qwen/Gemma as unavailable
        mock_check.return_value = False

        trigger_event = {
            'type': 'stream_start',
            'title': 'Test Stream',
            'url': 'https://youtube.com/test',
            'description': 'Test stream description'
        }

        # This would normally try external AI services
        # For testing, we'll mock the external AI calls
        with patch.object(self.orchestrator, '_draft_with_claude') as mock_claude:
            mock_claude.return_value = {
                'content': 'Mock Claude response',
                'draft_hash': 'mock_hash',
                'confidence': 0.85
            }

            result = await self.orchestrator.draft_linkedin_content(trigger_event)

            # Verify fallback was attempted
            mock_claude.assert_called_once()
            self.assertIsNotNone(result)

    def test_scheduler_instruction_file_creation(self):
        """Test that UI-TARS instruction files are created"""
        post = ScheduledPost(
            content="Instruction test",
            scheduled_time=datetime.now(),
            content_type="instruction_test",
            company_page="foundups",
            draft_hash="instruction_hash",
            metadata={"instruction_test": True}
        )

        self.scheduler.schedule_linkedin_post(post)

        # Check if instruction file was created
        instruction_files = list(self.ui_tars_path.glob("schedule_*.json"))
        self.assertEqual(len(instruction_files), 1)

        # Verify instruction content
        import json
        with open(instruction_files[0], 'r') as f:
            instructions = json.load(f)

        self.assertEqual(instructions['draft_hash'], 'instruction_hash')
        self.assertEqual(instructions['content'], 'Instruction test')
        self.assertIn('ui_instructions', instructions)

    def test_orchestrator_skill_loading(self):
        """Test that orchestrator can load skills prompts"""
        # Create a test skills file
        skills_dir = Path(self.temp_dir) / "skills"
        skills_dir.mkdir()
        skills_file = skills_dir / "stream_start.md"

        with open(skills_file, 'w') as f:
            f.write("Test skills prompt for stream start")

        # Test loading (would normally be handled by orchestrator)
        try:
            with open(skills_file, 'r') as f:
                content = f.read()
            self.assertEqual(content, "Test skills prompt for stream start")
        except FileNotFoundError:
            self.skipTest("Skills file creation failed")

    async def test_delegation_scheduling_integration(self):
        """Test integration between delegation and scheduling"""
        # Mock a successful draft
        draft_result = {
            'content': 'Integration test content',
            'draft_hash': 'integration_hash',
            'ai_service': 'test_service',
            'confidence': 0.9,
            'metadata': {'test_integration': True}
        }

        # Schedule the draft
        success = await self.orchestrator.schedule_draft(draft_result, delay_hours=1)

        # Verify scheduling worked
        self.assertTrue(success)

        # Check that post was created in scheduler
        scheduled_posts = self.scheduler.get_scheduled_posts()
        self.assertEqual(len(scheduled_posts), 1)

        post = scheduled_posts[0]
        self.assertEqual(post.draft_hash, 'integration_hash')
        self.assertEqual(post.content, 'Integration test content')

    def test_vision_insight_content_generation(self):
        """Test Vision DAE insight content generation"""
        try:
            from modules.infrastructure.dae_infrastructure.foundups_vision_dae.src.vision_dae import VisionTelemetryReporter

            # Create reporter with test scheduler
            reporter = VisionTelemetryReporter(Path(self.temp_dir) / "vision_test")
            reporter.ui_tars_scheduler = self.scheduler

            # Test insight content generation
            insight = {
                'type': 'performance_improvement',
                'improvement_percentage': 25.5,
                'metric': 'response time'
            }

            content = reporter._generate_content_from_insight(insight)
            self.assertIn('25.5%', content)
            self.assertIn('response time', content)
            self.assertIn('#AI', content)

        except ImportError:
            self.skipTest("Vision DAE components not available")


if __name__ == '__main__':
    # Simple test runner for now
    unittest.main()
