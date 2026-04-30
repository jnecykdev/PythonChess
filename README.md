# PythonChess

PythonChess is a simple chess game built with Pygame for the visual board and
python-chess for legal move validation and board state.

## Features

- Graphical 8x8 chessboard rendered with Pygame.
- Piece images loaded from the `assets/` directory.
- Click-to-move gameplay:
  - Click one of the current player's pieces to select it.
  - Legal destination squares are highlighted by move type.
  - Click a highlighted square to move the selected piece.
  - Clicking another current-player piece switches selection.
  - Clicking outside the board clears selection.
- Side panel with the active turn, captured pieces, and move history.
- Move categories with distinct highlight colors:
  - Green: normal move.
  - Dark green: capture.
  - Blue: check.
  - Red: checkmate.
  - Gold: promotion.
  - Teal: castling.
- Terminal gameplay remains available while the Pygame window is open.
- Legal move validation, turn handling, checkmate, and stalemate detection are handled by `python-chess`.
- GUI pawn promotion defaults to queen.
- Terminal promotion supports UCI promotion notation, such as `a7a8q`.
- Save and load helpers store game state with FEN in JSON.
- Pytest test suite for move parsing, click behavior, drawing highlights, and save/load.

## Project Structure

```text
PythonChess/
├── assets/
│   ├── bB.png
│   ├── bK.png
│   ├── bN.png
│   ├── bP.png
│   ├── bQ.png
│   ├── bR.png
│   ├── wB.png
│   ├── wK.png
│   ├── wN.png
│   ├── wP.png
│   ├── wQ.png
│   └── wR.png
├── tests/
│   └── test_python_chess.py
├── board_renderer.py
├── chess_board.py
├── chess_game.py
├── click_controller.py
├── config.py
├── main.py
├── piece.py
├── pytest.ini
├── requirements.txt
└── utils.py
```

## Requirements

- Python 3.8 or newer is recommended.
- Dependencies are listed in `requirements.txt`.

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Running the Game

From the project directory:

```bash
python main.py
```

If you are using the included virtual environment:

```bash
venv/bin/python main.py
```

The Pygame window opens with the chessboard. You can play by clicking pieces on
the board, or by entering UCI moves in the terminal.

Terminal examples:

```text
e2e4
g1f3
a7a8q
quit
```

## Controls

- Left-click a current-player piece to select it.
- Colored squares show where the selected piece can legally move and what type of move each target creates.
- Left-click a highlighted square to make the move.
- Left-click the selected piece again to deselect it.
- The right-side panel shows whose turn it is, captured pieces, and recent moves.
- Type `quit` in the terminal to exit.

## Tests

Run the test suite with:

```bash
venv/bin/python -m pytest -q
```

The tests use dummy SDL video and audio drivers, so they can run in a headless
terminal environment.

Note: if `venv/bin/pytest` points to an old path, use `venv/bin/python -m pytest`
instead.

## Main Files

- `main.py`: starts Pygame, keeps the window responsive, and reads terminal moves in a background thread.
- `chess_board.py`: facade that coordinates game state, rendering, and click interaction.
- `chess_game.py`: owns chess rules, board state, move history, captures, and save/load helpers.
- `board_renderer.py`: handles Pygame image loading, board drawing, legal move highlighting, and the side panel.
- `click_controller.py`: converts mouse positions into selection state and legal GUI moves.
- `config.py`: centralizes constants, static labels/messages, layout values, piece metadata, asset paths, and default settings.
- `piece.py`: maps piece colors and types to asset symbols like `wP` and `bK`.
- `utils.py`: parses terminal move input into UCI format.
- `tests/test_python_chess.py`: documents and verifies current behavior.
