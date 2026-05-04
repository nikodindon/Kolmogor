# Task Plan

## task-001: Initialize game state
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: none
- **Estimated tokens**: 100
- **Done when**: grid is initialized to 20x10 array of 0s, score is set to 0, gameOver is set to false.

Set grid to initial value, set score to 0, set gameOver to false.

## task-002: Initialize current piece
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: currentPiece is initialized with a random type, x set to 4, y set to 0, rotation set to 0.

Select a random piece type and set currentPiece to {type: selectedType, x: 4, y: 0, rotation: 0}.

## task-003: Render initial board
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002
- **Estimated tokens**: 100
- **Done when**: drawBoard() function is called, rendering both the grid and the current piece.

Draw the initial state of the grid and the current piece on the board.

## task-004: Set up game loop
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-003
- **Estimated tokens**: 100
- **Done when**: setInterval is set up to call gameLoop() every 500ms.

Use setInterval to call game loop function every 500ms.

## task-005: Implement game loop
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-003, task-004
- **Estimated tokens**: 100
- **Done when**: gameLoop() function is implemented, handling both game logic and rendering.

Handle game logic and rendering within the game loop.

## task-006: Handle piece movement
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-003, task-004, task-005
- **Estimated tokens**: 100
- **Done when**: movePiece() function is implemented, handling left, right, and down arrow key presses.

Implement movePiece function to handle left, right, and down arrow key presses.

## task-007: Handle piece rotation
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-003, task-004, task-005, task-006
- **Estimated tokens**: 100
- **Done when**: rotatePiece() function is implemented, handling up arrow key presses.

Implement rotatePiece function to handle up arrow key presses.

## task-008: Handle collision detection
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-003, task-004, task-005, task-006, task-007
- **Estimated tokens**: 100
- **Done when**: checkCollision() function is implemented, correctly detecting collisions.

Implement checkCollision function to detect collisions with grid boundaries and other pieces.

## task-009: Handle piece locking
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-003, task-004, task-005, task-006, task-007, task-008
- **Estimated tokens**: 100
- **Done when**: lockPiece() function is implemented, correctly locking the piece and clearing full lines.

Implement lockPiece function to lock the piece in place and clear full lines.

## task-010: Handle game over condition
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-003, task-004, task-005, task-006, task-007, task-008, task-009
- **Estimated tokens**: 100
- **Done when**: checkGameOver() function is implemented, correctly determining if the game is over.

Implement checkGameOver function to determine if the game is over.
