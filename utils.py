from config import INVALID_MOVE_FORMAT_MESSAGE, UCI_MOVE_LENGTHS


def parse_move_input(move_str):
    """
    Parses a chess move string (e.g., "e2e4" or "e2 e4") into UCI format.
    """
    move_str = move_str.strip().lower().replace(" ", "")
    if len(move_str) in UCI_MOVE_LENGTHS:
        return move_str
    print(INVALID_MOVE_FORMAT_MESSAGE)
    return None
