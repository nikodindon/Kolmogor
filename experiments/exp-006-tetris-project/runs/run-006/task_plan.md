# Task Plan

## task-001: Initialize game state
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: none
- **Estimated tokens**: 100
- **Done when**: Behavioral: The board is initialized with all values set to 0, currentPiece is initialized with a random type and position, score is set to 0, gameOver is set to false, and paused is set to false.

Initialize the board, currentPiece, score, gameOver, and paused state variables.

## task-002: Draw the initial board
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: Behavioral: The entire board is drawn with grid lines and all cells are empty.

Draw the initial state of the board on the canvas.

## task-003: Implement spawnPiece algorithm
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 150
- **Done when**: Behavioral: A new Tetrimino is spawned at the top center of the board with a random type and rotation set to 0.

Implement the spawnPiece algorithm to choose a random Tetrimino type and set its initial position at the top center of the board.

## task-004: Implement movePiece algorithm
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-003
- **Estimated tokens**: 150
- **Done when**: Behavioral: The piece moves left, right, or down if the move is valid, and the board is redrawn.

Implement the movePiece algorithm to check if the move is valid and update the piece's position.

## task-005: Implement rotatePiece algorithm
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-003
- **Estimated tokens**: 150
- **Done when**: Behavioral: The piece rotates if the rotation is valid, and the board is redrawn.

Implement the rotatePiece algorithm to check if the rotation is valid and update the piece's rotation.

## task-006: Implement dropPiece algorithm
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-003
- **Estimated tokens**: 150
- **Done when**: Behavioral: The piece is moved down until it can't move further, locked in place, and the board is redrawn.

Implement the dropPiece algorithm to move the piece down until it can't move further and lock it in place.

## task-007: Implement lockPiece algorithm
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-003, task-006
- **Estimated tokens**: 150
- **Done when**: Behavioral: The piece's cells are written to the board, the game over condition is checked, and the board is redrawn.

Implement the lockPiece algorithm to write the piece's cells to the board and check for game over.

## task-008: Implement clearLines algorithm
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-007
- **Estimated tokens**: 150
- **Done when**: Behavioral: Completed lines are removed, rows above the cleared line are shifted down, and the score is updated.

Implement the clearLines algorithm to remove completed lines from the board and shift rows down.

## task-009: Implement checkGameOver algorithm
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-003
- **Estimated tokens**: 150
- **Done when**: Behavioral: The game over condition is checked, and the board is redrawn.

Implement the checkGameOver algorithm to check if the new piece overlaps with any existing cells.

## task-010: Add controls and game loop
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-003, task-004, task-005, task-006, task-007, task-008, task-009
- **Estimated tokens**: 150
- **Done when**: Behavioral: The game can be controlled using arrow keys, spacebar, and P key, and the game loop updates the game state.

Add controls for moving, rotating, dropping, and pausing the game, and implement a game loop to update the game state.
