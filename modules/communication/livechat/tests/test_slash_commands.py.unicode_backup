"""
Test slash command handling directly
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.communication.livechat.src.command_handler import CommandHandler
from modules.gamification.whack_a_magat import get_profile

# Mock timeout manager
class MockTimeoutManager:
    pass

# Test the command handler
def test_help_command():
    """Test /help command"""
    print("Testing /help command...")
    
    # Initialize command handler
    handler = CommandHandler(MockTimeoutManager(), None)
    
    # Test /help for regular user
    response = handler.handle_whack_command("/help", "TestUser", "test_id_123", "USER")
    print(f"USER Response: {response}")
    assert response is not None
    assert "@TestUser" in response
    assert "MAGADOOM" in response
    
    # Test /help for mod
    response = handler.handle_whack_command("/help", "TestMod", "test_id_456", "MOD")
    print(f"MOD Response: {response}")
    assert response is not None
    assert "@TestMod" in response
    assert "/toggle" in response  # MOD-only command
    
    print("✅ /help command works!")

def test_score_command():
    """Test /score command"""
    print("\nTesting /score command...")
    
    # Initialize command handler
    handler = CommandHandler(MockTimeoutManager(), None)
    
    # Test /score
    response = handler.handle_whack_command("/score", "TestUser", "test_id_123", "USER")
    print(f"Response: {response}")
    assert response is not None
    assert "@TestUser" in response
    assert "XP" in response
    
    print("✅ /score command works!")

def test_leaderboard_command():
    """Test /leaderboard command"""
    print("\nTesting /leaderboard command...")
    
    # Initialize command handler
    handler = CommandHandler(MockTimeoutManager(), None)
    
    # Test /leaderboard
    response = handler.handle_whack_command("/leaderboard", "TestUser", "test_id_123", "USER")
    print(f"Response: {response}")
    assert response is not None
    assert "@TestUser" in response
    
    print("✅ /leaderboard command works!")

if __name__ == "__main__":
    try:
        test_help_command()
        test_score_command()
        test_leaderboard_command()
        print("\n🎉 All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()