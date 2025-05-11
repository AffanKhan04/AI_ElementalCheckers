import pygame
from checkers.constants import WIDTH, HEIGHT, BOARD_HEIGHT, INFO_HEIGHT, SQUARE_SIZE, BLACK, WHITE, CREAM, BROWN, \
    LIGHT_GREY, ELEMENTS
from checkers.game import Game
from minimax.algorithm import minimax
import sys

FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Elemental Checkers')


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    # Only register clicks within the board area
    if row < 8 and col < 8:
        return row, col
    return None, None

def draw_menu(win):
    """Draw the initial menu screen with game mode options"""
    # Initialize fonts
    title_font = pygame.font.SysFont('Arial', 48)
    option_font = pygame.font.SysFont('Arial', 32)
    instruction_font = pygame.font.SysFont('Arial', 24)

    # Fill background
    win.fill(CREAM)

    # Draw checkerboard pattern in background
    for row in range(8):
        for col in range(row % 2, 8, 2):
            pygame.draw.rect(win, BROWN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Draw semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 200))  # White with alpha
    win.blit(overlay, (0, 0))

    # Draw title
    title = title_font.render("ELEMENTAL CHECKERS", True, (0, 0, 0))
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    # Draw game mode options
    mode_text = option_font.render("Select Game Mode:", True, (0, 0, 0))
    win.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, 200))

    # Human vs AI button
    pygame.draw.rect(win, (200, 200, 200), (WIDTH // 2 - 150, 250, 300, 50))
    ai_text = option_font.render("Human vs AI", True, (0, 0, 0))
    win.blit(ai_text, (WIDTH // 2 - ai_text.get_width() // 2, 260))

    # Human vs Human button
    pygame.draw.rect(win, (200, 200, 200), (WIDTH // 2 - 150, 320, 300, 50))
    human_text = option_font.render("Human vs Human", True, (0, 0, 0))
    win.blit(human_text, (WIDTH // 2 - human_text.get_width() // 2, 330))

    # Draw instructions
    instructions = instruction_font.render("Choose a game mode to begin", True, (0, 0, 0))
    win.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 400))

    # Draw version information and credits
    version_text = instruction_font.render("Version 1.0", True, (0, 0, 0))
    win.blit(version_text, (WIDTH - version_text.get_width() - 20, HEIGHT - version_text.get_height() - 20))

    return {
        'ai_button': pygame.Rect(WIDTH // 2 - 150, 250, 300, 50),
        'human_button': pygame.Rect(WIDTH // 2 - 150, 320, 300, 50)
    }


def draw_difficulty_menu(win):
    """Draw the AI difficulty selection menu"""
    # Initialize fonts
    title_font = pygame.font.SysFont('Arial', 48)
    option_font = pygame.font.SysFont('Arial', 32)
    instruction_font = pygame.font.SysFont('Arial', 24)

    # Fill background
    win.fill(CREAM)

    # Draw checkerboard pattern in background
    for row in range(8):
        for col in range(row % 2, 8, 2):
            pygame.draw.rect(win, BROWN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Draw semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 200))  # White with alpha
    win.blit(overlay, (0, 0))

    # Draw title
    title = title_font.render("Select AI Difficulty", True, (0, 0, 0))
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    difficulty_buttons = {}
    difficulty_labels = ["Easy", "Medium", "Hard"]

    for i, label in enumerate(difficulty_labels):
        button_rect = pygame.Rect(WIDTH // 2 - 100, 200 + (i * 80), 200, 50)
        pygame.draw.rect(win, (200, 200, 200), button_rect)

        text = option_font.render(label, True, (0, 0, 0))
        win.blit(text, (WIDTH // 2 - text.get_width() // 2, 210 + (i * 80)))

        difficulty_buttons[label] = button_rect

    instructions = instruction_font.render("Choose a difficulty level", True, (0, 0, 0))
    win.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 450))

    # Add back button
    back_button = pygame.Rect(20, HEIGHT - 60, 100, 40)
    pygame.draw.rect(win, (200, 200, 200), back_button)
    back_text = instruction_font.render("Back", True, (0, 0, 0))
    win.blit(back_text, (20 + (100 - back_text.get_width()) // 2, HEIGHT - 60 + (40 - back_text.get_height()) // 2))
    
    difficulty_buttons['back'] = back_button

    return difficulty_buttons


def draw_info_panel(win, ai_mode, current_player, game_over=False, fire_active=False):
    """Draw the information panel below the game board"""
    # Draw background for info panel
    pygame.draw.rect(win, LIGHT_GREY, (0, BOARD_HEIGHT, WIDTH, INFO_HEIGHT))

    # Draw a separator line
    pygame.draw.line(win, BLACK, (0, BOARD_HEIGHT), (WIDTH, BOARD_HEIGHT), 2)

    # Initialize font
    info_font = pygame.font.SysFont('Arial', 20)

    # Show game mode
    if ai_mode:
        mode_text = info_font.render("Mode: Human (Black) vs AI (White)", True, BLACK)
    else:
        mode_text = info_font.render("Mode: Human vs Human", True, BLACK)

    win.blit(mode_text, (20, BOARD_HEIGHT + 15))

    # Show current player's turn
    if not game_over:
        turn_text = info_font.render(f"Current turn: {current_player}", True, BLACK)
        win.blit(turn_text, (20, BOARD_HEIGHT + 45))

    # Show fire ability hint if active
    if fire_active:
        fire_text = info_font.render("Fire power ready! Click piece again to capture adjacent enemy", True, (255, 0, 0))
        win.blit(fire_text, (20, BOARD_HEIGHT + 65))

    # Show restart instruction
    restart_text = info_font.render("Press R to restart game", True, BLACK)
    win.blit(restart_text, (WIDTH - 200, BOARD_HEIGHT + 15))
    
    # Show menu instruction
    menu_text = info_font.render("Press M for main menu", True, BLACK)
    win.blit(menu_text, (WIDTH - 200, BOARD_HEIGHT + 45))


def draw_help_screen(win):
    """Draw the help screen with game rules and element powers"""
    # Initialize fonts
    title_font = pygame.font.SysFont('Arial', 36)
    subtitle_font = pygame.font.SysFont('Arial', 28)
    content_font = pygame.font.SysFont('Arial', 20)

    # Fill background
    win.fill(CREAM)

    # Draw semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 240))  # White with alpha
    win.blit(overlay, (0, 0))

    # Draw title
    title = title_font.render("ELEMENTAL CHECKERS GUIDE", True, (0, 0, 0))
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    # Draw basic rules
    rules_title = subtitle_font.render("Basic Rules:", True, (0, 0, 0))
    win.blit(rules_title, (50, 80))

    rules = [
        "• Standard checkers rules apply",
        "• Capture is mandatory when available",
        "• Pieces promote to kings when reaching the opposite end",
        "• Kings can move diagonally in any direction",
        "• Each piece has a random elemental power (can be used once)"
    ]

    for i, rule in enumerate(rules):
        rule_text = content_font.render(rule, True, (0, 0, 0))
        win.blit(rule_text, (70, 120 + i * 25))

    # Draw elemental powers
    powers_title = subtitle_font.render("Elemental Powers:", True, (0, 0, 0))
    win.blit(powers_title, (50, 250))

    powers = [
        "• Fire: Capture an adjacent enemy piece without moving (click piece twice)",
        "• Water: Move backward (regular pieces can normally only move forward)",
        "• Air: Jump two squares diagonally in one move",
        "• Earth: Avoid being captured when an opponent tries to jump over you"
    ]

    for i, power in enumerate(powers):
        power_text = content_font.render(power, True, (0, 0, 0))
        win.blit(power_text, (70, 290 + i * 25))

    # Draw controls
    controls_title = subtitle_font.render("Controls:", True, (0, 0, 0))
    win.blit(controls_title, (50, 420))

    controls = [
        "• Click to select and move pieces",
        "• Click a piece with fire power twice to use it",
        "• R: Restart game",
        "• M: Return to main menu",
        "• H: Show this help screen",
        "• Esc: Exit game"
    ]

    for i, control in enumerate(controls):
        control_text = content_font.render(control, True, (0, 0, 0))
        win.blit(control_text, (70, 460 + i * 25))

    # Add back button
    back_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 60, 150, 40)
    pygame.draw.rect(win, (200, 200, 200), back_button)
    back_text = content_font.render("Back to Game", True, (0, 0, 0))
    win.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 60 + (40 - back_text.get_height()) // 2))

    return back_button


def menu_screen():
    """Show the menu screen and get player choices"""
    pygame.font.init()
    clock = pygame.time.Clock()

    # First menu - game mode selection
    buttons = draw_menu(WIN)
    pygame.display.update()

    # Game settings
    ai_mode = None
    ai_depth = None

    # Menu state
    menu_state = "main"  # Can be "main" or "difficulty"

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if menu_state == "main":
                    if buttons['ai_button'].collidepoint(mouse_pos):
                        ai_mode = True
                        menu_state = "difficulty"
                        difficulty_buttons = draw_difficulty_menu(WIN)
                        pygame.display.update()

                    elif buttons['human_button'].collidepoint(mouse_pos):
                        ai_mode = False
                        running = False  # Exit menu and start game

                elif menu_state == "difficulty":
                    if 'back' in difficulty_buttons and difficulty_buttons['back'].collidepoint(mouse_pos):
                        menu_state = "main"
                        buttons = draw_menu(WIN)
                        pygame.display.update()
                        continue
                        
                    for difficulty, button in difficulty_buttons.items():
                        if difficulty != 'back' and button.collidepoint(mouse_pos):
                            if difficulty == "Easy":
                                ai_depth = 1
                            elif difficulty == "Medium":
                                ai_depth = 2
                            else:  # Hard
                                ai_depth = 5
                            running = False  # Exit menu and start game

    return ai_mode, ai_depth


def main():
    # Initialize pygame
    pygame.init()
    
    # Show menu and get settings
    ai_mode, ai_depth = menu_screen()

    # Default AI depth if somehow skipped
    if ai_mode and ai_depth is None:
        ai_depth = 2

    # Initialize game
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    # Game state
    game_over = False
    show_help = False

    # Text rendering setup
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 32)
    small_font = pygame.font.SysFont('Arial', 20)


    while run:
        clock.tick(FPS)

        # Check for winner
        winner = game.winner()
        if winner is not None and not game_over:
            game_over = True
            winner_text = f"{'Black' if winner == BLACK else 'White'} Wins!"
            text_surface = font.render(winner_text, True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, BOARD_HEIGHT // 2))
            restart_text = small_font.render("Press R to restart", True, (0, 0, 0))
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, BOARD_HEIGHT // 2 + 40))

        # Handle Earth power dialog if active
        if game.earth_power_active:
            yes_button, no_button = game.draw_earth_power_dialog(WIN)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if yes_button.collidepoint(mouse_pos):
                        game.handle_earth_power_choice(True)
                    elif no_button.collidepoint(mouse_pos):
                        game.handle_earth_power_choice(False)
            # Skip the rest of the loop while dialog is active
            pygame.display.update()
            continue

        # Show help screen if active
        if show_help:
            back_button = draw_help_screen(WIN)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h or event.key == pygame.K_ESCAPE:
                        show_help = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if back_button.collidepoint(mouse_pos):
                        show_help = False
            pygame.display.update()
            continue

        # AI move when it's white's turn, game is not over, and in AI mode
        if game.turn == WHITE and not game_over and ai_mode:
            # Display "AI thinking..." text in the info panel
            game.update()
            # Draw info panel with AI thinking message
            draw_info_panel(WIN, ai_mode, "White (AI thinking...)", game_over)
            pygame.display.update()

            # Run minimax with alpha-beta pruning
            value, new_board = minimax(game.get_board(), ai_depth, True, game)
            game.ai_move(new_board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # Restart game with R key
                if event.key == pygame.K_r:
                    game.reset()
                    game_over = False
                # Return to main menu with M key
                elif event.key == pygame.K_m:
                    return main()
                # Show help screen with H key
                elif event.key == pygame.K_h:
                    show_help = True
                # Exit game with Esc key
                elif event.key == pygame.K_ESCAPE:
                    if show_help:
                        show_help = False
                    else:
                        run = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not show_help:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)

                # Only process clicks on the board
                if row is not None and col is not None:
                    # In AI mode, only allow BLACK pieces to be moved by player
                    if ai_mode:
                        if game.turn == BLACK:
                            game.select(row, col)
                    # In human vs human mode, allow either player to move on their turn
                    else:
                        game.select(row, col)

        # Update game board
        game.update()

        # Display current mode and player turn in info panel
        current_player = "Black" if game.turn == BLACK else "White"
        draw_info_panel(WIN, ai_mode, current_player, game_over)

        # Draw winner text if game is over
        if game_over:
            WIN.blit(text_surface, text_rect)
            WIN.blit(restart_text, restart_rect)

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()