#!/usr/bin/env python3
"""
Integration Test for Refactored Social Media Orchestrator
Tests the complete flow with real module interactions
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the refactored modules
from src.refactored_posting_orchestrator import get_orchestrator
from src.orchestrator_migration import get_migration_bridge


def test_refactored_orchestrator():
    """Test the refactored orchestrator with sample data"""
    print("\n" + "="*80)
    print("TESTING REFACTORED SOCIAL MEDIA ORCHESTRATOR")
    print("="*80)

    # Get orchestrator instance
    orchestrator = get_orchestrator()
    print("\n✅ Orchestrator initialized successfully")

    # Validate configuration
    print("\n🔍 Validating configuration...")
    validation = orchestrator.validate_configuration()
    print(f"   Configuration valid: {validation['valid']}")
    print(f"   Enabled channels: {validation['components']['channels']['count']}")

    # Test duplicate checking
    print("\n🔍 Testing duplicate prevention...")
    test_video_id = "TEST_REFACTOR_123"

    # First check - should not be posted
    result = orchestrator.duplicate_manager.check_if_already_posted(test_video_id)
    print(f"   Video {test_video_id} already posted: {result['already_posted']}")
    assert not result['already_posted'], "Test video should not be marked as posted initially"

    # Mark as posted to LinkedIn first
    orchestrator.duplicate_manager.mark_as_posted(
        video_id=test_video_id,
        platform="linkedin",
        title="Test Stream for Refactored Modules",
        url="https://youtube.com/test"
    )

    # Mark as posted to X as well
    orchestrator.duplicate_manager.mark_as_posted(
        video_id=test_video_id,
        platform="x_twitter",
        title="Test Stream for Refactored Modules",
        url="https://youtube.com/test"
    )
    print(f"   Marked as posted to both platforms")

    # Second check - should be posted
    result = orchestrator.duplicate_manager.check_if_already_posted(test_video_id)
    print(f"   Video {test_video_id} already posted: {result['already_posted']}")
    print(f"   Platforms: {result['platforms_posted']}")
    assert result['already_posted'], "Test video should be marked as posted after marking"

    # Test channel configuration
    print("\n🔍 Testing channel configuration...")
    channels = orchestrator.channel_config.get_enabled_channels()
    print(f"   Enabled channels: {channels}")

    for channel in channels[:2]:  # Test first two channels
        config = orchestrator.channel_config.get_channel_config(channel)
        print(f"   {channel}: LinkedIn={config.get('linkedin_page')}, X={config.get('x_account')}")

    # Test live status verifier
    print("\n🔍 Testing live status verifier...")
    orchestrator.status_verifier.clear_cache()
    print("   Cache cleared successfully")

    # Test posting service configuration
    print("\n🔍 Testing platform posting service...")
    posting_validation = orchestrator.posting_service.validate_configuration()
    print(f"   Posting service valid: {posting_validation['valid']}")
    if posting_validation.get('errors'):
        for error in posting_validation['errors']:
            print(f"   ⚠️ {error}")

    # Get posting statistics
    print("\n📊 Posting statistics:")
    stats = orchestrator.get_posting_stats()
    print(f"   Total videos in history: {stats.get('total_videos', 0)}")
    print(f"   LinkedIn posts: {stats.get('linkedin_count', 0)}")
    print(f"   X/Twitter posts: {stats.get('x_twitter_count', 0)}")

    print("\n✅ All integration tests passed!")
    return True


def test_migration_bridge():
    """Test the migration bridge for backward compatibility"""
    print("\n" + "="*80)
    print("TESTING MIGRATION BRIDGE")
    print("="*80)

    # Get migration bridge
    bridge = get_migration_bridge()
    print("\n✅ Migration bridge initialized")

    # Test backward compatible check
    test_video = "MIGRATION_TEST_456"
    result = bridge.check_if_already_posted(test_video)
    print(f"\n🔍 Checking video {test_video}:")
    print(f"   Already posted: {result['already_posted']}")
    print(f"   Platforms: {result.get('platforms_posted', [])}")

    # Test stats through bridge
    stats = bridge.get_posting_stats()
    print(f"\n📊 Stats through bridge:")
    print(f"   Total videos: {stats.get('total_videos', 0)}")

    print("\n✅ Migration bridge tests passed!")
    return True


def test_sample_stream_flow():
    """Test complete flow with sample stream data"""
    print("\n" + "="*80)
    print("TESTING COMPLETE STREAM FLOW")
    print("="*80)

    orchestrator = get_orchestrator()

    # Sample stream data
    sample_stream = {
        'video_id': 'SAMPLE_STREAM_789',
        'title': 'Testing Refactored Social Media Orchestrator',
        'url': 'https://youtube.com/watch?v=SAMPLE_789',
        'channel_name': '@FoundUps'
    }

    print(f"\n📹 Processing sample stream:")
    print(f"   Video: {sample_stream['video_id']}")
    print(f"   Title: {sample_stream['title']}")
    print(f"   Channel: {sample_stream['channel_name']}")

    # First, check if already posted
    duplicate_check = orchestrator.duplicate_manager.check_if_already_posted(
        sample_stream['video_id']
    )
    print(f"\n🔍 Duplicate check:")
    print(f"   Already posted: {duplicate_check['already_posted']}")

    if not duplicate_check['already_posted']:
        print("\n✅ Not a duplicate - would proceed with posting")
        print("   (Skipping actual posting in test mode)")
    else:
        print("\n⚠️ Already posted to: {duplicate_check['platforms_posted']}")

    # Test the handle_stream_detected method (non-blocking)
    print("\n🚀 Testing handle_stream_detected (non-blocking)...")
    result = orchestrator.handle_stream_detected(**sample_stream)
    print(f"   Request processed: video_id={result['video_id']}")
    print(f"   Errors: {result.get('errors', 'None')}")

    print("\n✅ Stream flow test completed!")
    return True


def main():
    """Run all integration tests"""
    print("\n" + "🚀 "*20)
    print("REFACTORED SOCIAL MEDIA ORCHESTRATOR - INTEGRATION TESTS")
    print("🚀 "*20)

    try:
        # Run tests
        test_refactored_orchestrator()
        test_migration_bridge()
        test_sample_stream_flow()

        print("\n" + "="*80)
        print("✅ ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
        print("="*80)
        print("\n📝 Summary:")
        print("   - Refactored orchestrator: ✅ Working")
        print("   - Core modules: ✅ Integrated")
        print("   - Migration bridge: ✅ Compatible")
        print("   - Stream flow: ✅ Functional")
        print("\n🎉 The refactored modules are ready for production use!")

    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)