# main.py (remains unchanged)
import sys
import pygame
import chess
from chess_board import ChessBoard # Import your (now simpler) ChessBoard class
from piece import Piece # Import your custom Piece class
from utils import parse_move_input

# --- Configuration for Pygame (defined here for the main runner) ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
FPS = 30 # Frames per second

def run_game():
    """
    Main function to run the chess game loop, integrating Pygame and python-chess.
    """
    pygame.init() # Initialize all the Pygame modules
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Set up the display window
    pygame.display.set_caption("Python Chess Game") # Set window title
    clock = pygame.time.Clock() # To control the frame rate

    chess_game_board = ChessBoard() # Instantiate our ChessBoard wrapper

    running = True
    while running:
        # Event handling loop for Pygame window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # User clicked the close button
                running = False
            # Future phases: Handle MOUSEBUTTONDOWN events for piece selection and movement

        # --- Drawing the board ---
        screen.fill((0, 0, 0)) # Fill the screen with black background
        chess_game_board.draw_board(screen) # Draw the chessboard squares and pieces

        pygame.display.flip() # Update the full display Surface to the screen

        # --- Console-based interaction for moves (for now) ---
        # This part will be replaced by GUI interaction in later phases
        chess_game_board.display_text() # Show board state in console for current turn
        
        # Determine whose turn it is for console prompt
        current_turn_color = "White" if chess_game_board.board.turn == chess.WHITE else "Black"
        
        move_input = input(f"{current_turn_color}'s turn. Enter your move (UCI, e.g., e2e4) or 'quit': ").strip().lower()

        if move_input == 'quit':
            running = False # Set flag to exit Pygame loop
            print("Exiting game. Goodbye!")
            sys.exit() # Exit the script

        uci_move = parse_move_input(move_input)
        if uci_move:
            # Attempt to make the move using python-chess's validation
            if chess_game_board.move_piece(uci_move):
                print(f"Move '{uci_move}' made successfully.")
                # In later phases, you'd check for checkmate/stalemate here
                # after a successful move.
            else:
                print("Could not make the move. Please check the input and chess rules.")
        else:
            print("Invalid input. Please try again.")

        clock.tick(FPS) # Control the frame rate to limit CPU usage

    pygame.quit() # Uninitialize pygame modules gracefully

# --- Entry point of the script ---
if __name__ == "__main__":
    run_game()