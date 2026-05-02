# Task Plan

## task-001: Create HTML structure
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: none
- **Estimated tokens**: 100
- **Done when**: The HTML contains a div with id 'game-board' and two buttons with ids 'start-button' and 'pause-button'.

Create the basic HTML structure with a div for the game board and buttons for start and pause.

## task-002: Style the game board
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: The CSS styles the 'game-board' div with a black background and white grid lines.

Style the game board with a black background and white grid lines.

## task-003: Define Tetrimino colors
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: The CSS defines classes for each Tetrimino (I, J, L, O, S, T, Z) with their specific colors.

Define CSS classes for each Tetrimino with their respective colors.

## task-004: Initialize game board
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: The JavaScript creates 200 div cells in the 'game-board' div, each 30x30px.

Create a 20x10 grid of div cells within the 'game-board' div.

## task-005: Create Tetrimino shapes
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: The JavaScript defines the shapes and rotations for each Tetrimino (I, J, L, O, S, T, Z).

Define the shapes and rotations for each Tetrimino.

## task-006: Implement Tetrimino rendering
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-004, task-005
- **Estimated tokens**: 100
- **Done when**: The JavaScript renders the initial Tetrimino on the game board.

Render the initial Tetrimino on the game board.

## task-007: Implement Tetrimino movement
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-006
- **Estimated tokens**: 100
- **Done when**: The JavaScript allows the Tetrimino to move left, right, and down.

Allow the Tetrimino to move left, right, and down.

## task-008: Implement Tetrimino rotation
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-006
- **Estimated tokens**: 100
- **Done when**: The JavaScript allows the Tetrimino to rotate.

Allow the Tetrimino to rotate.

## task-009: Implement line clearing
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-004
- **Estimated tokens**: 100
- **Done when**: The JavaScript clears lines when they are completely filled and updates the score.

Clear lines when they are completely filled and update the score.

## task-010: Implement game over condition
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001, task-004
- **Estimated tokens**: 100
- **Done when**: The JavaScript ends the game when the Tetriminos stack up to the top of the grid.

End the game when the Tetriminos stack up to the top of the grid.
