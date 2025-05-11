import pygame
from copy import deepcopy
from checkers.constants import WHITE, BLACK

def __deepcopy__(self, memo):
    new_piece = Piece(self.row, self.col, self.color)
    new_piece.king = self.king
    new_piece.element_power = self.element_power
    new_piece.power_used = self.power_used
    return new_piece
    
def minimax(board, depth, max_player, game, alpha=float('-inf'), beta=float('inf')):
    """
    Implementation of minimax algorithm with alpha-beta pruning for checkers

    Args:
        board: Current board state
        depth: How many moves to look ahead
        max_player: Color of the maximizing player
        game: Game instance for accessing game state
        alpha: Alpha value for pruning
        beta: Beta value for pruning

    Returns:
        tuple: (evaluation, best_board)
    """
    if depth == 0 or board.winner() is not None:
        return evaluate(board), board

    if max_player:
        max_eval = float('-inf')
        best_move = None
        for move in get_all_moves(board, WHITE, game):
            evaluation = minimax(move, depth - 1, False, game, alpha, beta)[0]
            max_eval = max(max_eval, evaluation)
            if max_eval == evaluation:
                best_move = move

            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break

        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in get_all_moves(board, BLACK, game):
            evaluation = minimax(move, depth - 1, True, game, alpha, beta)[0]
            min_eval = min(min_eval, evaluation)
            if min_eval == evaluation:
                best_move = move

            beta = min(beta, evaluation)
            if beta <= alpha:
                break

        return min_eval, best_move


def simulate_move(piece, move, board, game, skip):
    """
    Simulates a move and returns the new board state
    Handles king promotion and multiple jumps
    """
    board_copy = deepcopy(board)
    piece_copy = board_copy.get_piece(piece.row, piece.col)

    # Check if skip is a valid list of pieces to skip or an empty list
    if isinstance(skip, list) and len(skip) > 0 and isinstance(skip[0], str):
        skip = []  # If it's a string (e.g., 'water_move'), treat skip as empty

    # Check for special elemental power moves
    if isinstance(skip, list) and len(skip) > 0:
        # Earth power move: Check if the skipped piece has earth power and block capture
        if skip[0].element_power == 'earth' and not skip[0].power_used:
                skip[0].use_power()
                board_copy.move(piece_copy, move[0], move[1])
                return board_copy

    # Handle fire power (capture without moving)
    if move[0] == piece.row and move[1] == piece.col and skip:
        if piece_copy.element_power == 'fire' and not piece_copy.power_used:
            piece_copy.use_power()
            board_copy.remove(skip)
            return board_copy
    
    # Handle air power (jump two squares diagonally)
    if not skip:
        distance = abs(move[0] - piece.row) + abs(move[1] - piece.col)
        if distance == 4:  # 2 squares diagonally
            if piece_copy.element_power == 'air' and not piece_copy.power_used:
                piece_copy.use_power()
                board_copy.move(piece_copy, move[0], move[1])
                return board_copy
    
    # Make the move
    board_copy.move(piece_copy, move[0], move[1])
    
    # Handle water power move (if backward move is indicated)
    if isinstance(skip, list) and len(skip) > 0 and skip[-1] == 'water_move':
        if piece_copy.element_power == 'water' and not piece_copy.power_used:
            piece_copy.use_power()
            skip.pop()  # Remove the water_move marker
            
    # Process captures
    if isinstance(skip, list) and len(skip) > 0 and skip[0] != 'water_move':
        board_copy.remove(skip)

        # Check for additional captures
        additional_moves = {}
        additional_moves = board_copy.get_valid_moves(piece_copy)
        # Filter to only keep capture moves
        capture_moves = {m: s for m, s in additional_moves.items() if s and isinstance(s, list) and len(s) > 0 and not isinstance(s[-1], str)}

        # If there are additional captures, recursively make the best one
        if capture_moves:
            best_move = max(capture_moves.items(), key=lambda x: len(x[1]))
            move_pos, skipped = best_move

            # Recursively simulate the additional capture
            return simulate_move(piece_copy, move_pos, board_copy, game, skipped)

    return board_copy



def get_all_moves(board, color, game):
    """Gets all possible moves for a given color"""
    moves = []

    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            moves.append(simulate_move(piece, move, board, game, skip))

    return moves


def evaluate(board):
    """
    Evaluates the board state with a more sophisticated evaluation function
    Takes into account:
    - Number of pieces
    - Kings (weighted more heavily)
    - Position on the board (edges and advancement)
    - Mobility (number of moves available)
    - Elemental powers remaining (pieces with unused powers are worth more)
    """
    # Basic piece count
    white_pieces = board.white_left
    black_pieces = board.red_left

    # Get all pieces for more detailed evaluation
    white_all_pieces = board.get_all_pieces(WHITE)
    black_all_pieces = board.get_all_pieces(BLACK)

    # King count (weighted more)
    white_kings = sum(1 for piece in white_all_pieces if piece.king)
    black_kings = sum(1 for piece in black_all_pieces if piece.king)
    
    # Count unused elemental powers (bonus value)
    white_powers = sum(1 for piece in white_all_pieces if piece.element_power and not piece.power_used)
    black_powers = sum(1 for piece in black_all_pieces if piece.element_power and not piece.power_used)

    # Calculate positional advantage
    white_position_value = sum(_get_position_value(piece, WHITE) for piece in white_all_pieces)
    black_position_value = sum(_get_position_value(piece, BLACK) for piece in black_all_pieces)

    # Calculate mobility (number of moves available)
    white_mobility = sum(len(board.get_valid_moves(piece)) for piece in white_all_pieces)
    black_mobility = sum(len(board.get_valid_moves(piece)) for piece in black_all_pieces)

    # Final score calculation with weights
    # Regular pieces are worth 1.0
    # Kings are worth 2.0
    # Unused powers are worth 0.5
    # Position value is weighted at 0.1
    # Mobility is weighted at 0.1 per move
    white_score = (white_pieces - white_kings) + (white_kings * 2.0) + (white_powers * 0.5) + (white_position_value * 0.1) + (
                white_mobility * 0.1)
    black_score = (black_pieces - black_kings) + (black_kings * 2.0) + (black_powers * 0.5) + (black_position_value * 0.1) + (
                black_mobility * 0.1)

    return white_score - black_score


def _get_position_value(piece, color):
    """
    Calculates positional value of a piece:
    - Regular pieces get value for advancing toward the opposite side
    - Kings get value for being centralized
    - Pieces on the edge are worth less
    """
    row, col = piece.row, piece.col
    value = 0

    # Value for regular pieces advancing
    if not piece.king:
        if color == WHITE:
            value += (7 - row) * 0.1  # More value as white advances upward
        else:
            value += row * 0.1  # More value as black advances downward
    else:
        # Kings want to be centralized
        # Calculate distance from center (3.5, 3.5)
        center_dist = abs(row - 3.5) + abs(col - 3.5)
        value += (7 - center_dist) * 0.1  # More central = more value

    # Penalty for edge pieces (harder to maneuver)
    if col == 0 or col == 7 or row == 0 or row == 7:
        value -= 0.2
        
    # Bonus for pieces with unused elemental powers
    if piece.element_power and not piece.power_used:
        value += 0.3

    return value