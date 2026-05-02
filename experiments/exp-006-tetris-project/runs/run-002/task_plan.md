# Task Plan

## task-001: Set up the HTML structure
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: none
- **Estimated tokens**: 100
- **Done when**: HTML contains a <div> with class 'grid' and two buttons with classes 'start-btn' and 'pause-btn'.

Create the basic HTML structure with a grid container and buttons for start and pause.

## task-002: Style the grid and buttons
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 150
- **Done when**: CSS styles the grid with white lines and the buttons with white text and gray hover effect.

Add CSS to style the grid and buttons according to the visual guidelines.

## task-003: Initialize the game state
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: JavaScript initializes a grid array and a current Tetrimino object.

Set up the JavaScript to initialize the game state with an empty grid and a current Tetrimino.

## task-004: Render the grid
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-003
- **Estimated tokens**: 100
- **Done when**: The grid is rendered on the page with white lines.

Write JavaScript to render the grid on the page.

## task-005: Define Tetrimino shapes
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-003
- **Estimated tokens**: 100
- **Done when**: JavaScript defines objects for each Tetrimino shape with their positions.

Create JavaScript objects for each Tetrimino shape with their respective positions.

## task-006: Render Tetriminoes
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-004, task-005
- **Estimated tokens**: 100
- **Done when**: The current Tetrimino is rendered on the grid.

Write JavaScript to render the current Tetrimino on the grid.

## task-007: Handle Tetrimino movement
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-006
- **Estimated tokens**: 100
- **Done when**: The Tetrimino can be moved left, right, and down using the arrow keys.

Implement JavaScript to handle left, right, and down arrow key presses to move the Tetrimino.

## task-008: Handle Tetrimino rotation
- **File**: `index.html`
- **Status**: FAILED
- **Depends on**: task-006
- **Estimated tokens**: 100
- **Done when**: The Tetrimino can be rotated using the up arrow key.

Implement JavaScript to handle the up arrow key press to rotate the Tetrimino.

## task-009: Handle game over condition
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-006
- **Estimated tokens**: 100
- **Done when**: The game ends when the Tetriminos stack up to the top of the grid.

Implement JavaScript to check for a game over condition when the Tetriminos stack up to the top of the grid.

## task-010: Add start and pause functionality
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-006
- **Estimated tokens**: 100
- **Done when**: The game can be started and paused using the start and pause buttons.

Implement JavaScript to handle the start and pause button clicks to control the game.
