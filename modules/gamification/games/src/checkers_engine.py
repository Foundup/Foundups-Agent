"""
Checkers Engine - Simple 8x8 checkers implementation.

Board representation:
- 8x8 grid, only dark squares used (32 playable squares)
- White pieces: 'w' (regular), 'W' (king)
- Black pieces: 'b' (regular), 'B' (king)
- Empty: '.'

Move format: "a3b4" (from square to square)
- Columns: a-h
- Rows: 1-8
- White starts at rows 1-3, moves up
- Black starts at rows 6-8, moves down
"""
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class CheckersEngine:
    """Checkers game logic."""

    def __init__(self):
        self._board = None

    def new_game(self) -> str:
        """
        Start a new game, return initial board state.

        Board string format: 64 chars, row by row from a1 to h8
        Only dark squares are playable in checkers.
        """
        # Standard starting position
        # Rows 1-3: white pieces on dark squares
        # Rows 4-5: empty
        # Rows 6-8: black pieces on dark squares
        board = [['.' for _ in range(8)] for _ in range(8)]

        # Place white pieces (rows 0-2, which are rows 1-3 in notation)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:  # Dark squares
                    board[row][col] = 'w'

        # Place black pieces (rows 5-7, which are rows 6-8 in notation)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:  # Dark squares
                    board[row][col] = 'b'

        return self._board_to_string(board)

    def make_move(self, board_str: str, move_str: str) -> Dict:
        """
        Make a move on the board.

        Args:
            board_str: Current board state
            move_str: Move in format "a3b4" or "a3c5" (jump)

        Returns:
            Dict with: valid, board, no_pieces (win condition), error
        """
        board = self._string_to_board(board_str)
        move_str = move_str.strip().lower()

        # Parse move
        if len(move_str) != 4:
            return {'valid': False, 'error': 'Move format: a3b4 (from-to)'}

        try:
            from_col = ord(move_str[0]) - ord('a')
            from_row = int(move_str[1]) - 1
            to_col = ord(move_str[2]) - ord('a')
            to_row = int(move_str[3]) - 1
        except (ValueError, IndexError):
            return {'valid': False, 'error': 'Move format: a3b4 (from-to)'}

        # Validate bounds
        if not all(0 <= x <= 7 for x in [from_col, from_row, to_col, to_row]):
            return {'valid': False, 'error': 'Square out of bounds (a1-h8)'}

        # Get piece
        piece = board[from_row][from_col]
        if piece == '.':
            return {'valid': False, 'error': 'No piece at that square'}

        # Determine player color from piece
        is_white = piece.lower() == 'w'
        is_king = piece.isupper()

        # Check if destination is empty and on dark square
        if board[to_row][to_col] != '.':
            return {'valid': False, 'error': 'Destination not empty'}

        if (to_row + to_col) % 2 == 0:
            return {'valid': False, 'error': 'Must move to dark square'}

        # Calculate move distance
        row_diff = to_row - from_row
        col_diff = abs(to_col - from_col)

        # Direction check (non-kings can only move forward)
        if not is_king:
            if is_white and row_diff <= 0:
                return {'valid': False, 'error': 'White must move up (higher row)'}
            if not is_white and row_diff >= 0:
                return {'valid': False, 'error': 'Black must move down (lower row)'}

        # Simple move (1 diagonal)
        if abs(row_diff) == 1 and col_diff == 1:
            # Valid simple move
            board[to_row][to_col] = piece
            board[from_row][from_col] = '.'

        # Jump (2 diagonal, must capture)
        elif abs(row_diff) == 2 and col_diff == 2:
            # Check for piece to capture
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            captured = board[mid_row][mid_col]

            if captured == '.':
                return {'valid': False, 'error': 'Jump must capture a piece'}

            # Can only capture opponent's piece
            captured_is_white = captured.lower() == 'w'
            if captured_is_white == is_white:
                return {'valid': False, 'error': "Can't capture your own piece"}

            # Execute jump
            board[to_row][to_col] = piece
            board[from_row][from_col] = '.'
            board[mid_row][mid_col] = '.'  # Remove captured piece

        else:
            return {'valid': False, 'error': 'Invalid move distance (1 or 2 diagonals)'}

        # Check for king promotion
        if is_white and to_row == 7:
            board[to_row][to_col] = 'W'
        elif not is_white and to_row == 0:
            board[to_row][to_col] = 'B'

        # Check for win condition (opponent has no pieces)
        white_pieces = sum(1 for row in board for c in row if c.lower() == 'w')
        black_pieces = sum(1 for row in board for c in row if c.lower() == 'b')

        result = {
            'valid': True,
            'board': self._board_to_string(board),
            'no_pieces': white_pieces == 0 or black_pieces == 0
        }

        if white_pieces == 0:
            result['winner'] = 'black'
        elif black_pieces == 0:
            result['winner'] = 'white'

        return result

    def board_to_text(self, board_str: str) -> str:
        """Convert board to ASCII text representation."""
        board = self._string_to_board(board_str)
        lines = []
        lines.append("  a b c d e f g h")
        for row in range(7, -1, -1):
            row_str = f"{row + 1} "
            for col in range(8):
                piece = board[row][col]
                if piece == '.':
                    # Show dark/light squares
                    char = '.' if (row + col) % 2 == 1 else ' '
                else:
                    char = piece
                row_str += char + ' '
            lines.append(row_str + f"{row + 1}")
        lines.append("  a b c d e f g h")
        return '\n'.join(lines)

    def _board_to_string(self, board: List[List[str]]) -> str:
        """Convert 2D board to string."""
        return ''.join(''.join(row) for row in board)

    def _string_to_board(self, board_str: str) -> List[List[str]]:
        """Convert string to 2D board."""
        return [[board_str[row * 8 + col] for col in range(8)] for row in range(8)]

    def get_legal_moves(self, board_str: str, is_white_turn: bool) -> List[str]:
        """Get list of legal moves for current player."""
        board = self._string_to_board(board_str)
        moves = []
        piece_char = 'w' if is_white_turn else 'b'

        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece.lower() != piece_char:
                    continue

                is_king = piece.isupper()

                # Check all diagonal directions
                directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                if not is_king:
                    # Regular pieces can only move forward
                    directions = [(1, 1), (1, -1)] if is_white_turn else [(-1, 1), (-1, -1)]

                for dr, dc in directions:
                    # Simple move
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                        if board[new_row][new_col] == '.':
                            from_sq = chr(ord('a') + col) + str(row + 1)
                            to_sq = chr(ord('a') + new_col) + str(new_row + 1)
                            moves.append(from_sq + to_sq)

                    # Jump
                    jump_row, jump_col = row + 2 * dr, col + 2 * dc
                    mid_row, mid_col = row + dr, col + dc
                    if 0 <= jump_row <= 7 and 0 <= jump_col <= 7:
                        if board[jump_row][jump_col] == '.' and 0 <= mid_row <= 7 and 0 <= mid_col <= 7:
                            mid_piece = board[mid_row][mid_col]
                            if mid_piece != '.' and mid_piece.lower() != piece_char:
                                from_sq = chr(ord('a') + col) + str(row + 1)
                                to_sq = chr(ord('a') + jump_col) + str(jump_row + 1)
                                moves.append(from_sq + to_sq)

        return moves
