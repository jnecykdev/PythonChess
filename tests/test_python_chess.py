import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import chess
import pygame
import pytest

from chess_board import (
    BoardRenderer,
    ChessBoard,
    ClickController,
    ChessGame,
)
from config import (
    BOARD_SIZE,
    BOARD_PIXEL_SIZE,
    LEGAL_CASTLING_COLOR,
    LEGAL_CAPTURE_COLOR,
    LEGAL_CHECK_COLOR,
    LEGAL_CHECKMATE_COLOR,
    LEGAL_MOVE_COLOR,
    LEGAL_PROMOTION_COLOR,
    PANEL_BACKGROUND_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SQUARE_SIZE,
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


def square_overlay_point(square):
    """
    Converts a square to a pixel near the corner where no piece image is drawn.
    """
    row = BOARD_SIZE - 1 - chess.square_rank(square)
    col = chess.square_file(square)
    return col * SQUARE_SIZE + 6, row * SQUARE_SIZE + 6


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
    assert SCREEN_WIDTH > BOARD_PIXEL_SIZE


def test_chess_board_composes_game_renderer_and_click_controller(chess_board):
    """
    Confirms ChessBoard delegates to separate game, renderer, and click objects.
    """
    assert isinstance(chess_board.game, ChessGame)
    assert isinstance(chess_board.renderer, BoardRenderer)
    assert isinstance(chess_board.click_controller, ClickController)


def test_terminal_move_path_makes_legal_move_and_clears_selection(chess_board):
    """
    Verifies terminal UCI moves update the board and reset GUI selection state.
    """
    chess_board.handle_click(square_center(chess.E2))

    assert chess_board.move_piece("e2e4") is True
    assert chess_board.board.piece_at(chess.E4).piece_type == chess.PAWN
    assert chess_board.game.move_history == ["e4"]
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
    assert chess_board.move_categories == {
        chess.E3: "normal",
        chess.E4: "normal",
    }


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
    assert chess_board.game.move_history == ["e4"]
    assert chess_board.selected_square is None
    assert chess_board.legal_destinations == set()


def test_rook_can_move_after_path_is_open(chess_board):
    """
    Verifies rook GUI selection and movement stays legal on open files/ranks.
    """
    chess_board.board = chess.Board("4k3/8/8/8/8/8/R7/4K3 w - - 0 1")

    assert chess_board.handle_click(square_center(chess.A2)) is None
    assert chess_board.legal_destinations == {
        chess.A1,
        chess.A3,
        chess.A4,
        chess.A5,
        chess.A6,
        chess.A7,
        chess.A8,
        chess.B2,
        chess.C2,
        chess.D2,
        chess.E2,
        chess.F2,
        chess.G2,
        chess.H2,
    }
    assert chess_board.handle_click(square_center(chess.A7)) == "a2a7"
    assert chess_board.board.piece_at(chess.A7).piece_type == chess.ROOK


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


def test_click_in_side_panel_clears_selection_without_moving(chess_board):
    """
    Ensures side panel clicks are ignored by board move handling.
    """
    chess_board.handle_click(square_center(chess.E2))

    assert chess_board.handle_click((BOARD_PIXEL_SIZE + 20, 20)) is None
    assert chess_board.board.piece_at(chess.E2).piece_type == chess.PAWN
    assert chess_board.selected_square is None


def test_click_promotion_defaults_to_queen(chess_board):
    """
    Verifies GUI pawn promotion chooses a queen by default.
    """
    chess_board.board = chess.Board("8/P7/8/8/8/8/8/4k2K w - - 0 1")
    chess_board.handle_click(square_center(chess.A7))

    assert chess_board.move_categories[chess.A8] == "promotion"
    assert chess_board.handle_click(square_center(chess.A8)) == "a7a8q"
    promoted_piece = chess_board.board.piece_at(chess.A8)
    assert promoted_piece.piece_type == chess.QUEEN
    assert promoted_piece.color == chess.WHITE


def test_click_promotion_can_be_configured():
    """
    Verifies GUI pawn promotion can use a configured piece type.
    """
    chess_board = ChessBoard(promotion_piece=chess.ROOK)
    chess_board.board = chess.Board("8/P7/8/8/8/8/8/4k2K w - - 0 1")
    chess_board.handle_click(square_center(chess.A7))

    assert chess_board.handle_click(square_center(chess.A8)) == "a7a8r"
    promoted_piece = chess_board.board.piece_at(chess.A8)
    assert promoted_piece.piece_type == chess.ROOK
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


@pytest.mark.parametrize(
    ("fen", "from_square", "to_square", "category", "color"),
    [
        ("8/8/8/3p4/4P3/8/8/4K2k w - - 0 1", chess.E4, chess.D5, "capture", LEGAL_CAPTURE_COLOR),
        ("7k/8/8/8/8/8/6R1/K7 w - - 0 1", chess.G2, chess.G8, "check", LEGAL_CHECK_COLOR),
        ("rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq g3 0 2", chess.D8, chess.H4, "checkmate", LEGAL_CHECKMATE_COLOR),
        ("8/P7/8/8/8/8/8/4k2K w - - 0 1", chess.A7, chess.A8, "promotion", LEGAL_PROMOTION_COLOR),
        ("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", chess.E1, chess.G1, "castling", LEGAL_CASTLING_COLOR),
    ],
)
def test_move_categories_drive_highlight_colors(chess_board, fen, from_square, to_square, category, color):
    """
    Verifies special legal move categories use their configured highlight colors.
    """
    chess_board.board = chess.Board(fen)
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    chess_board.handle_click(square_center(from_square))

    assert chess_board.move_categories[to_square] == category

    chess_board.draw_board(screen)
    pixel = screen.get_at(square_overlay_point(to_square))
    assert abs(pixel.r - color[0]) < 120
    assert abs(pixel.g - color[1]) < 120
    assert abs(pixel.b - color[2]) < 120


def test_captures_are_recorded_for_side_panel(chess_board):
    """
    Verifies captured pieces are tracked for the side panel.
    """
    chess_board.board = chess.Board("8/8/8/3p4/4P3/8/8/4K2k w - - 0 1")

    assert chess_board.handle_click(square_center(chess.E4)) is None
    assert chess_board.handle_click(square_center(chess.D5)) == "e4d5"
    assert [piece.symbol() for piece in chess_board.game.captured_pieces[chess.WHITE]] == ["p"]


def test_side_panel_is_drawn_next_to_board(chess_board):
    """
    Confirms the side panel area is painted separately from the board.
    """
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    chess_board.draw_board(screen)

    assert screen.get_at((BOARD_PIXEL_SIZE + 8, 8))[:3] == PANEL_BACKGROUND_COLOR


def test_move_history_scrolls_when_pointer_is_over_history(chess_board):
    """
    Verifies the move-history panel keeps all rows reachable by scrolling.
    """
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    chess_board.game.move_history = [f"M{index}" for index in range(40)]
    chess_board.draw_board(screen)

    assert chess_board.renderer.move_history_scroll == 0
    history_position = chess_board.renderer.history_rect.center

    assert chess_board.handle_scroll(3, history_position) is True
    chess_board.draw_board(screen)
    assert chess_board.renderer.move_history_scroll == 3

    assert chess_board.handle_scroll(-2, history_position) is True
    chess_board.draw_board(screen)
    assert chess_board.renderer.move_history_scroll == 1


def test_move_history_does_not_scroll_outside_history(chess_board):
    """
    Ensures mouse wheel events outside the history viewport are ignored.
    """
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    chess_board.game.move_history = [f"M{index}" for index in range(40)]
    chess_board.draw_board(screen)

    assert chess_board.handle_scroll(3, square_center(chess.E4)) is False
    assert chess_board.renderer.move_history_scroll == 0


def test_game_over_panel_can_restart_the_game(chess_board):
    """
    Verifies the Play Again action resets board, history, and selection state.
    """
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for move in ["f2f3", "e7e5", "g2g4", "d8h4"]:
        assert chess_board.move_piece(move) is True

    assert chess_board.board.is_checkmate()
    chess_board.draw_board(screen)

    assert chess_board.handle_click(chess_board.renderer.play_again_button_rect.center) == "restart"
    chess_board.restart_game()

    assert chess_board.board.board_fen() == chess.STARTING_BOARD_FEN
    assert chess_board.game.move_history == []
    assert chess_board.selected_square is None


def test_renderer_reuses_cached_highlight_overlays(chess_board):
    """
    Confirms highlight overlays are created once and reused while drawing.
    """
    move_highlight = chess_board.renderer.move_highlight
    capture_highlight = chess_board.renderer.capture_highlight

    chess_board.draw_board(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)))

    assert chess_board.renderer.move_highlight is move_highlight
    assert chess_board.renderer.capture_highlight is capture_highlight
    assert chess_board.renderer.highlight_overlays["normal"] is move_highlight
    assert chess_board.renderer.highlight_overlays["capture"] is capture_highlight
    assert move_highlight.get_at((0, 0))[:3] == LEGAL_MOVE_COLOR
    assert capture_highlight.get_at((0, 0))[:3] == LEGAL_CAPTURE_COLOR


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
