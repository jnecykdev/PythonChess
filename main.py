import queue
import threading
import pygame
from chess_board import ChessBoard
from config import (
    BACKGROUND_COLOR,
    CLICK_MOVE_SUCCESS_MESSAGE,
    EXITING_GAME_MESSAGE,
    EXIT_ACTION,
    FPS,
    GAME_OVER_HELP_MESSAGE,
    GAME_OVER_MESSAGE,
    ILLEGAL_MOVE_MESSAGE,
    INVALID_INPUT_MESSAGE,
    LEFT_MOUSE_BUTTON,
    NEW_GAME_MESSAGE,
    QUIT_COMMAND,
    RESTART_COMMANDS,
    RESTART_ACTION,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SCROLL_DOWN_MOUSE_BUTTON,
    SCROLL_UP_MOUSE_BUTTON,
    TERMINAL_MOVE_PROMPT,
    TERMINAL_MOVE_SUCCESS_MESSAGE,
    TERMINAL_THREAD_JOIN_TIMEOUT,
    TURN_STATUS_MESSAGE,
    WINDOW_TITLE,
)
from utils import parse_move_input

def read_terminal_moves(move_queue, stop_event):
    """
    Reads terminal moves without blocking the Pygame window.
    """
    while not stop_event.is_set():
        try:
            move_input = input(TERMINAL_MOVE_PROMPT).strip().lower()
        except EOFError:
            break
        move_queue.put(move_input)
        if move_input == QUIT_COMMAND:
            break

def print_turn_status(chess_game_board):
    """
    Prints the board and current turn for terminal players.
    """
    chess_game_board.display_text()
    print(TURN_STATUS_MESSAGE.format(chess_game_board.game.turn_label()))

def print_game_result(chess_game_board):
    """
    Prints a game-over message when python-chess detects one.
    """
    if chess_game_board.board.is_game_over():
        print(GAME_OVER_MESSAGE.format(chess_game_board.board.result()))
        print(GAME_OVER_HELP_MESSAGE)

def run_game():
    """
    Main function to run the chess game loop, integrating Pygame and python-chess.
    """
    pygame.init() # Initialize all the Pygame modules
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Set up the display window
    pygame.display.set_caption(WINDOW_TITLE) # Set window title
    clock = pygame.time.Clock() # To control the frame rate

    chess_game_board = ChessBoard() # Instantiate our ChessBoard wrapper
    terminal_moves = queue.Queue()
    stop_terminal_input = threading.Event()
    terminal_thread = threading.Thread(
        target=read_terminal_moves,
        args=(terminal_moves, stop_terminal_input),
        daemon=True,
    )
    terminal_thread.start()

    print_turn_status(chess_game_board)

    running = True
    while running:
        # Event handling loop for Pygame window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # User clicked the close button
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                mouse_position = pygame.mouse.get_pos()
                chess_game_board.handle_scroll(event.y, mouse_position)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (
                SCROLL_UP_MOUSE_BUTTON,
                SCROLL_DOWN_MOUSE_BUTTON,
            ):
                scroll_steps = 1 if event.button == SCROLL_UP_MOUSE_BUTTON else -1
                chess_game_board.handle_scroll(scroll_steps, event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT_MOUSE_BUTTON:
                click_result = chess_game_board.handle_click(event.pos)
                if click_result == RESTART_ACTION:
                    chess_game_board.restart_game()
                    print(NEW_GAME_MESSAGE)
                    print_turn_status(chess_game_board)
                elif click_result == EXIT_ACTION:
                    running = False
                elif click_result:
                    print(CLICK_MOVE_SUCCESS_MESSAGE.format(click_result))
                    print_game_result(chess_game_board)
                    if not chess_game_board.board.is_game_over():
                        print_turn_status(chess_game_board)

        while not terminal_moves.empty():
            move_input = terminal_moves.get()

            if move_input == QUIT_COMMAND:
                running = False # Set flag to exit Pygame loop
                print(EXITING_GAME_MESSAGE)
                break
            if move_input in RESTART_COMMANDS:
                chess_game_board.restart_game()
                print(NEW_GAME_MESSAGE)
                print_turn_status(chess_game_board)
                continue

            uci_move = parse_move_input(move_input)
            if uci_move:
                # Attempt to make the move using python-chess's validation
                if chess_game_board.move_piece(uci_move):
                    print(TERMINAL_MOVE_SUCCESS_MESSAGE.format(uci_move))
                    print_game_result(chess_game_board)
                    if not chess_game_board.board.is_game_over():
                        print_turn_status(chess_game_board)
                else:
                    print(ILLEGAL_MOVE_MESSAGE)
            else:
                print(INVALID_INPUT_MESSAGE)

        # --- Drawing the board ---
        screen.fill(BACKGROUND_COLOR) # Fill the screen with black background
        chess_game_board.draw_board(screen) # Draw the chessboard squares and pieces

        pygame.display.flip() # Update the full display Surface to the screen

        clock.tick(FPS) # Control the frame rate to limit CPU usage

    stop_terminal_input.set()
    terminal_thread.join(timeout=TERMINAL_THREAD_JOIN_TIMEOUT)
    pygame.quit() # Uninitialize pygame modules gracefully

# --- Entry point of the script ---
if __name__ == "__main__":
    run_game()
