# Technical Design

**Project type**: game

## State variables
- `ballPosition` (object, {x: number, y: number}) — Tracks the ball's current position, updated on each game tick — init: `{x: 150, y: 150}`
- `ballVelocity` (object, {x: number, y: number}) — Tracks the ball's direction and speed, reversed on collision — init: `{x: 2, y: 2}`
- `playerPaddle` (object, {x: number, y: number}) — Tracks player paddle position, updated on key press — init: `{x: 50, y: 150}`
- `aiPaddle` (object, {x: number, y: number}) — Tracks AI paddle position, updated by predictive algorithm — init: `{x: 250, y: 150}`
- `score` (object, {player: number, ai: number}) — Tracks scores for both players — init: `{player: 0, ai: 0}`
- `gameState` (string, 'running' | 'over') — Tracks whether game is active or ended — init: `'running'`

## Algorithms

### updateBallPosition
Triggered by: game tick interval
Reads: ballPosition, ballVelocity, playerPaddle, aiPaddle
Writes: ballPosition, ballVelocity
Calls: checkScore, updateGameState
  1. Add ballVelocity.x to ballPosition.x
  2. Add ballVelocity.y to ballPosition.y
  3. Check wall collisions and reverse velocity if needed
  4. Check paddle collisions and reverse velocity if needed

### predictAIPath
Triggered by: game tick interval
Reads: ballPosition, ballVelocity, aiPaddle
Writes: aiPaddle
Calls: 
  1. Calculate ball trajectory based on current velocity
  2. Predict where ball will hit the AI paddle
  3. Move AI paddle toward predicted position

### checkScore
Triggered by: ball position update
Reads: ballPosition, score
Writes: score, gameState
Calls: 
  1. Check if ball passed player paddle
  2. Check if ball passed AI paddle
  3. Increment score for respective player

### updateGameState
Triggered by: score check
Reads: gameState, score
Writes: gameState
Calls: 
  1. If gameState is 'running' and ball passed paddle, set to 'over'

## Render strategy
Canvas-based rendering with fixed dimensions (400x600), redrawing all elements on each game tick

## Render integration (CRITICAL)
Draw player paddle at playerPaddle.x/y, AI paddle at aiPaddle.x/y, ball at ballPosition.x/y, score text with current values, and reset button with hover state

## Timing (CRITICAL)
Use setInterval with 16ms interval (60fps) for game ticks, not requestAnimationFrame

## Critical mechanisms
- When ball collides with paddle, reverse ballVelocity.y and update ballPosition immediately before next tick
- AI prediction algorithm must calculate ball trajectory based on current ballVelocity and predict landing position on AI paddle

## Pitfalls
- Using requestAnimationFrame for game ticks instead of setInterval(16) causes inconsistent ball movement and scoring
- Forgetting to reset ballPosition and ballVelocity when resetting game state
- Not checking both paddle collision conditions in updateBallPosition algorithm