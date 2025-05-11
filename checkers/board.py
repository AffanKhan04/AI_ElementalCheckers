import pygame
import random
from .constants import ROWS, COLS, SQUARE_SIZE, WHITE, BLACK, CREAM, BROWN, ELEMENTS
from .piece import Piece


class Board:
    def __init__(self):
        self.board = []
        self.white_left = self.red_left = 12  # Keeping variable names for compatibility
        self.white_kings = self.black_kings = 0
        self.create_board()
        self.pending_earth_power = None  # Store info when earth power is triggered

    def draw_squares(self, win):
        win.fill(CREAM)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, BROWN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        piece = Piece(row, col, WHITE)
                        # Assign random elemental power
                        piece.set_element(random.choice(ELEMENTS))
                        self.board[row].append(piece)
                    elif row > 4:
                        piece = Piece(row, col, BLACK)
                        # Assign random elemental power
                        piece.set_element(random.choice(ELEMENTS))
                        self.board[row].append(piece)
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def move(self, piece, row, col):
        """Moves a piece and handles king promotion"""
        self.board[piece.row][piece.col] = 0
        piece.move(row, col)

        # Check if piece should be promoted to king
        if (row == 0 and piece.color == BLACK) or (row == ROWS - 1 and piece.color == WHITE):
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.black_kings += 1

        self.board[row][col] = piece

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def get_piece(self, row, col):
        """Returns the piece at a given position"""
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.board[row][col]
        return None

    def remove(self, pieces):
        """Removes pieces from the board (after a capture)"""
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece.color == BLACK:
                self.red_left -= 1  # Using red_left for BLACK pieces for compatibility
            else:
                self.white_left -= 1

            # Also decrement kings count if needed
            if piece.king:
                if piece.color == BLACK:
                    self.black_kings -= 1
                else:
                    self.white_kings -= 1

    def winner(self):
        """Determines if there's a winner"""
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return BLACK

        # Additional check: if a player has no valid moves, they lose
        black_moves = any(len(self.get_valid_moves(piece)) > 0 for piece in self.get_all_pieces(BLACK))
        white_moves = any(len(self.get_valid_moves(piece)) > 0 for piece in self.get_all_pieces(WHITE))

        if not black_moves:
            return WHITE
        if not white_moves:
            return BLACK

        return None

    def _traverse_left(self, start, stop, step, color, left, skipped=[], is_water_move=False):
        """Traverse the board diagonally to the left. For kings, this allows unlimited distance movement until an obstacle"""
        
        moves = {}
        last = []

        # Handle negative step correctly
        if step < 0:
            condition = lambda r: r > stop
        else:
            condition = lambda r: r < stop

        r = start
        while condition(r) and left >= 0:
            current = self.board[r][left]

            # Empty square
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    # For water power backward moves, mark them as water moves
                    if is_water_move:
                        # Create a list if last is empty
                        moves[(r, left)] = last.copy() if last else []
                        # Add a special marker to indicate this is a water power move
                        moves[(r, left)].append('water_move')
                    else:
                        moves[(r, left)] = last

                if last:
                    # If we've skipped a piece, check for additional jumps
                    if step == -1:
                        row = -1  # Allow kings to go all the way up
                    else:
                        row = ROWS  # Allow kings to go all the way down
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            # Same color piece - can't move here
            elif current.color == color:
                break
            # Opponent's piece - can possibly jump
            else:
                last = [current]

            left -= 1
            r += step

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[], is_water_move=False):
        """
        Traverse the board diagonally to the right
        For kings, this allows unlimited distance movement until an obstacle
        """
        moves = {}
        last = []

        # Handle negative step correctly
        if step < 0:
            condition = lambda r: r > stop
        else:
            condition = lambda r: r < stop

        r = start
        while condition(r) and right < COLS:
            current = self.board[r][right]

            # Empty square
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    if is_water_move:
                        moves[(r, right)] = last.copy() if last else []
                        moves[(r, right)].append('water_move')
                    else:
                        moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = -1
                    else:
                        row = ROWS
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break

            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
            r += step

        return moves

   
    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        # For regular pieces, limit movement to 1 square in their direction
        # For kings, allow movement in any direction with no distance limitation
        if piece.king:
            # Kings can move in all 4 diagonal directions
            moves.update(self._traverse_left(row - 1, -1, -1, piece.color, left))  # Up-left
            moves.update(self._traverse_right(row - 1, -1, -1, piece.color, right))  # Up-right
            moves.update(self._traverse_left(row + 1, ROWS, 1, piece.color, left))  # Down-left
            moves.update(self._traverse_right(row + 1, ROWS, 1, piece.color, right))  # Down-right
        else:
            # Regular pieces can only move in their direction
            if piece.color == BLACK:
                moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
                moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
            if piece.color == WHITE:
                moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
                moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
            
            # Special case for water power - allow backward movement
            if piece.element_power == 'water' and not piece.power_used:
                # Add backward moves for water element
                if piece.color == BLACK:
                    moves.update(self._traverse_left(row + 1, min(row + 2, ROWS), 1, piece.color, left, is_water_move=True))
                    moves.update(self._traverse_right(row + 1, min(row + 2, ROWS), 1, piece.color, right, is_water_move=True))
                else:  # WHITE
                    moves.update(self._traverse_left(row - 1, max(row - 2, -1), -1, piece.color, left, is_water_move=True))
                    moves.update(self._traverse_right(row - 1, max(row - 2, -1), -1, piece.color, right, is_water_move=True))
        
        # Special case for air power - add extra diagonal jumps
        if piece.element_power == 'air' and not piece.power_used:
            air_moves = self._get_air_moves(piece)
            moves.update(air_moves)
            
        # Special case for fire power - add capture without move
        if piece.element_power == 'fire' and not piece.power_used:
            fire_moves = self._get_fire_moves(piece)
            moves.update(fire_moves)

        return moves
        
    def _get_fire_moves(self, piece):
        """Get valid moves for fire power (capture adjacent enemy without moving)"""
        fire_moves = {}
        directions = [
            (-1, -1), (-1, 1),  # Diagonals up
            (1, -1), (1, 1)     # Diagonals down
        ]
        
        # Check all adjacent squares for opponent pieces
        for dr, dc in directions:
            r, c = piece.row + dr, piece.col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                target = self.board[r][c]
                if target != 0 and target.color != piece.color:
                    # Fire power allows capturing without moving
                    # Use the piece's own position as the key and the target as the value
                    fire_moves[(piece.row, piece.col)] = [target]
                    
        return fire_moves

    def _get_air_moves(self, piece):
        """Get valid moves for air power (jump two squares diagonally)"""
        air_moves = {}
        directions = [
            (-2, -2), (-2, 2),  # Two squares diagonally up
            (2, -2), (2, 2)     # Two squares diagonally down
        ]
        
        # Only non-king pieces need extra air moves since kings can already move any distance
        if not piece.king:
            for dr, dc in directions:
                r, c = piece.row + dr, piece.col + dc
                
                # Check if the destination is on the board and empty
                if 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == 0:
                    # For regular pieces, respect direction constraints
                    if (piece.color == BLACK and dr < 0) or (piece.color == WHITE and dr > 0) or piece.king:
                        air_moves[(r, c)] = []  # No pieces are captured in this special move
        
        return air_moves
        
    def handle_earth_power(self, captor, captured_piece, destination):
        """Set up information for earth power logic"""
        self.pending_earth_power = {
            'captor': captor,
            'captured': captured_piece,
            'destination': destination
        }
        return True
        
    def execute_earth_power(self, use_power):
        """Execute earth power based on user choice"""
        if not self.pending_earth_power:
            return False
            
        captor = self.pending_earth_power['captor']
        captured = self.pending_earth_power['captured']
        dest_row, dest_col = self.pending_earth_power['destination']
        
        if use_power and captured.element_power == 'earth' and not captured.power_used:
            # Mark earth power as used
            captured.use_power()
            
            # Move the captor to the destination (jumping over the earth piece)
            self.board[captor.row][captor.col] = 0
            captor.move(dest_row, dest_col)
            self.board[dest_row][dest_col] = captor
            
            # No capture happens - earth piece remains in place
            result = True
        else:
            # Normal capture proceeds
            result = False
            
        # Reset pending earth power
        self.pending_earth_power = None
        return result