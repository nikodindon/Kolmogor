# Technical Design

**Project type**: game

## State variables
- `grid` (array, int[20][10]) — tracks the state of the game grid, 0 for empty, 1-7 for different Tetriminos — init: `new Array(20).fill(0).map(() => new Array(10).fill(0))`
- `currentPiece` (object, {type: string, x: int, y: int, rotation: int}) — tracks the current Tetrimino, its type, position, and rotation — init: `null`
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
  5. generate and place a new Tetrimino

### generatePiece
Triggered by: when a new Tetrimino is needed
Reads: 
Writes: currentPiece
Calls: 
  1. randomly select a Tetrimino type
  2. set currentPiece to {type, x: 4, y: 0, rotation: 0}

### movePiece
Triggered by: arrow key inputs
Reads: grid, currentPiece
Writes: currentPiece
Calls: 
  1. check if the move is valid
  2. if valid, update currentPiece's x or y
  3. if invalid, do nothing

### rotatePiece
Triggered by: up arrow key input
Reads: grid, currentPiece
Writes: currentPiece
Calls: 
  1. check if the rotation is valid
  2. if valid, update currentPiece's rotation
  3. if invalid, do nothing

### dropPiece
Triggered by: spacebar input
Reads: grid, currentPiece
Writes: grid, currentPiece
Calls: 
  1. move piece down until it can't move further

### clearLines
Triggered by: piece placement
Reads: grid
Writes: grid, score
Calls: 
  1. check for full lines
  2. if full, clear the line and add to score
  3. shift all above lines down

### checkGameOver
Triggered by: piece placement
Reads: grid, currentPiece
Writes: gameOver
Calls: 
  1. check if the new piece can't be placed
  2. if so, set gameOver to true

### gameTick
Triggered by: game loop
Reads: grid, currentPiece, gameOver, paused
Writes: grid, currentPiece, score, gameOver
Calls: clearLines, checkGameOver
  1. move currentPiece down
  2. if piece can't move, place it and generate a new piece
  3. clear lines
  4. check game over

## Render strategy
use a game loop to update the grid and currentPiece state, then redraw the grid and pieces

## Render integration (CRITICAL)
drawBoard() must draw BOTH board[][] locked cells AND currentPiece at its current x/y position — drawing only board[][] is wrong

## Timing (CRITICAL)
use setInterval at 500ms for game ticks, NOT requestAnimationFrame which runs at 60fps and would make pieces fall instantly

## Critical mechanisms
- gameTick() must check if the game is paused before proceeding

## Pitfalls
- using requestAnimationFrame for game ticks causes pieces to fall at 60fps and lock immediately