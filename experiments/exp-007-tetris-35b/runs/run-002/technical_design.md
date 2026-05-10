# Technical Design

**Project type**: game

## State variables
- `grid` (object, int[10][20]) — Tracks filled cells in the grid, updated when pieces lock into place — init: `0`
- `currentPiece` (object, {x: int, y: int, color: string, shape: array[4][4]}) — Represents the active tetromino's position, color, and shape — init: `{x: 5, y: 0, color: '#00ff00', shape: [[1,1,1,1],[0,0,0,0],[0,0,0,0],[0,0,0,0]]}`
- `nextPiece` (object, {color: string, shape: array[4][4]}) — Holds the next tetromino's color and shape for preview — init: `{color: '#0000ff', shape: [[1,1,1,1],[0,0,0,0],[0,0,0,0],[0,0,0,0]]}`
- `score` (number, int) — Tracks total score, incremented by 100 per cleared line — init: `0`
- `gameState` (boolean, true/false) — Tracks whether game is active (true) or paused (false) — init: `false`

## Algorithms

### moveLeft
Triggered by: Left arrow key press
Reads: currentPiece, grid
Writes: currentPiece, grid
Calls: checkCollision
  1. Check collision at (x-1, y)
  2. If no collision, decrement currentPiece.x
  3. Update grid visualization

### moveDown
Triggered by: Auto-tick interval and Down arrow key press
Reads: currentPiece, grid
Writes: currentPiece, grid
Calls: checkCollision, lockPiece, clearLines
  1. Check collision at (x, y+1)
  2. If no collision, increment currentPiece.y
  3. Update grid visualization
  4. If collision, lock piece and clear lines

### rotate
Triggered by: Up arrow key press
Reads: currentPiece, grid
Writes: currentPiece, grid
Calls: checkCollision
  1. Rotate currentPiece shape 90 degrees
  2. Check collision at new position
  3. If collision, adjust position (e.g., shift right)
  4. Update grid visualization

### lockPiece
Triggered by: Collision detected during movement
Reads: currentPiece, grid, score
Writes: grid, score, currentPiece
Calls: clearLines, generateNewPiece
  1. Merge currentPiece into grid array
  2. Check for full lines
  3. Clear full lines and update score
  4. Generate new piece

### clearLines
Triggered by: Piece lock after filling rows
Reads: grid, score
Writes: grid, score
Calls: 
  1. Scan grid for full rows (all cells filled)
  2. For each full row, increment score by 100
  3. Shift rows down and clear top row if needed

### togglePause
Triggered by: Start/Pause button click
Reads: gameState
Writes: gameState
Calls: 
  1. Set gameState to !gameState
  2. If paused, stop interval; if resumed, restart interval

## Render strategy
DOM manipulation using CSS transforms for piece positioning, with grid lines and block colors applied via inline styles. Grid cells are updated in real-time as pieces move/lock.

## Render integration (CRITICAL)
drawBoard() must draw the 10x20 grid with filled cells from grid[][] array, overlaying currentPiece's shape at its current x/y position, and displaying score and nextPiece color preview.

## Timing (CRITICAL)
Use setInterval at 500ms for game ticks to control piece drop speed, not requestAnimationFrame which would cause inconsistent timing.

## Critical mechanisms
- When rotating, the algorithm must first rotate the shape matrix, then checkCollision() at (x, y+1) to detect wall kicks, then adjust position if needed before updating grid.

## Pitfalls
- Using requestAnimationFrame for game ticks causes pieces to fall at 60fps and lock immediately, breaking Tetris timing rules
- Not initializing nextPiece color correctly leads to incorrect preview display
- Missing checkCollision() implementation in rotate() causes pieces to clip through grid
- Forgetting to update grid visualization after movement/rotation results in stale display