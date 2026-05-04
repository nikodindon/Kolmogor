# Task Plan

## task-001: Initialize game state
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: none
- **Estimated tokens**: 100
- **Done when**: Behavioral: grid is initialized to all 0s, score is 0, gameOver is false, paused is false.

Set grid to initial state, set score to 0, set gameOver to false, set paused to false.

## task-002: Spawn a new piece
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: Behavioral: currentPiece is set with a random type, x=4, y=0, rotation=0.

Select a random Tetrimino type, set currentPiece to {type, x: 4, y: 0, rotation: 0}.

## task-003: Draw the board
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002
- **Estimated tokens**: 100
- **Done when**: Behavioral: The board is drawn with locked cells and the current piece at its position.

Draw both board[][] locked cells and currentPiece at its current x/y position.

## task-004: Check for collision
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002
- **Estimated tokens**: 100
- **Done when**: Behavioral: Returns true if collision, false otherwise.

Check if the piece's new position collides with the grid boundaries or other pieces.

## task-005: Move piece
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-004
- **Estimated tokens**: 100
- **Done when**: Behavioral: Piece is moved if valid, collision is checked.

Check if the move is valid, if valid, update currentPiece's x or y position, call checkCollision.

## task-006: Rotate piece
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-004
- **Estimated tokens**: 100
- **Done when**: Behavioral: Piece is rotated if valid, collision is checked.

Check if the rotation is valid, if valid, update currentPiece's rotation, call checkCollision.

## task-007: Drop piece
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-004, task-005, task-006
- **Estimated tokens**: 100
- **Done when**: Behavioral: Piece is dropped, locked, lines are cleared, new piece is spawned.

Move piece down until it collides, lock the piece in place, clear lines, call checkCollision, clearLines, spawnPiece.

## task-008: Clear lines
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-007
- **Estimated tokens**: 100
- **Done when**: Behavioral: Full lines are cleared, score is incremented.

Check for full lines, remove full lines from the grid, increment score based on number of lines cleared.

## task-009: Check game over
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-007
- **Estimated tokens**: 100
- **Done when**: Behavioral: gameOver is set to true if new piece collides with top.

Check if the new piece collides with the top of the grid, if true, set gameOver to true.

## task-010: Start game loop
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-002, task-007, task-009
- **Estimated tokens**: 100
- **Done when**: Behavioral: gameTick is called every 500ms.

Use setInterval to call gameTick every 500ms.
