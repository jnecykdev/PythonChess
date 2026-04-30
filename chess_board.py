from board_renderer import BoardRenderer
from chess_game import ChessGame
from click_controller import ClickController
from config import DEFAULT_PROMOTION_PIECE, DEFAULT_SAVE_FILENAME


class ChessBoard:
    """
    Facade that coordinates chess state, rendering, and click interaction.
    """

    def __init__(self, promotion_piece=DEFAULT_PROMOTION_PIECE):
        """
        Initializes the game, renderer, and click controller.
        """
        self.promotion_piece = promotion_piece
        self.game = ChessGame()
        self.renderer = BoardRenderer()
        self.click_controller = ClickController(self.game, promotion_piece)

    @property
    def board(self):
        """
        Exposes the underlying python-chess board for compatibility.
        """
        return self.game.board

    @board.setter
    def board(self, board):
        """
        Replaces the underlying board and keeps controllers in sync.
        """
        self.game.board = board
        self.clear_selection()

    @property
    def piece_images(self):
        """
        Exposes loaded piece images for tests and compatibility.
        """
        return self.renderer.piece_images

    @property
    def selected_square(self):
        """
        Exposes the currently selected GUI square.
        """
        return self.click_controller.selected_square

    @property
    def legal_destinations(self):
        """
        Exposes GUI legal destination highlights.
        """
        return self.click_controller.legal_destinations

    @property
    def move_categories(self):
        """
        Exposes GUI legal destination categories.
        """
        return self.click_controller.move_categories

    def _square_rect(self, row, col):
        """
        Returns the screen-space rectangle for a board square.
        """
        return self.renderer.square_rect(row, col)

    def _board_square(self, row, col):
        """
        Converts a screen row/column to a python-chess square.
        """
        return self.renderer.board_square(row, col)

    def _screen_square(self, position):
        """
        Converts a screen pixel position to a python-chess square.
        """
        return self.click_controller.screen_square(position)

    def _legal_moves_from(self, square):
        """
        Returns all legal moves from the given square.
        """
        return self.game.legal_moves_from(square)

    def clear_selection(self):
        """
        Clears any GUI selection and legal-move highlights.
        """
        self.click_controller.clear_selection()

    def handle_click(self, position):
        """
        Handles a GUI click on the board.
        """
        if self.board.is_game_over():
            action = self.renderer.game_over_action_at(position)
            if action:
                return action
        move_uci = self.click_controller.handle_click(position)
        if move_uci:
            self.renderer.reset_move_history_scroll()
        return move_uci

    def handle_scroll(self, steps, position):
        """
        Scrolls side-panel move history when the pointer is over it.
        """
        if self.renderer.history_contains(position):
            self.renderer.scroll_move_history(steps)
            return True
        return False

    def restart_game(self):
        """
        Resets the board and interaction state for a new game.
        """
        self.game = ChessGame()
        self.click_controller = ClickController(self.game, self.promotion_piece)
        self.renderer.reset_move_history_scroll()

    def display_text(self):
        """
        Prints the current state of the chess board to the console.
        """
        print("\n" + str(self.board) + "\n")

    def draw_board(self, screen):
        """
        Draws the chessboard squares and pieces using Pygame.
        """
        self.renderer.draw(
            screen,
            self.game,
            self.selected_square,
            self.move_categories,
        )

    def move_piece(self, move_uci):
        """
        Attempts to make a terminal UCI move and clears GUI selection on success.
        """
        if self.game.move_uci(move_uci):
            self.clear_selection()
            self.renderer.reset_move_history_scroll()
            return True
        return False

    def save_game_state(self, filename=DEFAULT_SAVE_FILENAME):
        """
        Saves the current board position and active turn to a JSON file.
        """
        self.game.save_game_state(filename)

    def load_game_state(self, filename=DEFAULT_SAVE_FILENAME):
        """
        Loads a saved board position and active turn from a JSON file.
        """
        loaded = self.game.load_game_state(filename)
        if loaded:
            self.clear_selection()
        return loaded


__all__ = [
    "BoardRenderer",
    "ChessBoard",
    "ChessGame",
    "ClickController",
]
