"""Run games module tests without pytest plugin issues."""
import sys
import traceback
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_all_tests():
    """Run all test classes manually."""
    passed = 0
    failed = 0
    errors = []

    print("=" * 60)
    print("GAMES MODULE TESTS")
    print("=" * 60)

    # Test Chess Engine
    print("\n[CHESS ENGINE]")
    try:
        from modules.gamification.games.src.chess_engine import ChessEngine, CHESS_AVAILABLE

        if not CHESS_AVAILABLE:
            print("  SKIP: python-chess not installed")
        else:
            engine = ChessEngine()

            # Test 1: New game
            fen = engine.new_game()
            assert fen.startswith("rnbqkbnr"), "New game should return starting position"
            print("  PASS: new_game returns starting FEN")
            passed += 1

            # Test 2: Valid move e2e4
            result = engine.make_move(fen, "e2e4")
            assert result['valid'] is True, "e2e4 should be valid"
            print("  PASS: valid move e2e4")
            passed += 1

            # Test 3: Invalid move
            result = engine.make_move(fen, "e2e5")
            assert result['valid'] is False, "e2e5 should be invalid"
            print("  PASS: invalid move rejected")
            passed += 1

            # Test 4: Board to text
            text = engine.board_to_text(fen)
            assert 'r' in text and 'R' in text, "Board text should have pieces"
            print("  PASS: board_to_text works")
            passed += 1

            # Test 5: Legal moves
            moves = engine.get_legal_moves(fen)
            assert len(moves) == 20, f"Should have 20 legal moves, got {len(moves)}"
            print("  PASS: get_legal_moves returns 20 moves")
            passed += 1

    except Exception as e:
        print(f"  FAIL: {e}")
        errors.append(f"Chess: {e}")
        failed += 1

    # Test Checkers Engine
    print("\n[CHECKERS ENGINE]")
    try:
        from modules.gamification.games.src.checkers_engine import CheckersEngine
        engine = CheckersEngine()

        # Test 1: New game has 24 pieces
        board = engine.new_game()
        white = board.count('w')
        black = board.count('b')
        assert white == 12 and black == 12, f"Should have 12+12 pieces, got {white}+{black}"
        print("  PASS: new_game has 24 pieces")
        passed += 1

        # Test 2: Valid simple move
        result = engine.make_move(board, "b3c4")
        assert result['valid'] is True, "b3c4 should be valid"
        print("  PASS: valid move b3c4")
        passed += 1

        # Test 3: Board to text
        text = engine.board_to_text(board)
        assert 'w' in text and 'b' in text, "Board should show pieces"
        print("  PASS: board_to_text works")
        passed += 1

        # Test 4: Jump capture
        # Note: Checkers uses dark squares where (row+col) % 2 == 1
        # b3 (row 2, col 1): (2+1)%2=1 ✓ dark
        # c4 (row 3, col 2): (3+2)%2=1 ✓ dark
        # d5 (row 4, col 3): (4+3)%2=1 ✓ dark
        test_board = '.' * 64
        board_list = list(test_board)
        board_list[2 * 8 + 1] = 'w'  # White at b3 (row 2, col 1)
        board_list[3 * 8 + 2] = 'b'  # Black at c4 (row 3, col 2)
        test_board = ''.join(board_list)
        result = engine.make_move(test_board, "b3d5")
        assert result['valid'] is True, f"Jump should be valid: {result.get('error', '')}"
        assert result['board'][3 * 8 + 2] == '.', "Captured piece should be gone"
        print("  PASS: jump capture works")
        passed += 1

        # Test 5: King promotion
        test_board = '.' * 64
        board_list = list(test_board)
        board_list[6 * 8 + 1] = 'w'  # White at b7
        test_board = ''.join(board_list)
        result = engine.make_move(test_board, "b7a8")
        assert result['valid'] is True, "Move to last row should work"
        assert result['board'][7 * 8 + 0] == 'W', "Should be promoted to king"
        print("  PASS: king promotion works")
        passed += 1

    except Exception as e:
        print(f"  FAIL: {e}")
        traceback.print_exc()
        errors.append(f"Checkers: {e}")
        failed += 1

    # Test Game Manager
    print("\n[GAME MANAGER]")
    try:
        from modules.gamification.games.src.game_manager import GameManager

        # Test 1: First player waits
        gm = GameManager()
        result = gm.join_chess("Alice", "UC_alice")
        assert result['status'] == 'waiting', "First player should wait"
        print("  PASS: first player waits")
        passed += 1

        # Test 2: Second player starts game
        gm = GameManager()
        gm.join_chess("Alice", "UC_alice")
        result = gm.join_chess("Bob", "UC_bob")
        assert result['status'] == 'started', "Game should start"
        assert result['game'].white_player in ['Alice', 'Bob'], "Should have white player"
        print("  PASS: second player starts game")
        passed += 1

        # Test 3: Random color assignment
        gm = GameManager()
        gm.join_chess("Alice", "UC_alice")
        result = gm.join_chess("Bob", "UC_bob")
        white = result['game'].white_player
        black = result['game'].black_player
        assert white != black, "Colors should be different"
        print(f"  PASS: random colors ({white}=white, {black}=black)")
        passed += 1

        # Test 4: Make valid move
        gm = GameManager()
        gm.join_chess("Alice", "UC_alice")
        result = gm.join_chess("Bob", "UC_bob")
        game = result['game']
        white_id = game.white_id
        white_name = game.white_player
        result = gm.make_move(white_name, white_id, "e2e4")
        assert result['status'] == 'moved', f"Move should work, got {result['status']}"
        print("  PASS: valid move works")
        passed += 1

        # Test 5: Wrong turn rejected
        gm = GameManager()
        gm.join_chess("Alice", "UC_alice")
        result = gm.join_chess("Bob", "UC_bob")
        game = result['game']
        black_id = game.black_id
        black_name = game.black_player
        result = gm.make_move(black_name, black_id, "e7e5")
        assert result['status'] == 'not_your_turn', "Black shouldn't move first"
        print("  PASS: wrong turn rejected")
        passed += 1

        # Test 6: Resign
        gm = GameManager()
        gm.join_chess("Alice", "UC_alice")
        gm.join_chess("Bob", "UC_bob")
        result = gm.resign("Alice", "UC_alice")
        assert result['status'] == 'resigned', "Resign should work"
        print("  PASS: resign works")
        passed += 1

        # Test 7: Checkers game
        gm = GameManager()
        gm.join_checkers("Alice", "UC_alice")
        result = gm.join_checkers("Bob", "UC_bob")
        assert result['status'] == 'started', "Checkers should start"
        assert result['game'].game_type == 'checkers', "Should be checkers"
        print("  PASS: checkers game starts")
        passed += 1

    except Exception as e:
        print(f"  FAIL: {e}")
        traceback.print_exc()
        errors.append(f"GameManager: {e}")
        failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
