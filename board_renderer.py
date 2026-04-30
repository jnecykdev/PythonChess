import chess
import pygame

from config import (
    ASSETS_DIR,
    BODY_FONT_SIZE,
    BOARD_SIZE,
    BOARD_PIXEL_SIZE,
    BUTTON_BORDER_RADIUS,
    CAPTURED_BY_BLACK_TEXT,
    CAPTURED_BY_WHITE_TEXT,
    CAPTURE_ROW_HEIGHT,
    DARK_SQUARE_COLOR,
    EMPTY_RECT,
    EMPTY_CAPTURE_TEXT,
    EXIT_ACTION,
    EXIT_TEXT,
    GAME_OVER_ACTIONS_BOTTOM_OFFSET,
    GAME_OVER_BUTTON_GAP,
    GAME_OVER_BUTTON_HEIGHT,
    GAME_OVER_BUTTON_TOP_GAP,
    GAME_OVER_BUTTON_WIDTH,
    GAME_OVER_HISTORY_BOTTOM_MARGIN,
    GAME_OVER_RESULT_GAP,
    GAME_OVER_TEXT,
    HIGHLIGHT_ALPHA,
    LIGHT_SQUARE_COLOR,
    MOVE_CATEGORY_CAPTURE,
    MOVE_CATEGORY_NORMAL,
    MOVE_HIGHLIGHT_COLORS,
    MOVE_HISTORY_BOTTOM_MARGIN,
    MOVE_HISTORY_RIGHT_PADDING,
    MOVE_HISTORY_ROW_FORMAT,
    MOVE_HISTORY_ROW_HEIGHT,
    MOVE_HISTORY_TITLE_TEXT,
    PANEL_ACCENT_COLOR,
    PANEL_BACKGROUND_COLOR,
    PANEL_BORDER_WIDTH,
    PANEL_HISTORY_GAP,
    PANEL_LARGE_GAP,
    PANEL_LEFT_PADDING,
    PANEL_MUTED_TEXT_COLOR,
    PANEL_SECTION_GAP,
    PANEL_TEXT_COLOR,
    PANEL_TEXT_LINE_HEIGHT,
    PANEL_TITLE_SPACING,
    PANEL_TITLE_TEXT,
    PANEL_TOP_PADDING,
    PIECE_SCALE,
    PIECE_COLORS,
    PIECE_IMAGE_LOAD_WARNING,
    PIECE_TYPES,
    PLACEHOLDER_FONT_SIZE,
    PLACEHOLDER_TEXT_COLOR,
    PLAY_AGAIN_TEXT,
    RESTART_ACTION,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SCROLLBAR_MIN_THUMB_HEIGHT,
    SCROLLBAR_TRACK_WIDTH,
    SELECTED_SQUARE_COLOR,
    SMALL_FONT_SIZE,
    SQUARE_SIZE,
    TITLE_FONT_SIZE,
    TURN_LABEL_TEXT,
)
from piece import Piece


