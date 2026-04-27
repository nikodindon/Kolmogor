# Project: Tetris Game
## Target
Python and Pygame
## Files
- `main.py` — Entry point of the game, initializes Pygame and runs the game loop.
- `tetris.py` — Contains the game logic, including the Tetris board, pieces, and game rules.
- `utils.py` — Utility functions for game operations, such as drawing the board and pieces.
## Features
1. A 10x20 grid Tetris board.
2. Seven different Tetris pieces (I, J, L, O, S, T, Z).
3. Piece rotation and movement controls.
4. Line clearing and scoring system.
5. Game over condition when pieces stack up to the top of the board.
## Visual guidelines
- Background color: #000000 (black)
- Board grid color: #333333 (dark gray)
- Piece colors: 
  - I: #00FFFF (cyan)
  - J: #0000FF (blue)
  - L: #FFA500 (orange)
  - O: #FFFF00 (yellow)
  - S: #00FF00 (green)
  - T: #800080 (purple)
  - Z: #FF0000 (red)
- Font: Arial, size 16
## Controls
- Left arrow key: Move piece left
- Right arrow key: Move piece right
- Down arrow key: Move piece down
- Up arrow key: Rotate piece
- Spacebar: Drop piece immediately
## Technical constraints
- The game must run in a native windowed environment.
- The game loop must update at least 30 times per second.