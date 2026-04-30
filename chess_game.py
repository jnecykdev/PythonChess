import json

import chess

from config import (
    BLACK_TURN_LABEL,
    DEFAULT_SAVE_FILENAME,
    GAME_LOAD_ERROR_MESSAGE,
    GAME_LOADED_MESSAGE,
    GAME_SAVED_MESSAGE,
    GAME_STATE_CAPTURED_BLACK_KEY,
    GAME_STATE_CAPTURED_WHITE_KEY,
    GAME_STATE_FEN_KEY,
    GAME_STATE_MOVE_HISTORY_KEY,
    GAME_STATE_TURN_KEY,
    ILLEGAL_MOVE_DETAIL_MESSAGE,
    MOVE_CATEGORY_CAPTURE,
    MOVE_CATEGORY_CASTLING,
    MOVE_CATEGORY_CHECK,
    MOVE_CATEGORY_CHECKMATE,
    MOVE_CATEGORY_NORMAL,
    MOVE_CATEGORY_PRIORITY,
    MOVE_CATEGORY_PROMOTION,
    READ_MODE,
    SAVE_FILE_NOT_FOUND_MESSAGE,
    WHITE_TURN_LABEL,
    WRITE_MODE,
)


class ChessGame:
    """
    Owns chess rules, board state, legal move lookup, and save/load behavior.
    """

    def __init__(self, board=None):
        """
        Creates a game with a standard board unless an existing board is given.
        """
        self.board = board or chess.Board()
        self.move_history = []
        self.captured_pieces = {
            chess.WHITE: [],
            chess.BLACK: [],
        }

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
            move = self.board.parse_uci(move_uci)
            self.push_move(move)
            return True
        except ValueError as e:
            print(ILLEGAL_MOVE_DETAIL_MESSAGE.format(e))
            return False

    def push_move(self, move):
        """
        Pushes an already validated python-chess move object.
        """
        san = self.board.san(move)
        captured_piece = self.captured_piece_for(move)
        moving_color = self.board.turn
        self.board.push(move)
        self.move_history.append(san)
        if captured_piece:
            self.captured_pieces[moving_color].append(captured_piece)

    def captured_piece_for(self, move):
        """
        Returns the piece captured by a move before that move is pushed.
        """
        if not self.board.is_capture(move):
            return None

        if self.board.is_en_passant(move):
            direction = -1 if self.board.turn == chess.WHITE else 1
            capture_square = move.to_square + direction * 8
            return self.board.piece_at(capture_square)

        return self.board.piece_at(move.to_square)

    def move_category(self, move):
        """
        Classifies a legal move for GUI highlighting.
        """
        board_copy = self.board.copy(stack=False)
        board_copy.push(move)
        if board_copy.is_checkmate():
            return MOVE_CATEGORY_CHECKMATE
        if move.promotion:
            return MOVE_CATEGORY_PROMOTION
        if board_copy.is_check():
            return MOVE_CATEGORY_CHECK
        if self.board.is_castling(move):
            return MOVE_CATEGORY_CASTLING
        if self.board.is_capture(move):
            return MOVE_CATEGORY_CAPTURE
        return MOVE_CATEGORY_NORMAL

    def move_categories_from(self, square):
        """
        Returns destination-square move categories for legal moves from a square.
        """
        categories = {}
        for move in self.legal_moves_from(square):
            category = self.move_category(move)
            current = categories.get(move.to_square)
            if current is None or MOVE_CATEGORY_PRIORITY[category] > MOVE_CATEGORY_PRIORITY[current]:
                categories[move.to_square] = category
        return categories

    def turn_label(self):
        """
        Returns the active player as display text.
        """
        return WHITE_TURN_LABEL if self.board.turn == chess.WHITE else BLACK_TURN_LABEL

    def move_history_rows(self):
        """
        Returns move history grouped into full-move display rows.
        """
        rows = []
        for index in range(0, len(self.move_history), 2):
            move_number = index // 2 + 1
            white_move = self.move_history[index]
            black_move = self.move_history[index + 1] if index + 1 < len(self.move_history) else ""
            rows.append((move_number, white_move, black_move))
        return rows

    def save_game_state(self, filename=DEFAULT_SAVE_FILENAME):
        """
        Saves the current board position and active turn to a JSON file.
        """
        game_state = {
            GAME_STATE_FEN_KEY: self.board.fen(),
            GAME_STATE_TURN_KEY: self.board.turn == chess.WHITE,
            GAME_STATE_MOVE_HISTORY_KEY: self.move_history,
            GAME_STATE_CAPTURED_WHITE_KEY: [piece.symbol() for piece in self.captured_pieces[chess.WHITE]],
            GAME_STATE_CAPTURED_BLACK_KEY: [piece.symbol() for piece in self.captured_pieces[chess.BLACK]],
        }
        with open(filename, WRITE_MODE) as f:
            json.dump(game_state, f, indent=4)
        print(GAME_SAVED_MESSAGE.format(filename))

    def load_game_state(self, filename=DEFAULT_SAVE_FILENAME):
        """
        Loads a saved board position and active turn from a JSON file.
        """
        try:
            with open(filename, READ_MODE) as f:
                game_state = json.load(f)
            self.board = chess.Board(game_state[GAME_STATE_FEN_KEY])
            self.board.turn = chess.WHITE if game_state[GAME_STATE_TURN_KEY] else chess.BLACK
            self.move_history = game_state.get(GAME_STATE_MOVE_HISTORY_KEY, [])
            self.captured_pieces = {
                chess.WHITE: [
                    chess.Piece.from_symbol(symbol)
                    for symbol in game_state.get(GAME_STATE_CAPTURED_WHITE_KEY, [])
                ],
                chess.BLACK: [
                    chess.Piece.from_symbol(symbol)
                    for symbol in game_state.get(GAME_STATE_CAPTURED_BLACK_KEY, [])
                ],
            }
            print(GAME_LOADED_MESSAGE.format(filename))
            return True
        except FileNotFoundError:
            print(SAVE_FILE_NOT_FOUND_MESSAGE.format(filename))
            return False
        except Exception as e:
            print(GAME_LOAD_ERROR_MESSAGE.format(e))
            return False
