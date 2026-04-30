import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import chess
import pygame
import pytest

from chess_board import (
    BOARD_SIZE,
    LEGAL_MOVE_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SQUARE_SIZE,
    ChessBoard,
)
from piece import Piece
from utils import parse_move_input


@pytest.fixture(scope="session", autouse=True)
def pygame_session():
    """
    Initializes pygame once with a dummy display for headless test runs.
    """
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    yield
    pygame.quit()


@pytest.fixture
def chess_board():
    """
    Provides a fresh ChessBoard instance for each test.
    """
    return ChessBoard()


def square_center(square):
    """
    Converts a python-chess square to the center pixel of that board square.
    """
    row = BOARD_SIZE - 1 - chess.square_rank(square)
    col = chess.square_file(square)
    return col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2


@pytest.mark.parametrize(
    ("move_text", "expected"),
    [
        ("e2e4", "e2e4"),
        ("E2 E4", "e2e4"),
        ("a7a8q", "a7a8q"),
    ],
)
def test_parse_move_input_accepts_uci_formats(move_text, expected):
    """
    Validates accepted terminal move formats are normalized to UCI text.
    """
    assert parse_move_input(move_text) == expected


def test_parse_move_input_rejects_bad_format():
    """
    Ensures malformed terminal move text is rejected.
    """
    assert parse_move_input("e2") is None


@pytest.mark.parametrize(
    ("color", "piece_type", "symbol"),
    [
        (chess.WHITE, chess.KING, "wK"),
        (chess.BLACK, chess.QUEEN, "bQ"),
        ("white", "knight", "wN"),
        ("black", "pawn", "bP"),
    ],
)
def test_piece_generates_asset_symbol(color, piece_type, symbol):
    """
    Confirms Piece creates symbols that match the image asset naming scheme.
    """
    assert Piece(color, piece_type).symbol == symbol


def test_chess_board_starts_with_all_piece_images_loaded(chess_board):
    """
    Checks a new board starts from the standard position with all asset keys.
    """
    assert len(chess_board.piece_images) == 12
    assert chess_board.board.board_fen() == chess.STARTING_BOARD_FEN


def test_terminal_move_path_makes_legal_move_and_clears_selection(chess_board):
    """
    Verifies terminal UCI moves update the board and reset GUI selection state.
    """
    chess_board.handle_click(square_center(chess.E2))

    assert chess_board.move_piece("e2e4") is True
    assert chess_board.board.piece_at(chess.E4).piece_type == chess.PAWN
    assert chess_board.selected_square is None
    assert chess_board.legal_destinations == set()


def test_terminal_move_path_rejects_illegal_move(chess_board):
    """
    Verifies illegal terminal UCI moves leave board state and turn unchanged.
    """
    assert chess_board.move_piece("e2e5") is False
    assert chess_board.board.piece_at(chess.E2).piece_type == chess.PAWN
    assert chess_board.board.turn == chess.WHITE


def test_clicking_current_turn_piece_selects_it_and_marks_legal_destinations(chess_board):
    """
    Ensures clicking a current-turn piece selects it and stores legal targets.
    """
    assert chess_board.handle_click(square_center(chess.E2)) is None

    assert chess_board.selected_square == chess.E2
    assert chess_board.legal_destinations == {chess.E3, chess.E4}


def test_clicking_opponent_piece_on_current_turn_does_not_select(chess_board):
    """
    Ensures a player cannot select the opponent's piece on their turn.
    """
    assert chess_board.handle_click(square_center(chess.E7)) is None

    assert chess_board.selected_square is None
    assert chess_board.legal_destinations == set()


def test_clicking_selected_piece_again_clears_selection(chess_board):
    """
    Confirms clicking the selected piece a second time deselects it.
    """
    chess_board.handle_click(square_center(chess.E2))

    assert chess_board.handle_click(square_center(chess.E2)) is None
    assert chess_board.selected_square is None
    assert chess_board.legal_destinations == set()


def test_clicking_another_current_turn_piece_switches_selection(chess_board):
    """
    Confirms selecting another own piece replaces the previous selection.
    """
    chess_board.handle_click(square_center(chess.E2))

    assert chess_board.handle_click(square_center(chess.G1)) is None
    assert chess_board.selected_square == chess.G1
    assert chess_board.legal_destinations == {chess.F3, chess.H3}


def test_clicking_legal_destination_makes_move(chess_board):
    """
    Verifies clicking a highlighted legal destination executes the move.
    """
    chess_board.handle_click(square_center(chess.E2))

    assert chess_board.handle_click(square_center(chess.E4)) == "e2e4"
    assert chess_board.board.piece_at(chess.E4).piece_type == chess.PAWN
    assert chess_board.board.piece_at(chess.E2) is None
    assert chess_board.board.turn == chess.BLACK
    assert chess_board.selected_square is None
    assert chess_board.legal_destinations == set()


def test_clicking_illegal_destination_clears_selection_without_moving(chess_board):
    """
    Ensures illegal target clicks clear selection without changing the board.
    """
    chess_board.handle_click(square_center(chess.E2))

    assert chess_board.handle_click(square_center(chess.E5)) is None
    assert chess_board.board.piece_at(chess.E2).piece_type == chess.PAWN
    assert chess_board.selected_square is None
    assert chess_board.legal_destinations == set()


def test_click_outside_board_clears_selection(chess_board):
    """
    Ensures clicks outside the board clear any active selection.
    """
    chess_board.handle_click(square_center(chess.E2))

    assert chess_board.handle_click((SCREEN_WIDTH + 1, SCREEN_HEIGHT + 1)) is None
    assert chess_board.selected_square is None
    assert chess_board.legal_destinations == set()


def test_click_promotion_defaults_to_queen(chess_board):
    """
    Verifies GUI pawn promotion chooses a queen by default.
    """
    chess_board.board = chess.Board("8/P7/8/8/8/8/8/4k2K w - - 0 1")
    chess_board.handle_click(square_center(chess.A7))

    assert chess_board.handle_click(square_center(chess.A8)) == "a7a8q"
    promoted_piece = chess_board.board.piece_at(chess.A8)
    assert promoted_piece.piece_type == chess.QUEEN
    assert promoted_piece.color == chess.WHITE


def test_clicks_are_ignored_after_game_over(chess_board):
    """
    Ensures GUI clicks cannot alter selection after a completed game.
    """
    for move in ["f2f3", "e7e5", "g2g4", "d8h4"]:
        chess_board.board.push_uci(move)

    assert chess_board.board.is_checkmate()

    assert chess_board.handle_click(square_center(chess.H4)) is None
    assert chess_board.selected_square is None
    assert chess_board.legal_destinations == set()


def test_draw_board_paints_legal_destinations_green(chess_board):
    """
    Confirms drawing the board paints legal destination highlights in green.
    """
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    chess_board.handle_click(square_center(chess.E2))

    chess_board.draw_board(screen)

    green_pixel = screen.get_at(square_center(chess.E4))
    assert green_pixel.g > green_pixel.r
    assert green_pixel.g > green_pixel.b
    assert abs(green_pixel.g - LEGAL_MOVE_COLOR[1]) < 80


def test_save_and_load_game_state_round_trip(chess_board, tmp_path):
    """
    Verifies saved game state can be loaded back to the exact same FEN.
    """
    save_file = tmp_path / "game.json"
    chess_board.move_piece("e2e4")
    saved_fen = chess_board.board.fen()

    chess_board.save_game_state(str(save_file))
    chess_board.move_piece("e7e5")

    assert chess_board.load_game_state(str(save_file)) is True
    assert chess_board.board.fen() == saved_fen
