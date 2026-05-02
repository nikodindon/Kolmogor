# Task Plan

## task-001: Set up the HTML structure
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: none
- **Estimated tokens**: 100
- **Done when**: The HTML file contains a <style> tag and a <script> tag.

Create the basic HTML structure with a <style> tag for CSS and a <script> tag for JavaScript.

## task-002: Define the grid dimensions
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 150
- **Done when**: The CSS contains a grid layout with specified dimensions.

Set the dimensions of the Tetris grid within the CSS.

## task-003: Style the grid lines
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-002
- **Estimated tokens**: 100
- **Done when**: The CSS contains styles for the grid lines.

Add CSS to style the grid lines with the specified color.

## task-004: Define Tetris piece colors
- **File**: `index.html`
- **Status**: DONE
- **Depends on**: task-001
- **Estimated tokens**: 100
- **Done when**: The CSS contains color definitions for each Tetris piece.

Set the colors for each Tetris piece within the CSS.

## task-005: Initialize the game board
- **File**: `index.html`
- **Status**: IN_PROGRESS
- **Depends on**: task-001
- **Estimated tokens**: 200
- **Done when**: The JavaScript contains a function to initialize the game board.

Create a JavaScript function to initialize the game board with the grid.

## task-006: Add Tetris pieces to the board
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-005
- **Estimated tokens**: 200
- **Done when**: The JavaScript contains a function to add Tetris pieces to the board.

Create a JavaScript function to add Tetris pieces to the game board.

## task-007: Implement piece movement controls
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-006
- **Estimated tokens**: 200
- **Done when**: The JavaScript contains functions to handle piece movement controls.

Create JavaScript functions to handle left, right, and down arrow key presses for moving Tetris pieces.

## task-008: Implement piece rotation control
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-007
- **Estimated tokens**: 150
- **Done when**: The JavaScript contains a function to handle piece rotation control.

Create a JavaScript function to handle the up arrow key press for rotating Tetris pieces.

## task-009: Implement scoring system
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-006
- **Estimated tokens**: 150
- **Done when**: The JavaScript contains a function to update the score.

Create a JavaScript function to update the score based on completed lines.

## task-010: Implement game over condition
- **File**: `index.html`
- **Status**: PENDING
- **Depends on**: task-006, task-009
- **Estimated tokens**: 150
- **Done when**: The JavaScript contains a function to check for the game over condition.

Create a JavaScript function to check for the game over condition when pieces stack up to the top.
