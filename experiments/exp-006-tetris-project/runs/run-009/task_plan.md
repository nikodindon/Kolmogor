# Task Plan

## task-001: Initialize game state
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: none
- **Estimated tokens**: 200
- **Done when**: gameOver is false, score is 0, grid is initialized, currentPiece is generated and placed on the grid, and paused is false.

Set grid to initial state, initialize score to 0, set gameOver to false, set paused to false, and generate the first Tetrimino.

## task-002: Draw initial board and piece
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: drawBoard() has been called and displays the initial grid and currentPiece.

Call drawBoard() to draw the initial state of the grid and the first Tetrimino.

## task-003: Handle arrow key inputs for moving pieces
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-001
- **Estimated tokens**: 150
- **Done when**: Arrow key inputs move the currentPiece left, right, or down as expected.

Add event listeners for arrow key inputs and implement movePiece() to move the currentPiece left, right, or down based on the input.

## task-004: Handle up arrow key input for rotating pieces
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: Up arrow key input rotates the currentPiece if the rotation is valid.

Add event listener for the up arrow key and implement rotatePiece() to rotate the currentPiece if the rotation is valid.

## task-005: Handle spacebar input for dropping pieces
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: Spacebar input moves the currentPiece down until it can't move further.

Add event listener for the spacebar and implement dropPiece() to move the currentPiece down until it can't move further.

## task-006: Handle game tick for piece movement
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-001
- **Estimated tokens**: 150
- **Done when**: gameTick() moves the currentPiece down every 500ms and calls dropPiece() if the piece can't move further.

Implement gameTick() to move the currentPiece down every 500ms using setInterval, and call dropPiece() if the piece can't move further.

## task-007: Clear full lines and update score
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: clearLines() clears full lines and updates the score.

Implement clearLines() to check for full lines and clear them, updating the score accordingly.

## task-008: Check for game over condition
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: checkGameOver() sets gameOver to true if the new piece can't be placed.

Implement checkGameOver() to check if the new piece can't be placed and set gameOver to true if so.

## task-009: Pause and resume game
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: P key input pauses and resumes the game.

Add event listener for the P key and implement logic to pause and resume the game using the paused state variable.

## task-010: Draw updated board and piece
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-001, task-003, task-004, task-005, task-006, task-007, task-008, task-009
- **Estimated tokens**: 100
- **Done when**: drawBoard() has been called and displays the updated grid and currentPiece after each game tick or user input.

Call drawBoard() to redraw the updated grid and currentPiece after each game tick or user input.