class BoardRenderer:
    """
    Handles Pygame image loading and drawing for the chessboard.
    """

    def __init__(self):
        """
        Initializes piece images and reusable highlight overlays.
        """
        self.piece_images = {}
        self.highlight_overlays = {
            category: self._create_highlight_overlay(color)
            for category, color in MOVE_HIGHLIGHT_COLORS.items()
        }
        self.move_highlight = self.highlight_overlays[MOVE_CATEGORY_NORMAL]
        self.capture_highlight = self.highlight_overlays[MOVE_CATEGORY_CAPTURE]
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.body_font = pygame.font.Font(None, BODY_FONT_SIZE)
        self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        self.move_history_scroll = 0
        self.history_rect = pygame.Rect(*EMPTY_RECT)
        self.play_again_button_rect = pygame.Rect(*EMPTY_RECT)
        self.exit_button_rect = pygame.Rect(*EMPTY_RECT)
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
        for color_val in PIECE_COLORS:
            for piece_type_val in PIECE_TYPES:
                custom_piece = Piece(color_val, piece_type_val)
                all_piece_configs.append((color_val, piece_type_val, custom_piece.symbol))

        for color, piece_type, symbol in all_piece_configs:
            image_path = ASSETS_DIR + f"/{symbol}.png"
            try:
                image = pygame.image.load(image_path).convert_alpha()
                self.piece_images[(color, piece_type)] = self._scale_piece_image(image)
            except pygame.error as e:
                print(PIECE_IMAGE_LOAD_WARNING.format(image_path, e))
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

        font = pygame.font.Font(None, PLACEHOLDER_FONT_SIZE)
        text_surface = font.render(text, True, PLACEHOLDER_TEXT_COLOR)
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

    def draw(self, screen, game, selected_square=None, move_categories=None):
        """
        Draws the board, highlighted moves, pieces, and side panel.
        """
        board = game.board
        move_categories = move_categories or {}
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                square_rect = self.square_rect(row, col)
                color = LIGHT_SQUARE_COLOR if (row + col) % 2 == 0 else DARK_SQUARE_COLOR
                pygame.draw.rect(screen, color, square_rect)

                square_index = self.board_square(row, col)
                if square_index == selected_square:
                    pygame.draw.rect(screen, SELECTED_SQUARE_COLOR, square_rect)
                elif square_index in move_categories:
                    overlay = self.highlight_overlays[move_categories[square_index]]
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

        self.draw_panel(screen, game)

    def draw_panel(self, screen, game):
        """
        Draws turn, captured pieces, and move history in the side panel.
        """
        panel_rect = pygame.Rect(BOARD_PIXEL_SIZE, 0, SCREEN_WIDTH - BOARD_PIXEL_SIZE, SCREEN_HEIGHT)
        pygame.draw.rect(screen, PANEL_BACKGROUND_COLOR, panel_rect)
        pygame.draw.line(
            screen,
            PANEL_ACCENT_COLOR,
            (BOARD_PIXEL_SIZE, 0),
            (BOARD_PIXEL_SIZE, SCREEN_HEIGHT),
            PANEL_BORDER_WIDTH,
        )

        x = BOARD_PIXEL_SIZE + PANEL_LEFT_PADDING
        y = PANEL_TOP_PADDING
        self._draw_text(screen, PANEL_TITLE_TEXT, self.title_font, PANEL_TEXT_COLOR, x, y)
        y += PANEL_TITLE_SPACING
        self._draw_text(screen, TURN_LABEL_TEXT, self.small_font, PANEL_MUTED_TEXT_COLOR, x, y)
        y += PANEL_TEXT_LINE_HEIGHT
        self._draw_text(screen, game.turn_label(), self.title_font, PANEL_ACCENT_COLOR, x, y)

        y += PANEL_LARGE_GAP
        self._draw_text(screen, CAPTURED_BY_WHITE_TEXT, self.small_font, PANEL_MUTED_TEXT_COLOR, x, y)
        y += PANEL_SECTION_GAP
        y = self._draw_captured_pieces(screen, game.captured_pieces[chess.WHITE], x, y)

        y += PANEL_SECTION_GAP
        self._draw_text(screen, CAPTURED_BY_BLACK_TEXT, self.small_font, PANEL_MUTED_TEXT_COLOR, x, y)
        y += PANEL_SECTION_GAP
        y = self._draw_captured_pieces(screen, game.captured_pieces[chess.BLACK], x, y)

        y += PANEL_HISTORY_GAP
        self._draw_move_history(screen, game, x, y)

        if game.board.is_game_over():
            self._draw_game_over_actions(screen, game, x)

    def _draw_move_history(self, screen, game, x, y):
        """
        Draws a scrollable move-history viewport.
        """
        self._draw_text(screen, MOVE_HISTORY_TITLE_TEXT, self.small_font, PANEL_MUTED_TEXT_COLOR, x, y)
        y += MOVE_HISTORY_ROW_HEIGHT

        row_height = MOVE_HISTORY_ROW_HEIGHT
        bottom_margin = (
            GAME_OVER_HISTORY_BOTTOM_MARGIN
            if game.board.is_game_over()
            else MOVE_HISTORY_BOTTOM_MARGIN
        )
        history_height = max(row_height, SCREEN_HEIGHT - y - bottom_margin)
        self.history_rect = pygame.Rect(x, y, SCREEN_WIDTH - x - MOVE_HISTORY_RIGHT_PADDING, history_height)
        rows = game.move_history_rows()
        visible_count = max(1, self.history_rect.height // row_height)
        max_scroll = max(0, len(rows) - visible_count)
        self.move_history_scroll = max(0, min(self.move_history_scroll, max_scroll))

        end = len(rows) - self.move_history_scroll
        start = max(0, end - visible_count)
        visible_rows = rows[start:end]

        clip = screen.get_clip()
        screen.set_clip(self.history_rect)
        draw_y = self.history_rect.y
        for move_number, white_move, black_move in visible_rows:
            move_text = MOVE_HISTORY_ROW_FORMAT.format(move_number, white_move, black_move)
            self._draw_text(screen, move_text, self.body_font, PANEL_TEXT_COLOR, x, draw_y)
            draw_y += row_height
        screen.set_clip(clip)

        if max_scroll:
            self._draw_scrollbar(screen, len(rows), visible_count, max_scroll)

    def _draw_scrollbar(self, screen, total_rows, visible_count, max_scroll):
        """
        Draws a compact scrollbar for the move history viewport.
        """
        track_width = SCROLLBAR_TRACK_WIDTH
        track_rect = pygame.Rect(
            self.history_rect.right - track_width,
            self.history_rect.y,
            track_width,
            self.history_rect.height,
        )
        pygame.draw.rect(screen, PANEL_MUTED_TEXT_COLOR, track_rect)

        thumb_height = max(SCROLLBAR_MIN_THUMB_HEIGHT, int(self.history_rect.height * visible_count / total_rows))
        thumb_range = self.history_rect.height - thumb_height
        thumb_y = self.history_rect.y
        if max_scroll:
            thumb_y += int(thumb_range * (max_scroll - self.move_history_scroll) / max_scroll)
        thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_width, thumb_height)
        pygame.draw.rect(screen, PANEL_ACCENT_COLOR, thumb_rect)

    def _draw_game_over_actions(self, screen, game, x):
        """
        Draws the final result and restart/exit actions.
        """
        y = SCREEN_HEIGHT - GAME_OVER_ACTIONS_BOTTOM_OFFSET
        self._draw_text(screen, GAME_OVER_TEXT, self.small_font, PANEL_MUTED_TEXT_COLOR, x, y)
        y += GAME_OVER_RESULT_GAP
        self._draw_text(screen, game.board.result(), self.title_font, PANEL_ACCENT_COLOR, x, y)
        y += GAME_OVER_BUTTON_TOP_GAP

        button_width = GAME_OVER_BUTTON_WIDTH
        button_height = GAME_OVER_BUTTON_HEIGHT
        gap = GAME_OVER_BUTTON_GAP
        self.play_again_button_rect = pygame.Rect(x, y, button_width, button_height)
        self.exit_button_rect = pygame.Rect(x + button_width + gap, y, button_width, button_height)
        self._draw_button(screen, self.play_again_button_rect, PLAY_AGAIN_TEXT, PANEL_ACCENT_COLOR)
        self._draw_button(screen, self.exit_button_rect, EXIT_TEXT, PANEL_MUTED_TEXT_COLOR)

    def _draw_button(self, screen, rect, text, color):
        """
        Draws a side-panel action button.
        """
        pygame.draw.rect(screen, color, rect, border_radius=BUTTON_BORDER_RADIUS)
        surface = self.small_font.render(text, True, PANEL_BACKGROUND_COLOR)
        text_rect = surface.get_rect(center=rect.center)
        screen.blit(surface, text_rect)

    def scroll_move_history(self, steps):
        """
        Scrolls the move-history viewport; positive values move toward older rows.
        """
        self.move_history_scroll = max(0, self.move_history_scroll + steps)

    def reset_move_history_scroll(self):
        """
        Returns the history viewport to the newest move.
        """
        self.move_history_scroll = 0

    def history_contains(self, position):
        """
        Returns whether a screen position is inside the move-history viewport.
        """
        return self.history_rect.collidepoint(position)

    def game_over_action_at(self, position):
        """
        Returns the game-over action button at a position, if any.
        """
        if self.play_again_button_rect.collidepoint(position):
            return RESTART_ACTION
        if self.exit_button_rect.collidepoint(position):
            return EXIT_ACTION
        return None

    def _draw_captured_pieces(self, screen, pieces, x, y):
        """
        Draws compact captured-piece symbols and returns the next y position.
        """
        if not pieces:
            self._draw_text(screen, EMPTY_CAPTURE_TEXT, self.body_font, PANEL_TEXT_COLOR, x, y)
            return y + CAPTURE_ROW_HEIGHT

        symbols = " ".join(piece.symbol() for piece in pieces)
        self._draw_text(screen, symbols, self.body_font, PANEL_TEXT_COLOR, x, y)
        return y + CAPTURE_ROW_HEIGHT

    def _draw_text(self, screen, text, font, color, x, y):
        """
        Draws a text label in the side panel.
        """
        surface = font.render(text, True, color)
        screen.blit(surface, (x, y))
