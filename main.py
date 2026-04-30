import queue
import threading
import pygame
import chess
from chess_board import ChessBoard # Import your (now simpler) ChessBoard class
from utils import parse_move_input

# --- Configuration for Pygame (defined here for the main runner) ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
FPS = 30 # Frames per second

def read_terminal_moves(move_queue):
    """
    Reads terminal moves without blocking the Pygame window.
    """
    while True:
        try:
            move_input = input("Terminal move (UCI, e.g., e2e4) or 'quit': ").strip().lower()
        except EOFError:
            break
        move_queue.put(move_input)
        if move_input == "quit":
            break

def print_turn_status(chess_game_board):
    """
    Prints the board and current turn for terminal players.
    """
    chess_game_board.display_text()
    current_turn_color = "White" if chess_game_board.board.turn == chess.WHITE else "Black"
    print(f"{current_turn_color}'s turn. Click a piece or enter a move in the terminal.")

def print_game_result(chess_game_board):
    """
    Prints a game-over message when python-chess detects one.
    """
    if chess_game_board.board.is_game_over():
        print(f"Game over: {chess_game_board.board.result()}")

def run_game():
    """
    Main function to run the chess game loop, integrating Pygame and python-chess.
    """
    pygame.init() # Initialize all the Pygame modules
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Set up the display window
    pygame.display.set_caption("Python Chess Game") # Set window title
    clock = pygame.time.Clock() # To control the frame rate

    chess_game_board = ChessBoard() # Instantiate our ChessBoard wrapper
    terminal_moves = queue.Queue()
    terminal_thread = threading.Thread(target=read_terminal_moves, args=(terminal_moves,), daemon=True)
    terminal_thread.start()

    print_turn_status(chess_game_board)

    running = True
    while running:
        # Event handling loop for Pygame window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # User clicked the close button
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                move_uci = chess_game_board.handle_click(event.pos)
                if move_uci:
                    print(f"Move '{move_uci}' made successfully by click.")
                    print_game_result(chess_game_board)
                    if not chess_game_board.board.is_game_over():
                        print_turn_status(chess_game_board)

        while not terminal_moves.empty():
            move_input = terminal_moves.get()

            if move_input == 'quit':
                running = False # Set flag to exit Pygame loop
                print("Exiting game. Goodbye!")
                break

            uci_move = parse_move_input(move_input)
            if uci_move:
                # Attempt to make the move using python-chess's validation
                if chess_game_board.move_piece(uci_move):
                    print(f"Move '{uci_move}' made successfully.")
                    print_game_result(chess_game_board)
                    if not chess_game_board.board.is_game_over():
                        print_turn_status(chess_game_board)
                else:
                    print("Could not make the move. Please check the input and chess rules.")
            else:
                print("Invalid input. Please try again.")

        # --- Drawing the board ---
        screen.fill((0, 0, 0)) # Fill the screen with black background
        chess_game_board.draw_board(screen) # Draw the chessboard squares and pieces

        pygame.display.flip() # Update the full display Surface to the screen

        clock.tick(FPS) # Control the frame rate to limit CPU usage

    pygame.quit() # Uninitialize pygame modules gracefully

# --- Entry point of the script ---
if __name__ == "__main__":
    run_game()
