# Technical Design

**Project type**: game

## State variables
- `board` (array, int[20][10]) — represents the playing field with 20 rows and 10 columns — init: `new Array(20).fill(null).map(() => new Array(10).fill(0))`
- `currentPiece` (object, {type: string, x: int, y: int, rotation: int}) — tracks the current Tetrimino's type, position, and rotation — init: `null`
- `score` (number, int) — keeps track of the player's score — init: `0`
- `gameOver` (boolean, bool) — indicates whether the game is over — init: `false`
- `paused` (boolean, bool) — indicates whether the game is paused — init: `false`

## Algorithms

### spawnPiece
Triggered by: when a new piece needs to be spawned
Reads: 
Writes: currentPiece
  1. Choose a random Tetrimino type
  2. Set the piece's initial position at the top center of the board
  3. Set the piece's rotation to 0
  4. Update the currentPiece state variable

### movePiece
Triggered by: arrow key presses
Reads: currentPiece, board
Writes: currentPiece
  1. Check if the move is valid
  2. Update the piece's position
  3. Redraw the board

### rotatePiece
Triggered by: up arrow key press
Reads: currentPiece, board
Writes: currentPiece
  1. Check if the rotation is valid
  2. Update the piece's rotation
  3. Redraw the board

### dropPiece
Triggered by: spacebar press
Reads: currentPiece, board
Writes: board, score, currentPiece
  1. Move the piece down until it can't move further
  2. Lock the piece in place
  3. Clear completed lines
  4. Update the score
  5. Spawn a new piece

### lockPiece
Triggered by: when a piece can't move further
Reads: currentPiece, board
Writes: board, score, currentPiece, gameOver
  1. Write the piece's cells to the board
  2. Check for game over
  3. Clear completed lines
  4. Update the score
  5. Spawn a new piece

### clearLines
Triggered by: when a line is completed
Reads: board
Writes: board, score
  1. Remove the completed line from the board
  2. Shift all rows above the cleared line down
  3. Update the score

### checkGameOver
Triggered by: when a new piece is spawned
Reads: currentPiece, board
Writes: gameOver
  1. Check if the new piece overlaps with any existing cells
  2. If it does, set gameOver to true

## Render strategy
full redraw from board[][] every tick

## Critical mechanisms
- piece locking: when downward movement is blocked, current piece cells are written to board[][] permanently and a new piece spawns
- line clearing: when a line is completed, all rows above the cleared line are shifted down
- game over condition: when a new piece spawns and overlaps with existing cells, the game is over

## Pitfalls
- forgetting to check for game over when a new piece is spawned
- not updating the score correctly when lines are cleared
- not properly handling piece rotation and movement validation