import chess

from config import (
    BOARD_SIZE,
    BOARD_PIXEL_SIZE,
    DEFAULT_PROMOTION_PIECE,
    PROMOTION_RANKS,
    SQUARE_SIZE,
)


class ClickController:
    """
    Converts board clicks into piece selection and legal moves.
    """

    def __init__(self, game, promotion_piece=DEFAULT_PROMOTION_PIECE):
        """
        Creates click state for a game and default GUI promotion piece.
        """
        self.game = game
        self.promotion_piece = promotion_piece
        self.selected_square = None
        self.legal_destinations = set()
        self.move_categories = {}

    def screen_square(self, position):
        """
        Converts a screen pixel position to a python-chess square.
        """
        x, y = position
        if not (0 <= x < BOARD_PIXEL_SIZE and 0 <= y < BOARD_PIXEL_SIZE):
            return None

        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE
        return chess.square(col, BOARD_SIZE - 1 - row)

    def select_square(self, square):
        """
        Selects a piece and stores its legal destination squares.
        """
        self.selected_square = square
        self.move_categories = self.game.move_categories_from(square)
        self.legal_destinations = set(self.move_categories)

    def clear_selection(self):
        """
        Clears any GUI selection and legal-move highlights.
        """
        self.selected_square = None
        self.legal_destinations = set()
        self.move_categories = {}

    def _promotion_piece(self, move):
        """
        Returns the configured GUI promotion piece for pawn promotions.
        """
        piece = self.game.board.piece_at(move.from_square)
        if (
            piece
            and piece.piece_type == chess.PAWN
            and chess.square_rank(move.to_square) in PROMOTION_RANKS
        ):
            return self.promotion_piece
        return None

    def _legal_click_move(self, from_square, to_square):
        """
        Finds the legal move matching a GUI click.
        """
        for move in self.game.legal_moves_from(from_square):
            if move.to_square != to_square:
                continue

            promotion = self._promotion_piece(move)
            if promotion is None or move.promotion == promotion:
                return move

        return None

    def handle_click(self, position):
        """
        Handles a GUI click and returns the move UCI when a move is made.
        """
        if self.game.board.is_game_over():
            self.clear_selection()
            return None

        clicked_square = self.screen_square(position)
        if clicked_square is None:
            self.clear_selection()
            return None

        clicked_piece = self.game.board.piece_at(clicked_square)
        if self.selected_square is None:
            if clicked_piece and clicked_piece.color == self.game.board.turn:
                self.select_square(clicked_square)
            return None

        if clicked_square == self.selected_square:
            self.clear_selection()
            return None

        if clicked_piece and clicked_piece.color == self.game.board.turn:
            self.select_square(clicked_square)
            return None

        move = self._legal_click_move(self.selected_square, clicked_square)
        if move:
            self.game.push_move(move)
            self.clear_selection()
            return move.uci()

        self.clear_selection()
        return None
