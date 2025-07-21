def parse_move_input(move_str):
    """
    Parses a chess move string (e.g., "e2e4" or "e2 e4") into UCI format.
    """
    move_str = move_str.strip().lower().replace(" ", "")
    if len(move_str) == 4 or len(move_str) == 5:
        return move_str
    print("Invalid format. Use UCI format (e.g., 'e2e4' or 'g1f3').")
    return None