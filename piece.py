import pygame
import chess
import os

# --- Configuration Constants (MUST be defined here) ---
BOARD_SIZE = 8
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
SQUARE_SIZE = SCREEN_WIDTH // BOARD_SIZE # Size of each square in pixels

LIGHT_SQUARE_COLOR = (240, 217, 181)
DARK_SQUARE_COLOR = (181, 136, 99)

# --- Asset Paths (MUST be defined here) ---
ASSETS_DIR = "assets" # Folder where piece images are stored

# --- Your Custom Piece Class ---
class Piece:
    """
    Represents a single chess piece.
    This class is maintained for its design pattern and symbolic representation,
    used here primarily to derive image filenames from piece types and colors.
    """
    def __init__(self, color, piece_type):
        if color not in [chess.WHITE, chess.BLACK, 'white', 'black']:
            raise ValueError("Piece color must be 'white' or 'black' (or chess.WHITE/BLACK).")
        if piece_type not in [
            chess.PAWN, chess.ROOK, chess.KNIGHT, chess.BISHOP,
            chess.QUEEN, chess.KING,
            'pawn', 'rook', 'knight', 'bishop', 'queen', 'king'
        ]:
            raise ValueError("Piece type must be a valid chess piece type (or chess.PAWN etc.).")

        self.color = chess.WHITE if color == 'white' or color is True else chess.BLACK
        
        if isinstance(piece_type, str):
            type_map = {
                'pawn': chess.PAWN, 'rook': chess.ROOK, 'knight': chess.KNIGHT,
                'bishop': chess.BISHOP, 'queen': chess.QUEEN, 'king': chess.KING
            }
            self.type = type_map.get(piece_type)
        else:
            self.type = piece_type

        self.symbol = self._generate_symbol() 

    def _generate_symbol(self):
        color_char = 'w' if self.color == chess.WHITE else 'b'
        type_map = {
            chess.PAWN: 'P',
            chess.ROOK: 'R',
            chess.KNIGHT: 'N',
            chess.BISHOP: 'B',
            chess.QUEEN: 'Q',
            chess.KING: 'K'
        }
        type_char = type_map.get(self.type, '?')
        return f"{color_char}{type_char}"

    def __str__(self):
        return self.symbol

    def __repr__(self):
        color_str = 'white' if self.color == chess.WHITE else 'black'
        type_str_map = {v: k for k, v in {
            'pawn': chess.PAWN, 'rook': chess.ROOK, 'knight': chess.KNIGHT,
            'bishop': chess.BISHOP, 'queen': chess.QUEEN, 'king': chess.KING
        }.items()}
        type_str = type_str_map.get(self.type, 'unknown')
        return f"Piece(color='{color_str}', type='{type_str}')"
