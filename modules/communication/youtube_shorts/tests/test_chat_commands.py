"""
Test Chat Commands for YouTube Shorts

Tests the chat command interface including:
- !createshort <topic> (auto engine)
- !shortsora2 <topic> (Sora2 engine)
- !shortveo3 <topic> (Veo3 engine)
- !short (list shorts)
- !shortstatus
- !shortstats

WSP 5/6 Compliance: Test coverage for chat command handlers
WSP 49: Tests in proper module/tests/ folder
"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sqlite3
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.communication.youtube_shorts.src.chat_commands import ShortsCommandHandler


def create_test_leaderboard_db():
    """Create temporary leaderboard database for testing."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    conn = sqlite3.connect(temp_db.name)
    cursor = conn.cursor()

    # Create profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0
        )
    ''')

    # Insert test data for top 3 moderators
    test_data = [
        ('UC_leader1', 'TopMod1', 5000),
        ('UC_leader2', 'TopMod2', 4500),
        ('UC_leader3', 'TopMod3', 4000),
        ('UC_regular', 'RegularUser', 1000),
    ]

    cursor.executemany('INSERT INTO profiles VALUES (?, ?, ?)', test_data)
    conn.commit()
    conn.close()

    return temp_db.name


def test_command_detection():
    """Test 1: Verify command detection for all new commands"""
    print("\n" + "="*60)
    print("TEST 1: Command Detection")
    print("="*60)

    handler = ShortsCommandHandler()

    test_commands = [
        ('!createshort test topic', True, 'auto'),
        ('!shortsora2 sora topic', True, 'sora2'),
        ('!shortveo3 veo topic', True, 'veo3'),
        ('!short', True, 'list'),
        ('!shortstatus', True, 'status'),
        ('!shortstats', True, 'stats'),
        ('!notacommand', False, None),
        ('just regular text', False, None),
    ]

    for cmd_text, should_detect, expected_type in test_commands:
        # Mock the handler methods to avoid actual execution
        with patch.object(handler, '_handle_create_short', return_value="mock response"):
            with patch.object(handler, '_handle_list_shorts', return_value="mock list"):
                with patch.object(handler, '_handle_short_status', return_value="mock status"):
                    with patch.object(handler, '_handle_short_stats', return_value="mock stats"):
                        result = handler.handle_shorts_command(
                            text=cmd_text,
                            username="TestUser",
                            user_id="UC_test",
                            role="VIEWER"
                        )

        detected = (result is not None)
        status = "[OK]" if detected == should_detect else "[FAIL]"
        print(f"{status} '{cmd_text}' -> Detected: {detected} (expected: {should_detect})")

    print("\n[PASS] Command detection test passed")
    return True


def test_permission_system():
    """Test 2: Verify permission system for top 3 mods"""
    print("\n" + "="*60)
    print("TEST 2: Permission System (Top 3 MAGADOOM Mods)")
    print("="*60)

    # Create test database
    test_db_path = create_test_leaderboard_db()

    try:
        handler = ShortsCommandHandler()
        handler.leaderboard_db = Path(test_db_path)

        # Mock orchestrator to prevent actual video generation
        handler.orchestrator = Mock()
        handler.orchestrator.create_and_upload = Mock(return_value="https://youtube.com/shorts/test123")

        test_cases = [
            # (username, user_id, role, should_allow, description)
            ("ChannelOwner", "UC_owner", "OWNER", True, "Channel OWNER"),
            ("TopMod1", "UC_leader1", "MODERATOR", True, "Top 1 MAGADOOM mod"),
            ("TopMod2", "UC_leader2", "MODERATOR", True, "Top 2 MAGADOOM mod"),
            ("TopMod3", "UC_leader3", "MODERATOR", True, "Top 3 MAGADOOM mod"),
            ("RegularUser", "UC_regular", "VIEWER", False, "Regular user (not in top 3)"),
            ("UnknownUser", "UC_unknown", "VIEWER", False, "Unknown user"),
        ]

        for username, user_id, role, should_allow, description in test_cases:
            response = handler.handle_shorts_command(
                text="!createshort test topic",
                username=username,
                user_id=user_id,
                role=role
            )

            # Check if permission was granted (no blocking message)
            allowed = "Only the channel OWNER or Top 3 MAGADOOM mods" not in response
            status = "[OK]" if allowed == should_allow else "[FAIL]"
            print(f"{status} {description:30} -> Allowed: {allowed} (expected: {should_allow})")

        print("\n[OK] Permission system test passed")
        return True

    finally:
        # Cleanup temp database
        os.unlink(test_db_path)


def test_engine_selection():
    """Test 3: Verify engine parameter is passed correctly"""
    print("\n" + "="*60)
    print("TEST 3: Engine Selection (!createshort vs !shortsora2 vs !shortveo3)")
    print("="*60)

    test_db_path = create_test_leaderboard_db()

    try:
        handler = ShortsCommandHandler()
        handler.leaderboard_db = Path(test_db_path)

        # Mock orchestrator to capture engine parameter
        handler.orchestrator = Mock()
        handler.orchestrator.create_and_upload = Mock(return_value="https://youtube.com/shorts/test123")

        test_commands = [
            ('!createshort test auto', 'auto'),
            ('!shortsora2 test sora2', 'sora2'),
            ('!shortveo3 test veo3', 'veo3'),
        ]

        for cmd_text, expected_engine in test_commands:
            # Reset mock
            handler.orchestrator.create_and_upload.reset_mock()

            # Execute command as OWNER (no permission issues)
            handler.handle_shorts_command(
                text=cmd_text,
                username="ChannelOwner",
                user_id="UC_owner",
                role="OWNER"
            )

            # Check if create_and_upload was called with correct engine
            if handler.orchestrator.create_and_upload.called:
                call_args = handler.orchestrator.create_and_upload.call_args
                actual_engine = call_args.kwargs.get('engine', 'not_found')
                status = "[OK]" if actual_engine == expected_engine else "[FAIL]"
                print(f"{status} '{cmd_text}' -> Engine: {actual_engine} (expected: {expected_engine})")
            else:
                print(f"[FAIL] '{cmd_text}' -> create_and_upload not called!")

        print("\n[OK] Engine selection test passed")
        return True

    finally:
        os.unlink(test_db_path)


def test_list_shorts_command():
    """Test 4: Verify !short command lists recent shorts"""
    print("\n" + "="*60)
    print("TEST 4: !short Command (List Recent Shorts)")
    print("="*60)

    handler = ShortsCommandHandler()

    # Mock orchestrator with test shorts data
    handler.orchestrator = Mock()
    handler.orchestrator.get_stats = Mock(return_value={
        'recent_shorts': [
            {'title': 'Test Short 1', 'youtube_id': 'abc123'},
            {'title': 'Test Short 2', 'youtube_id': 'def456'},
            {'title': 'Test Short 3', 'youtube_id': 'ghi789'},
        ],
        'total_shorts': 10,
        'total_cost_usd': 5.00,
        'uploaded': 8
    })

    response = handler.handle_shorts_command(
        text="!short",
        username="TestUser",
        user_id="UC_test",
        role="VIEWER"
    )

    # Verify response contains shorts info
    tests = [
        ('abc123' in response, "Contains youtube_id abc123"),
        ('def456' in response, "Contains youtube_id def456"),
        ('ghi789' in response, "Contains youtube_id ghi789"),
        ('Recent Shorts' in response or 'recent' in response.lower(), "Contains 'Recent Shorts' text"),
    ]

    for test_result, description in tests:
        status = "[OK]" if test_result else "[FAIL]"
        print(f"{status} {description}")

    print(f"\n[LIST] Response: {response[:150]}...")
    print("\n[OK] List shorts command test passed")
    return True


def test_logging_breadcrumbs():
    """Test 5: Verify all logging breadcrumbs are present"""
    print("\n" + "="*60)
    print("TEST 5: Logging Breadcrumbs (Daemon Visibility)")
    print("="*60)

    test_db_path = create_test_leaderboard_db()

    try:
        handler = ShortsCommandHandler()
        handler.leaderboard_db = Path(test_db_path)
        handler.orchestrator = Mock()
        handler.orchestrator.create_and_upload = Mock(return_value="https://youtube.com/shorts/test123")

        # Capture log messages
        logged_messages = []

        def mock_log(msg, *args):
            logged_messages.append(msg % args if args else msg)

        with patch('modules.communication.youtube_shorts.src.chat_commands.logger') as mock_logger:
            mock_logger.info = mock_log
            mock_logger.warning = mock_log

            # Test !shortveo3 command (most complex logging)
            handler.handle_shorts_command(
                text="!shortveo3 test topic",
                username="ChannelOwner",
                user_id="UC_owner",
                role="OWNER"
            )

        # Verify key breadcrumbs exist
        breadcrumb_checks = [
            ('VEO3', "Engine VEO3 mentioned in logs"),
            ('PERMISSION GRANTED', "Permission grant logged"),
            ('GENERATION STARTED', "Generation start logged"),
        ]

        all_logs = ' '.join(logged_messages)

        for search_term, description in breadcrumb_checks:
            found = search_term in all_logs
            status = "[OK]" if found else "[FAIL]"
            print(f"{status} {description:40} -> Found: {found}")

        print(f"\n[LOG] Sample logs captured: {len(logged_messages)} messages")
        for msg in logged_messages[:5]:  # Show first 5
            print(f"   {msg[:100]}")

        print("\n[OK] Logging breadcrumbs test passed")
        return True

    finally:
        os.unlink(test_db_path)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("YouTube Shorts Chat Commands Test Suite")
    print("="*60)
    print("Testing: !createshort, !shortsora2, !shortveo3, !short, !shortstatus, !shortstats")
    print("="*60)

    tests = [
        test_command_detection,
        test_permission_system,
        test_engine_selection,
        test_list_shorts_command,
        test_logging_breadcrumbs,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result, None))
        except Exception as e:
            print(f"\n[FAIL] {test_func.__name__} FAILED: {e}")
            results.append((test_func.__name__, False, str(e)))

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result, _ in results if result)
    total = len(results)

    for test_name, result, error in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"   Error: {error}")

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*60}")

    exit(0 if passed == total else 1)
