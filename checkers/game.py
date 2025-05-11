import pygame
from .constants import WHITE, BLUE, SQUARE_SIZE, BLACK, RED, WIDTH, BOARD_HEIGHT


class Game:
    def __init__(self, win):
        """Initialize the game with the given window"""
        self.win = win
        self._init()

    def update(self):
        """Update the game display"""
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        """Initialize game state variables"""
        from .board import Board  # Import here to avoid circular imports
        self.selected = None
        self.board = Board()
        self.turn = BLACK
        self.valid_moves = {}
        self.forced_capture = False  # Track if there's a forced capture
        self.last_move = None  # Track the last move for highlight
        self.power_dialog_active = False  # Track if we're showing a power dialog
        self.earth_power_active = False  # Track if earth power is being used
        # Track if a piece with fire ability was previously selected
        self.fire_piece_selected = False

    def reset(self):
        """Reset the game to initial state"""
        self._init()

    def winner(self):
        """Check if there's a winner"""
        return self.board.winner()

    def select(self, row, col):
        """Select a piece or a destination for the selected piece"""
        # If we're in the middle of an earth power decision, handle that first
        if self.earth_power_active:
            return False
            
        # Get the piece at the clicked position
        clicked_piece = self.board.get_piece(row, col)
        
        # Check if we already have a piece selected
        if self.selected:
            # Check if player clicked on the same piece with fire ability
            if (clicked_piece == self.selected and clicked_piece.element_power == 'fire' 
                    and not clicked_piece.power_used):
                # If this is the second click on the fire piece, activate fire ability
                if self.fire_piece_selected:
                    self._use_fire_ability(row, col)
                    return True
                else:
                    # First click on fire piece, mark it for potential fire ability activation
                    self.fire_piece_selected = True
                    return True
            else:
                # Reset fire piece selection flag if clicked elsewhere
                self.fire_piece_selected = False
                
            # Try to move the selected piece to (row, col)
            result = self._move(row, col)
            if not result:
                # If move failed, deselect and try to select again
                self.selected = None
                self.select(row, col)
                
        # If no piece is selected, try to select one
        if clicked_piece != 0 and clicked_piece.color == self.turn:
            # Check if there are any capture moves available for any piece
            all_pieces = self.board.get_all_pieces(self.turn)
            capture_available = False

            for p in all_pieces:
                moves = self.board.get_valid_moves(p)
                if any(len(skipped) > 0 and not isinstance(skipped[-1], str) for skipped in moves.values()):
                    capture_available = True
                    break

            # If capture is available, only allow selecting pieces that can capture
            if capture_available:
                moves = self.board.get_valid_moves(clicked_piece)
                if any(len(skipped) > 0 and not isinstance(skipped[-1], str) for skipped in moves.values()):
                    self.selected = clicked_piece
                    self.valid_moves = moves
                    # Reset fire piece selection flag when selecting a new piece
                    self.fire_piece_selected = False
                    return True
                else:
                    # Cannot select this piece if it can't capture
                    return False
            else:
                # No captures available, can select any piece
                self.selected = clicked_piece
                self.valid_moves = self.board.get_valid_moves(clicked_piece)
                # Reset fire piece selection flag when selecting a new piece
                self.fire_piece_selected = False
                return True

        return False

    def _use_fire_ability(self, row, col):
        """Activate fire ability to capture adjacent enemies without moving"""
        if not self.selected or self.selected.element_power != 'fire' or self.selected.power_used:
            return False

        # Get fire capture moves
        fire_key = (self.selected.row, self.selected.col)
        if fire_key in self.valid_moves:
            skipped = self.valid_moves[fire_key]
            if skipped:  # If there are pieces to capture
                self.selected.use_power()
                self.board.remove(skipped)
                self.change_turn()
                self.last_move = (fire_key, fire_key)  # Same position for fire power
                # Reset fire piece selection flag
                self.fire_piece_selected = False
                return True

        return False

    def _move(self, row, col):
        """Move the selected piece to the given position if valid"""
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            # Store the starting position for highlighting
            start_pos = (self.selected.row, self.selected.col)
            skipped = self.valid_moves[(row, col)]
            
            # Check if this is a special power move
            is_special_move = False
            
            # Handle water power (backward move)
            if skipped and isinstance(skipped[-1], str) and skipped[-1] == 'water_move':
                if self.selected.element_power == 'water' and not self.selected.power_used:
                    self.selected.use_power()
                    skipped.pop()  # Remove the water_move marker
                    is_special_move = True
            
            # Handle fire power (capture without moving) - this is now handled in _use_fire_ability
            
            # Handle air power (long jump)
            if len(skipped) == 0:
                # Calculate Manhattan distance to see if it's a special air move
                distance = abs(row - self.selected.row) + abs(col - self.selected.col)
                if distance == 4:  # Air move (2 squares diagonally)
                    if self.selected.element_power == 'air' and not self.selected.power_used:
                        self.selected.use_power()
                        self.board.move(self.selected, row, col)
                        self.change_turn()
                        self.last_move = (start_pos, (row, col))
                        # Reset fire piece selection flag
                        self.fire_piece_selected = False
                        return True
            
            # Before proceeding with a capture move, check if the target piece has earth power
            if skipped and not is_special_move:
                target_piece = skipped[0]  # Get the piece to be captured
                if target_piece.element_power == 'earth' and not target_piece.power_used:
                    # Set up earth power dialog
                    self.earth_power_active = True
                    self.board.handle_earth_power(self.selected, target_piece, (row, col))
                    # Reset fire piece selection flag
                    self.fire_piece_selected = False
                    # Defer the actual move until the user decides
                    return True
            
            # Regular move
            self.board.move(self.selected, row, col)
            
            # If this move captured any pieces, remove them
            if skipped and not is_special_move:
                self.board.remove(skipped)

                # Check if additional captures are available with this piece
                self.selected.move(row, col)  # Update piece position
                additional_moves = self.board.get_valid_moves(self.selected)

                # Only consider additional captures with non-special moves
                valid_additional = {}
                for move_pos, skipped_pieces in additional_moves.items():
                    if skipped_pieces and not isinstance(skipped_pieces[-1], str):
                        valid_additional[move_pos] = skipped_pieces

                if valid_additional:
                    # Additional captures available - don't change turn yet
                    self.valid_moves = valid_additional
                    self.last_move = ((start_pos), (row, col))
                    # Reset fire piece selection flag
                    self.fire_piece_selected = False
                    return True

            # No more captures available, change turn
            self.change_turn()
            # Record the move for highlighting
            self.last_move = ((start_pos), (row, col))
            # Reset fire piece selection flag
            self.fire_piece_selected = False
            return True

        return False
        
    def handle_earth_power_choice(self, use_power):
        """Handle the user's choice about using earth power"""
        if self.earth_power_active:
            # Execute the earth power logic
            self.board.execute_earth_power(use_power)
            self.earth_power_active = False
            # Change turn after the interaction
            self.change_turn()
            return True
        return False

    def draw_valid_moves(self, moves):
        """Draw valid move indicators"""
        for move in moves:
            row, col = move
            # Special indicator for fire ability (when clicking on the same piece)
            if self.selected and (row, col) == (self.selected.row, self.selected.col):
                if self.selected.element_power == 'fire' and not self.selected.power_used:
                    # Draw a red circle to indicate fire ability is available
                    pygame.draw.circle(
                        self.win, RED,
                        (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                        15
                    )
                    # If this piece is marked for fire ability (clicked once), add a visual indicator
                    if self.fire_piece_selected:
                        pygame.draw.circle(
                            self.win, RED,
                            (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                            20, 3  # Larger outline circle
                        )
            else:
                pygame.draw.circle(
                    self.win, BLUE,
                    (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                    15
                )

        # Highlight the last move
        if self.last_move:
            start, end = self.last_move
            # Draw slightly transparent red rectangle for start position
            s_row, s_col = start
            e_row, e_col = end

            # Create transparent surface for highlighting
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_surface.fill((255, 0, 0, 80))  # Semi-transparent red

            # Draw highlight for start and end positions
            self.win.blit(highlight_surface, (s_col * SQUARE_SIZE, s_row * SQUARE_SIZE))
            self.win.blit(highlight_surface, (e_col * SQUARE_SIZE, e_row * SQUARE_SIZE))

    def change_turn(self):
        self.valid_moves = {}
        self.selected = None
        self.fire_piece_selected = False
        self.turn = WHITE if self.turn == BLACK else BLACK

    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        self.change_turn()

    def draw_earth_power_dialog(self, win):
        """Draw dialog asking if the player wants to use earth power"""
        if not self.earth_power_active:
            return None, None
            
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        win.blit(overlay, (0, 0))
        
        # Create the dialog box
        dialog_width, dialog_height = 400, 200
        dialog_x = (WIDTH - dialog_width) // 2
        dialog_y = (BOARD_HEIGHT - dialog_height) // 2
        
        # Draw dialog background
        pygame.draw.rect(win, (220, 220, 220), (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(win, (0, 0, 0), (dialog_x, dialog_y, dialog_width, dialog_height), 2)
        
        # Setup font
        font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 20)
        
        # Draw message
        message = "Your piece is being captured!"
        text = font.render(message, True, (0, 0, 0))
        win.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, dialog_y + 30))
        
        message2 = "Use Earth power to avoid capture?"
        text2 = small_font.render(message2, True, (0, 0, 0))
        win.blit(text2, (dialog_x + (dialog_width - text2.get_width()) // 2, dialog_y + 70))
        
        # Draw description
        description = "Earth power allows a piece to avoid being captured"
        desc_text = small_font.render(description, True, (0, 0, 0))
        win.blit(desc_text, (dialog_x + (dialog_width - desc_text.get_width()) // 2, dialog_y + 100))
        
        # Draw yes button
        yes_button_width, yes_button_height = 100, 40
        yes_button_x = dialog_x + (dialog_width // 3) - (yes_button_width // 2)
        yes_button_y = dialog_y + 140
        
        yes_button = pygame.Rect(yes_button_x, yes_button_y, yes_button_width, yes_button_height)
        pygame.draw.rect(win, (100, 200, 100), yes_button)  # Green button
        pygame.draw.rect(win, (0, 0, 0), yes_button, 2)     # Black border
        
        yes_text = font.render("Yes", True, (0, 0, 0))
        win.blit(yes_text, (yes_button_x + (yes_button_width - yes_text.get_width()) // 2, 
                          yes_button_y + (yes_button_height - yes_text.get_height()) // 2))
        
        # Draw no button
        no_button_width, no_button_height = 100, 40
        no_button_x = dialog_x + (2 * dialog_width // 3) - (no_button_width // 2)
        no_button_y = dialog_y + 140
        
        no_button = pygame.Rect(no_button_x, no_button_y, no_button_width, no_button_height)
        pygame.draw.rect(win, (200, 100, 100), no_button)  # Red button
        pygame.draw.rect(win, (0, 0, 0), no_button, 2)     # Black border
        
        no_text = font.render("No", True, (0, 0, 0))
        win.blit(no_text, (no_button_x + (no_button_width - no_text.get_width()) // 2, 
                         no_button_y + (no_button_height - no_text.get_height()) // 2))
        
        return yes_button, no_button