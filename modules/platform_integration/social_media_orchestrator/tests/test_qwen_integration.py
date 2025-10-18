#!/usr/bin/env python3
"""
Test script to verify QWEN intelligence integration with social media orchestrator
Tests that the enhanced DuplicatePreventionManager works with refactored orchestrator
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import sys
import os
import json
import logging

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_qwen_integration():
    """Test QWEN intelligence features in DuplicatePreventionManager"""
    logger.info("=" * 60)
    logger.info("[U+1F9EA] TESTING QWEN INTEGRATION")
    logger.info("=" * 60)

    # Import the enhanced module
    from modules.platform_integration.social_media_orchestrator.src.core import (
        DuplicatePreventionManager,
        PostingStatus
    )

    # Create instance with QWEN enabled
    logger.info("\n1️⃣ Creating DuplicatePreventionManager with QWEN enabled...")
    manager = DuplicatePreventionManager(qwen_enabled=True)

    # Verify QWEN is enabled
    assert manager.qwen_enabled, "QWEN should be enabled"
    logger.info("[OK] QWEN intelligence enabled")

    # Test QWEN pre-posting check
    logger.info("\n2️⃣ Testing QWEN pre-posting check...")
    stream_info = {
        'video_id': 'test_video_123',
        'title': 'Test Stream',
        'url': 'https://youtube.com/watch?v=test_video_123',
        'channel_name': 'FoundUps'
    }
    target_platforms = ['linkedin', 'x_twitter']

    decision = manager.qwen_pre_posting_check(stream_info, target_platforms)

    # Verify decision structure
    assert 'qwen_active' in decision, "Decision should indicate QWEN is active"
    assert decision['qwen_active'], "QWEN should be active"
    assert 'should_post' in decision, "Decision should include should_post"
    assert 'approved_platforms' in decision, "Decision should include approved platforms"
    assert 'posting_order' in decision, "Decision should include posting order"
    assert 'delays' in decision, "Decision should include delays"

    logger.info(f"[OK] QWEN decision: {json.dumps(decision, indent=2)}")

    # Test QWEN monitoring
    logger.info("\n3️⃣ Testing QWEN monitoring...")
    post_id = "test_video_123_linkedin"

    # We need to use the PostingStatus from DuplicatePreventionManager which has the extended enum
    from modules.platform_integration.social_media_orchestrator.src.core.duplicate_prevention_manager import PostingStatus as QwenPostingStatus

    # Simulate posting progress
    manager.qwen_monitor_posting_progress(
        post_id, 'linkedin', QwenPostingStatus.IN_PROGRESS,
        {'stream_info': stream_info}
    )
    logger.info("[OK] QWEN monitoring IN_PROGRESS")

    # Simulate success
    manager.qwen_monitor_posting_progress(
        post_id, 'linkedin', QwenPostingStatus.SUCCESS,
        {'result': 'success'}
    )
    logger.info("[OK] QWEN monitoring SUCCESS")

    # Get QWEN report
    logger.info("\n4️⃣ Getting QWEN posting report...")
    report = manager.qwen_get_posting_report()

    assert report['qwen_active'], "Report should show QWEN is active"
    assert 'platform_health' in report, "Report should include platform health"

    logger.info(f"[OK] QWEN report: {json.dumps(report, indent=2)}")

    # Test integration with orchestrator
    logger.info("\n5️⃣ Testing orchestrator integration...")
    from modules.platform_integration.social_media_orchestrator.src.refactored_posting_orchestrator import (
        RefactoredPostingOrchestrator
    )

    orchestrator = RefactoredPostingOrchestrator()

    # Verify QWEN is enabled in orchestrator's duplicate manager
    assert orchestrator.duplicate_manager.qwen_enabled, "Orchestrator should have QWEN enabled"
    logger.info("[OK] Orchestrator has QWEN intelligence enabled")

    logger.info("\n" + "=" * 60)
    logger.info("[OK] ALL QWEN INTEGRATION TESTS PASSED!")
    logger.info("=" * 60)

    return True


def test_backwards_compatibility():
    """Test that existing functionality still works without QWEN"""
    logger.info("\n" + "=" * 60)
    logger.info("[U+1F9EA] TESTING BACKWARDS COMPATIBILITY")
    logger.info("=" * 60)

    from modules.platform_integration.social_media_orchestrator.src.core import (
        DuplicatePreventionManager
    )

    # Create instance with QWEN disabled
    logger.info("\n1️⃣ Creating DuplicatePreventionManager with QWEN disabled...")
    manager = DuplicatePreventionManager(qwen_enabled=False)

    # Test duplicate check still works
    logger.info("\n2️⃣ Testing duplicate check without QWEN...")
    result = manager.check_if_already_posted('test_video_456')

    assert 'video_id' in result, "Result should include video_id"
    assert 'already_posted' in result, "Result should include already_posted flag"
    assert 'platforms_posted' in result, "Result should include platforms_posted"

    logger.info(f"[OK] Duplicate check works: {result}")

    # Test marking as posted still works
    logger.info("\n3️⃣ Testing mark as posted without QWEN...")
    manager.mark_as_posted('test_video_456', 'linkedin', 'Test Title', 'http://test.url')

    # Verify it was marked
    result = manager.check_if_already_posted('test_video_456')
    assert result['already_posted'], "Video should be marked as posted"
    assert 'linkedin' in result['platforms_posted'], "LinkedIn should be in posted platforms"

    logger.info("[OK] Mark as posted works")

    logger.info("\n" + "=" * 60)
    logger.info("[OK] BACKWARDS COMPATIBILITY MAINTAINED!")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    try:
        # Run integration tests
        test_qwen_integration()

        # Run backwards compatibility tests
        test_backwards_compatibility()

        logger.info("\n" + "[CELEBRATE]" * 20)
        logger.info("[OK] ALL TESTS PASSED SUCCESSFULLY!")
        logger.info("QWEN intelligence has been successfully integrated")
        logger.info("into existing social media orchestrator modules!")
        logger.info("[CELEBRATE]" * 20)

    except AssertionError as e:
        logger.error(f"[FAIL] Test assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)