import json

import chess
import pygame

from config import (
    ASSETS_DIR,
    BOARD_SIZE,
    DARK_SQUARE_COLOR,
    DEFAULT_PROMOTION_PIECE,
    HIGHLIGHT_ALPHA,
    LEGAL_CAPTURE_COLOR,
    LEGAL_MOVE_COLOR,
    LIGHT_SQUARE_COLOR,
    PIECE_SCALE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SELECTED_SQUARE_COLOR,
    SQUARE_SIZE,
)
from piece import Piece


class ChessGame:
    """
    Owns chess rules, board state, legal move lookup, and save/load behavior.
    """

    def __init__(self, board=None):
        """
        Creates a game with a standard board unless an existing board is given.
        """
        self.board = board or chess.Board()

    def legal_moves_from(self, square):
        """
        Returns all legal moves that start from the given square.
        """
        return [move for move in self.board.legal_moves if move.from_square == square]

    def move_uci(self, move_uci):
        """
        Attempts to push a move in UCI format and returns whether it succeeded.
        """
        try:
            self.board.push_uci(move_uci)
            return True
        except ValueError as e:
            print(f"Illegal move: {e}")
            return False

    def push_move(self, move):
        """
        Pushes an already validated python-chess move object.
        """
        self.board.push(move)

    def save_game_state(self, filename="chess_game.json"):
        """
        Saves the current board position and active turn to a JSON file.
        """
        game_state = {
            "fen": self.board.fen(),
            "turn": self.board.turn == chess.WHITE,
        }
        with open(filename, "w") as f:
            json.dump(game_state, f, indent=4)
        print(f"Game saved to {filename}")

    def load_game_state(self, filename="chess_game.json"):
        """
        Loads a saved board position and active turn from a JSON file.
        """
        try:
            with open(filename, "r") as f:
                game_state = json.load(f)
            self.board = chess.Board(game_state["fen"])
            self.board.turn = chess.WHITE if game_state["turn"] else chess.BLACK
            print(f"Game loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"Error: Save file '{filename}' not found.")
            return False
        except Exception as e:
            print(f"Error loading game: {e}")
            return False


class BoardRenderer:
    """
    Handles Pygame image loading and drawing for the chessboard.
    """

    def __init__(self):
        """
        Initializes piece images and reusable highlight overlays.
        """
        self.piece_images = {}
        self.move_highlight = self._create_highlight_overlay(LEGAL_MOVE_COLOR)
        self.capture_highlight = self._create_highlight_overlay(LEGAL_CAPTURE_COLOR)
        pygame.font.init()
        self._load_piece_images()

    def _create_highlight_overlay(self, color):
        """
        Creates a cached transparent overlay for highlighted board squares.
        """
        overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        overlay.fill((*color, HIGHLIGHT_ALPHA))
        return overlay

    def _load_piece_images(self):
        """
        Loads all chess piece images from the assets directory.
        """
        all_piece_configs = []
        for color_val in [chess.WHITE, chess.BLACK]:
            for piece_type_val in [
                chess.PAWN,
                chess.ROOK,
                chess.KNIGHT,
                chess.BISHOP,
                chess.QUEEN,
                chess.KING,
            ]:
                custom_piece = Piece(color_val, piece_type_val)
                all_piece_configs.append((color_val, piece_type_val, custom_piece.symbol))

        for color, piece_type, symbol in all_piece_configs:
            image_path = ASSETS_DIR + f"/{symbol}.png"
            try:
                image = pygame.image.load(image_path).convert_alpha()
                self.piece_images[(color, piece_type)] = self._scale_piece_image(image)
            except pygame.error as e:
                print(f"Warning: Could not load image {image_path}. Error: {e}")
                self.piece_images[(color, piece_type)] = self._create_text_placeholder(symbol)

    def _scale_piece_image(self, image):
        """
        Scales a piece image to fit inside a square while preserving aspect ratio.
        """
        max_piece_size = int(SQUARE_SIZE * PIECE_SCALE)
        width, height = image.get_size()
        scale = min(max_piece_size / width, max_piece_size / height)
        scaled_size = (round(width * scale), round(height * scale))
        return pygame.transform.smoothscale(image, scaled_size)

    def _create_text_placeholder(self, text):
        """
        Creates a simple text surface as a placeholder if an image fails to load.
        """
        if not pygame.font.get_init():
            pygame.font.init()

        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, (255, 0, 0))
        placeholder_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        text_rect = text_surface.get_rect(center=(SQUARE_SIZE // 2, SQUARE_SIZE // 2))
        placeholder_surface.blit(text_surface, text_rect)
        return placeholder_surface

    def square_rect(self, row, col):
        """
        Returns the screen-space rectangle for a board square.
        """
        return pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

    def board_square(self, row, col):
        """
        Converts a screen row/column to a python-chess square.
        """
        return chess.square(col, BOARD_SIZE - 1 - row)

    def draw(self, screen, board, selected_square=None, legal_destinations=None):
        """
        Draws squares, highlights, and pieces for the current board state.
        """
        legal_destinations = legal_destinations or set()
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                square_rect = self.square_rect(row, col)
                color = LIGHT_SQUARE_COLOR if (row + col) % 2 == 0 else DARK_SQUARE_COLOR
                pygame.draw.rect(screen, color, square_rect)

                square_index = self.board_square(row, col)
                if square_index == selected_square:
                    pygame.draw.rect(screen, SELECTED_SQUARE_COLOR, square_rect)
                elif square_index in legal_destinations:
                    overlay = (
                        self.capture_highlight
                        if board.piece_at(square_index)
                        else self.move_highlight
                    )
                    screen.blit(overlay, square_rect)

                piece_on_board = board.piece_at(square_index)
                image_key = (
                    piece_on_board.color,
                    piece_on_board.piece_type,
                ) if piece_on_board else None
                if image_key in self.piece_images:
                    piece_img = self.piece_images[image_key]
                    piece_rect = piece_img.get_rect(center=square_rect.center)
                    screen.blit(piece_img, piece_rect)


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

    def screen_square(self, position):
        """
        Converts a screen pixel position to a python-chess square.
        """
        x, y = position
        if not (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
            return None

        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE
        return chess.square(col, BOARD_SIZE - 1 - row)

    def select_square(self, square):
        """
        Selects a piece and stores its legal destination squares.
        """
        self.selected_square = square
        self.legal_destinations = {
            move.to_square for move in self.game.legal_moves_from(square)
        }

    def clear_selection(self):
        """
        Clears any GUI selection and legal-move highlights.
        """
        self.selected_square = None
        self.legal_destinations = set()

    def _promotion_piece(self, move):
        """
        Returns the configured GUI promotion piece for pawn promotions.
        """
        piece = self.game.board.piece_at(move.from_square)
        if (
            piece
            and piece.piece_type == chess.PAWN
            and chess.square_rank(move.to_square) in [0, 7]
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


class ChessBoard:
    """
    Facade that coordinates chess state, rendering, and click interaction.
    """

    def __init__(self, promotion_piece=DEFAULT_PROMOTION_PIECE):
        """
        Initializes the game, renderer, and click controller.
        """
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
        return self.click_controller.handle_click(position)

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
            self.board,
            self.selected_square,
            self.legal_destinations,
        )

    def move_piece(self, move_uci):
        """
        Attempts to make a terminal UCI move and clears GUI selection on success.
        """
        if self.game.move_uci(move_uci):
            self.clear_selection()
            return True
        return False

    def save_game_state(self, filename="chess_game.json"):
        """
        Saves the current board position and active turn to a JSON file.
        """
        self.game.save_game_state(filename)

    def load_game_state(self, filename="chess_game.json"):
        """
        Loads a saved board position and active turn from a JSON file.
        """
        loaded = self.game.load_game_state(filename)
        if loaded:
            self.clear_selection()
        return loaded
