# PythonChess


1. Getting Started: Running the Game 🚀
This section provides all the essential information to set up and run the Python Chess game on your system.


1.1 Prerequisites
Before you can run the game, ensure you have the following installed:


Python 3: The game is developed in Python. It's recommended to use Python 3.7 or newer. You can download it from the official Python website.


pip: Python's package installer, which usually comes bundled with Python 3.


1.2 Project Structure
Your project directory should be organized as follows. It's crucial that the assets folder is directly within your main project directory, containing the piece image files.

PythonChess
/

├── main.py

├── chess_board.py (or chess_logic.py)

├── utils.py
   
└── assets/
    ├── bB.png
    ├── bK.png
    ├── bN.png
    ├── bP.png
    ├── bQ.png
    ├── bR.png
    ├── wB.png
    ├── wK.png
    ├── wN.png
    ├── wP.png
    ├── wQ.png
    └── wR.png
    
1.3 Installation
Follow these steps to install the required Python libraries:


Open your terminal or command prompt.


Navigate to your project directory (e.g., cd C:\Users\Julio\Documents\GitHub\PythonChess).


Install the necessary libraries using pip:


pip install pygame chess


1.4 How to Run
Once the prerequisites are met and the libraries are installed, you can start the game:


Ensure your terminal is still in the PythonChess directory.


Execute the main.py script:


python main.py


A Pygame window displaying the chessboard and pieces should appear, and the game will prompt you for moves in the console.


2. Game Features
This section details the functionalities and features implemented in the current version of the Python Chess game.


2.1 Graphical Interface
The game provides a visual chessboard using Pygame. It displays a standard 8x8 chessboard with alternating light and dark squares for clear visibility.


2.2 Chess Piece Display
The game is set up to load and display chess piece images.


Asset Loading: It loads piece images (e.g., pawns, rooks, knights, bishops, queens, kings for both white and black) from an assets/ folder.


Image Naming Convention: Images are expected to follow a specific naming convention (e.g., wP.png for a white pawn, bK.png for a black king).


Placeholder Fallback: If a specific piece image is not found in the assets/ directory, the game automatically generates a text-based placeholder (e.g., "wP") directly on the board, ensuring the piece is still visible.


2.3 Game Logic (Powered by python-chess)
The core chess rules and game state management are handled by the robust python-chess library. This integration provides:


Accurate Board State: Manages the positions of all pieces on the board.


Move Validation: Automatically checks if entered moves are legal according to chess rules, preventing invalid actions.


Turn Management: Correctly enforces turns, switching between White and Black after each valid move.


2.4 Console-Based Move Input
Currently, players interact with the game by entering their moves in UCI (Universal Chess Interface) format via the console.


Input Format: Moves are entered as a four or five-character string representing the starting square and the ending square (e.g., e2e4 for a pawn move from e2 to e4, or g1f3 for a knight move from g1 to f3).


Feedback: The game provides console feedback on whether a move was successful or illegal.


2.5 Game State Management
The game includes functionalities to save and load the current state of a match.


Save Game: You can save the current board position, including whose turn it is, to a JSON file. This uses the FEN (Forsyth-Edwards Notation) standard for compact board representation.


Load Game: You can load a previously saved game state from a JSON file, allowing you to resume a match.
