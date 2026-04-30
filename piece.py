import chess

from config import (
    BLACK_ASSET_PREFIX,
    BLACK_COLOR_NAME,
    INVALID_PIECE_COLOR_MESSAGE,
    INVALID_PIECE_TYPE_MESSAGE,
    PIECE_COLOR_NAMES,
    PIECE_COLORS,
    PIECE_NAME_BY_TYPE,
    PIECE_REPR_FORMAT,
    PIECE_SYMBOL_BY_TYPE,
    PIECE_TYPE_BY_NAME,
    PIECE_TYPE_NAMES,
    PIECE_TYPES,
    UNKNOWN_PIECE_NAME,
    UNKNOWN_PIECE_SYMBOL,
    WHITE_ASSET_PREFIX,
    WHITE_COLOR_NAME,
)


class Piece:
    """
    Represents a single chess piece.
    This class is maintained for its design pattern and symbolic representation,
    used here primarily to derive image filenames from piece types and colors.
    """
    def __init__(self, color, piece_type):
        """
        Creates a piece from python-chess constants or matching text names.
        """
        if color not in PIECE_COLORS and color not in PIECE_COLOR_NAMES:
            raise ValueError(INVALID_PIECE_COLOR_MESSAGE)
        if piece_type not in PIECE_TYPES and piece_type not in PIECE_TYPE_NAMES:
            raise ValueError(INVALID_PIECE_TYPE_MESSAGE)

        self.color = chess.WHITE if color == WHITE_COLOR_NAME or color is True else chess.BLACK
        
        if isinstance(piece_type, str):
            self.type = PIECE_TYPE_BY_NAME.get(piece_type)
        else:
            self.type = piece_type

        self.symbol = self._generate_symbol() 

    def _generate_symbol(self):
        """
        Builds the asset filename stem for this piece, such as wP or bK.
        """
        color_char = WHITE_ASSET_PREFIX if self.color == chess.WHITE else BLACK_ASSET_PREFIX
        type_char = PIECE_SYMBOL_BY_TYPE.get(self.type, UNKNOWN_PIECE_SYMBOL)
        return f"{color_char}{type_char}"

    def __str__(self):
        """
        Returns the compact symbolic representation used by asset filenames.
        """
        return self.symbol

    def __repr__(self):
        """
        Returns a developer-friendly representation of the piece.
        """
        color_str = WHITE_COLOR_NAME if self.color == chess.WHITE else BLACK_COLOR_NAME
        type_str = PIECE_NAME_BY_TYPE.get(self.type, UNKNOWN_PIECE_NAME)
        return PIECE_REPR_FORMAT.format(color_str, type_str)
