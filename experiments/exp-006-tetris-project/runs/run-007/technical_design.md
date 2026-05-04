# Technical Design

**Project type**: game

## State variables
- `grid` (array, int[20][10]) — tracks the state of the game grid, 0 for empty, 1 for filled — init: `new Array(20).fill(0).map(() => new Array(10).fill(0))`
- `currentPiece` (object, {type: string, x: int, y: int, rotation: int}) — tracks the current piece being played — init: `null`
- `score` (number, int) — tracks the player's score — init: `0`
- `gameOver` (boolean, bool) — indicates if the game is over — init: `false`

## Algorithms

### initializeGame
Triggered by: when the game starts
Reads: 
Writes: grid, score, gameOver, currentPiece
Calls: 
  1. set grid to initial value
  2. set score to 0
  3. set gameOver to false
  4. spawn a new piece

### spawnPiece
Triggered by: when a piece lands or at the start of the game
Reads: 
Writes: currentPiece
Calls: 
  1. select a random piece type
  2. set currentPiece to {type: selectedType, x: 4, y: 0, rotation: 0}

### movePiece
Triggered by: arrow key press
Reads: grid, currentPiece
Writes: currentPiece
Calls: 
  1. check if the move is valid
  2. if valid, update currentPiece's x or y
  3. if invalid, revert the move

### rotatePiece
Triggered by: up arrow key press
Reads: grid, currentPiece
Writes: currentPiece
Calls: 
  1. check if the rotation is valid
  2. if valid, update currentPiece's rotation
  3. if invalid, revert the rotation

### checkCollision
Triggered by: movePiece or rotatePiece
Reads: grid, currentPiece
Writes: 
Calls: 
  1. check if the piece collides with the grid boundaries or other pieces
  2. return true if collision, false otherwise

### lockPiece
Triggered by: piece reaches the bottom or collides with another piece
Reads: grid, currentPiece
Writes: grid, score
Calls: clearLines
  1. set the piece's cells in the grid to 1
  2. check for full lines and clear them
  3. update score
  4. spawn a new piece

### clearLines
Triggered by: lockPiece
Reads: grid
Writes: grid
Calls: 
  1. find full lines
  2. remove full lines from the grid
  3. shift remaining lines down

### checkGameOver
Triggered by: lockPiece
Reads: grid, currentPiece
Writes: gameOver
Calls: 
  1. check if the new piece cannot be spawned
  2. if true, set gameOver to true

## Render strategy
use a game loop to update the visual state based on the game state

## Render integration (CRITICAL)
drawBoard() must draw BOTH board[][] locked cells AND currentPiece at its current x/y position — drawing only board[][] is wrong

## Timing (CRITICAL)
use setInterval at 500ms for game ticks, NOT requestAnimationFrame which runs at 60fps and would make pieces fall instantly

## Critical mechanisms
- the game loop must handle both game logic and rendering to ensure smooth gameplay

## Pitfalls
- using requestAnimationFrame for game ticks causes pieces to fall at 60fps and lock immediately