# Technical Design

**Project type**: game

## State variables
- `grid` (array, int[20][10]) — tracks the state of each cell in the grid (0 for empty, 1 for filled) — init: `new Array(20).fill(0).map(() => new Array(10).fill(0))`
- `currentPiece` (object, {type: string, x: int, y: int, rotation: int}) — tracks the current Tetrimino's type, position, and rotation — init: `null`
- `score` (number, int) — tracks the player's score — init: `0`
- `gameOver` (boolean, bool) — indicates if the game is over — init: `false`
- `paused` (boolean, bool) — indicates if the game is paused — init: `false`

## Algorithms

### initializeGame
Triggered by: when the game starts
Reads: 
Writes: grid, score, gameOver, paused, currentPiece
Calls: 
  1. set grid to initial state
  2. set score to 0
  3. set gameOver to false
  4. set paused to false
  5. spawn a new Tetrimino

### spawnPiece
Triggered by: when a new Tetrimino needs to be spawned
Reads: 
Writes: currentPiece
Calls: 
  1. select a random Tetrimino type
  2. set currentPiece to {type, x: 4, y: 0, rotation: 0}

### movePiece
Triggered by: arrow key input
Reads: grid, currentPiece
Writes: currentPiece
Calls: checkCollision
  1. check if the move is valid
  2. if valid, update currentPiece's x or y position

### rotatePiece
Triggered by: up arrow key input
Reads: grid, currentPiece
Writes: currentPiece
Calls: checkCollision
  1. check if the rotation is valid
  2. if valid, update currentPiece's rotation

### dropPiece
Triggered by: spacebar input
Reads: grid, currentPiece
Writes: grid, score, currentPiece
Calls: checkCollision, clearLines, spawnPiece
  1. move piece down until it collides
  2. lock the piece in place
  3. clear lines
  4. spawn a new piece

### checkCollision
Triggered by: movePiece, rotatePiece, dropPiece
Reads: grid, currentPiece
Writes: 
Calls: 
  1. check if the piece's new position collides with the grid boundaries or other pieces
  2. return true if collision, false otherwise

### clearLines
Triggered by: dropPiece
Reads: grid
Writes: grid, score
Calls: 
  1. check for full lines
  2. remove full lines from the grid
  3. increment score based on number of lines cleared

### checkGameOver
Triggered by: spawnPiece
Reads: grid, currentPiece
Writes: gameOver
Calls: 
  1. check if the new piece collides with the top of the grid
  2. if true, set gameOver to true

### togglePause
Triggered by: P key input
Reads: paused
Writes: paused
Calls: startGameLoop, stopGameLoop
  1. toggle paused state
  2. if paused, stop game loop
  3. if unpaused, resume game loop

### startGameLoop
Triggered by: initializeGame, togglePause
Reads: 
Writes: 
Calls: 
  1. use setInterval to call gameTick every 500ms

### stopGameLoop
Triggered by: togglePause
Reads: 
Writes: 
Calls: 
  1. clear the interval set by startGameLoop

### gameTick
Triggered by: game loop
Reads: grid, currentPiece, gameOver
Writes: grid, score, currentPiece
Calls: checkCollision, clearLines, spawnPiece
  1. move currentPiece down
  2. if collision, lock piece and clear lines
  3. spawn new piece if necessary

## Render strategy
The render function will update the grid display based on the current state of the grid and currentPiece. It will also update the score display.

## Render integration (CRITICAL)
drawBoard() must draw BOTH board[][] locked cells AND currentPiece at its current x/y position — drawing only board[][] is wrong

## Timing (CRITICAL)
use setInterval at 500ms for game ticks, NOT requestAnimationFrame which runs at 60fps and would make pieces fall instantly

## Critical mechanisms
- The game loop must use setInterval to ensure consistent game speed regardless of frame rate. Using requestAnimationFrame would cause pieces to fall at 60fps and lock immediately.

## Pitfalls
- Using requestAnimationFrame for game ticks causes pieces to fall at 60fps and lock immediately.