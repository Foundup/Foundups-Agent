"""
Test automatic session logging functionality
Tests that sessions are automatically logged when streams start/end
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directories to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Direct import from the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from chat_memory_manager import ChatMemoryManager


def test_automatic_session_logging():
    """Test that sessions are automatically logged with proper format."""

    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"✅ Created temp directory: {temp_dir}")

        # Initialize memory manager
        manager = ChatMemoryManager(memory_dir=temp_dir)
        print("✅ Initialized ChatMemoryManager")

        # Start a session
        manager.start_session("test_video_123", "Test Stream Title")
        print("✅ Started session")

        # Simulate some messages
        # Regular user message
        manager.store_message(
            author_name="RegularUser",
            message_text="Hello everyone!",
            role="USER",
            author_id="UC_regular_user_id",
            youtube_name="RegularUser"
        )

        # Mod message
        manager.store_message(
            author_name="ModeratorJohn",
            message_text="Welcome to the stream!",
            role="MOD",
            author_id="UC_mod_john_id",
            youtube_name="ModeratorJohn"
        )

        # Owner message
        manager.store_message(
            author_name="StreamOwner",
            message_text="Thanks for joining!",
            role="OWNER",
            author_id="UC_owner_id",
            youtube_name="StreamOwner"
        )

        # Consciousness trigger
        manager.store_message(
            author_name="ConsciousUser",
            message_text="✊✋🖐 What's the meaning of life?",
            role="USER",
            author_id="UC_conscious_id",
            youtube_name="ConsciousUser"
        )

        # Fact check request
        manager.store_message(
            author_name="ModeratorJohn",
            message_text="✊✋🖐FC @TrollUser spreading misinformation",
            role="MOD",
            author_id="UC_mod_john_id",
            youtube_name="ModeratorJohn"
        )

        # Log a fact-check event
        manager.log_fact_check("TrollUser", "ModeratorJohn", "conspiracy theory defense")

        print("✅ Added test messages")

        # End session (should save logs)
        manager.end_session()
        print("✅ Ended session")

        # Check that files were created
        conversation_dir = Path(temp_dir) / "conversation"
        assert conversation_dir.exists(), "Conversation directory not created"

        # Find the session directory
        session_dirs = list(conversation_dir.glob("session_*"))
        assert len(session_dirs) == 1, f"Expected 1 session dir, found {len(session_dirs)}"

        session_dir = session_dirs[0]
        print(f"✅ Found session directory: {session_dir.name}")

        # Check required files exist
        full_transcript = session_dir / "full_transcript.txt"
        mod_messages = session_dir / "mod_messages.txt"
        session_summary = session_dir / "session_summary.txt"

        assert full_transcript.exists(), "Full transcript not created"
        assert mod_messages.exists(), "Mod messages file not created"
        assert session_summary.exists(), "Session summary not created"

        print("✅ All log files created")

        # Verify content format
        # Check mod messages format
        with open(mod_messages, 'r', encoding='utf-8') as f:
            mod_content = f.read()
            assert "UC_mod_john_id | ModeratorJohn: Welcome to the stream!" in mod_content
            assert "UC_owner_id | StreamOwner: Thanks for joining!" in mod_content
            print("✅ Mod messages format correct (YouTube ID | Name: Message)")

        # Check full transcript
        with open(full_transcript, 'r', encoding='utf-8') as f:
            full_content = f.read()
            assert "RegularUser: Hello everyone!" in full_content
            assert "[MOD] ModeratorJohn: Welcome to the stream!" in full_content
            assert "[OWNER] StreamOwner: Thanks for joining!" in full_content
            assert "FACT-CHECK:" in full_content  # Check for fact-check entry
            print("✅ Full transcript format correct")

        # Check summary
        with open(session_summary, 'r', encoding='utf-8') as f:
            summary_content = f.read()
            assert "Total Messages: 6" in summary_content  # 5 messages + 1 fact-check
            assert "Mod Messages: 3" in summary_content  # 2 mod messages + 1 owner
            assert "Consciousness Triggers: 2" in summary_content  # Both messages with emojis
            assert "Fact Check Requests: 1" in summary_content
            assert "Defense Mechanisms Triggered:" in summary_content
            print("✅ Session summary contains all expected stats")

        print("\n🎉 All tests passed! Automatic session logging is working correctly.")
        print(f"📁 Session logs saved to: {session_dir}")

        # Display sample output
        print("\n📄 Sample Mod Message Format:")
        print("UC_mod_john_id | ModeratorJohn: Welcome to the stream!")
        print("UC_owner_id | StreamOwner: Thanks for joining!")

        return True


if __name__ == "__main__":
    try:
        success = test_automatic_session_logging()
        if success:
            print("\n✅ TEST PASSED: Automatic session logging is fully functional!")
            print("🔍 Sessions will be automatically logged to memory/conversation/")
            print("🎯 Fact-checks and defense mechanisms are tracked for 0102 analysis")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()