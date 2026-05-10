# Technical Design

**Project type**: game

## State variables
- `board` (array, int[20][10]) — Stores the grid state. 0 represents empty cells, positive integers represent locked piece colors. — init: `20x10 array filled with 0`
- `currentPiece` (object, { shape: int[4][2], x: int, y: int, color: string }) — Tracks the active tetromino shape (array of relative coordinates), position (x, y), and color. — init: `null`
- `nextPiece` (object, { shape: int[4][2], color: string }) — Stores the shape and color of the upcoming piece for the preview panel. — init: `null`
- `score` (number, int) — Accumulates points from line clears. — init: `0`
- `lines` (number, int) — Tracks total lines cleared to determine speed level. — init: `0`
- `dropInterval` (number, int) — Time in milliseconds between automatic piece descents. Decreases as lines are cleared. — init: `1000`
- `lastTime` (number, int) — Timestamp of the previous frame for delta time calculation. — init: `0`
- `timeAccumulator` (number, int) — Accumulates elapsed time to trigger piece descents at fixed intervals. — init: `0`
- `isPaused` (boolean, bool) — Indicates if the game loop is suspended. — init: `false`
- `isGameOver` (boolean, bool) — Indicates if the game has ended due to collision on spawn. — init: `false`
- `ghostY` (number, int) — Tracks the lowest valid Y position for the current piece to indicate landing spot. — init: `0`

## Algorithms

### initGame
Triggered by: Page load or restart
Reads: 
Writes: board, currentPiece, nextPiece, score, lines, dropInterval, lastTime, timeAccumulator, isPaused, isGameOver, ghostY
Calls: spawnPiece
  1. Reset board to 20x10 zeros.
  2. Reset score, lines, timeAccumulator, lastTime.
  3. Reset isPaused, isGameOver to false.
  4. Set dropInterval to 1000.
  5. Spawn first piece and next piece.
  6. Calculate ghostY.

### spawnPiece
Triggered by: initGame or after lockPiece
Reads: board
Writes: currentPiece, nextPiece, isGameOver, ghostY
Calls: checkCollision, calculateGhostY
  1. Generate random shape and color for currentPiece.
  2. Set currentPiece x to 3, y to 0.
  3. Check collision at spawn position.
  4. If collision, set isGameOver = true.
  5. Else, assign nextPiece to currentPiece, generate new nextPiece.
  6. Calculate ghostY.

### movePiece
Triggered by: handleInput (Left/Right) or gameLoop (Down)
Reads: currentPiece, board
Writes: currentPiece
Calls: checkCollision
  1. Calculate new x = currentPiece.x + dx, new y = currentPiece.y + dy.
  2. Check bounds and collision with board at new position.
  3. If valid, update currentPiece.x and currentPiece.y.
  4. Return true.
  5. If invalid, return false.

### rotatePiece
Triggered by: handleInput (Up)
Reads: currentPiece, board
Writes: currentPiece
Calls: checkCollision
  1. Calculate rotated shape coordinates (90 deg clockwise).
  2. Check bounds and collision with board at rotated position.
  3. If valid, update currentPiece.shape.
  4. If invalid, do nothing (no wall kick per spec constraints).

### hardDrop
Triggered by: handleInput (Space)
Reads: currentPiece, board
Writes: currentPiece, board, score, lines, dropInterval, nextPiece, ghostY
Calls: movePiece, lockPiece
  1. Loop: Call movePiece(0, 1).
  2. If movePiece returns false, break loop.
  3. After loop, call lockPiece().

### softDrop
Triggered by: handleInput (Down held) or gameLoop (timeAccumulator)
Reads: currentPiece, board
Writes: currentPiece, board, score, lines, dropInterval, nextPiece, ghostY
Calls: movePiece, lockPiece
  1. Call movePiece(0, 1).
  2. If movePiece returns false, call lockPiece().

### lockPiece
Triggered by: movePiece returns false or hardDrop completes
Reads: currentPiece, board, score, lines, dropInterval
Writes: board, score, lines, dropInterval, nextPiece, currentPiece, ghostY
Calls: clearLines, spawnPiece
  1. Copy currentPiece shape to board at currentPiece.x, currentPiece.y.
  2. Call clearLines().
  3. Call spawnPiece().

### clearLines
Triggered by: lockPiece
Reads: board, score, lines, dropInterval
Writes: board, score, lines, dropInterval
Calls: 
  1. Scan board rows from bottom to top.
  2. Identify full rows (no zeros).
  3. Remove full rows and shift upper rows down.
  4. Calculate points: 100 * lines + 300 * lines + 500 * lines + 800 * lines.
  5. Add points to score.
  6. Increment lines count.
  7. Update dropInterval: dropInterval = 1000 * Math.pow(0.9, Math.floor(lines / 10)).

### calculateGhostY
Triggered by: spawnPiece, movePiece, rotatePiece
Reads: currentPiece, board
Writes: ghostY, currentPiece
Calls: movePiece
  1. Save currentPiece.y.
  2. Set currentPiece.y to 0.
  3. Loop: Call movePiece(0, 1).
  4. If movePiece returns false, break.
  5. Set ghostY = currentPiece.y - 1.
  6. Restore currentPiece.y to saved value.

### handleInput
Triggered by: keydown event
Reads: isGameOver, isPaused
Writes: isPaused, timeAccumulator, lastTime
Calls: movePiece, rotatePiece, hardDrop, softDrop
  1. If isGameOver, return.
  2. If key is 'p' or 'P': Toggle isPaused.
  3. If isPaused: Reset timeAccumulator = 0, lastTime = timestamp. Return.
  4. If key is ArrowLeft: Call movePiece(-1, 0).
  5. If key is ArrowRight: Call movePiece(1, 0).
  6. If key is ArrowUp: Call rotatePiece().
  7. If key is Space: Call hardDrop().
  8. If key is ArrowDown: Call softDrop().

### gameLoop
Triggered by: requestAnimationFrame
Reads: isPaused, isGameOver, timeAccumulator, dropInterval
Writes: timeAccumulator, lastTime
Calls: softDrop, render
  1. If isPaused or isGameOver: requestAnimationFrame(gameLoop). Return.
  2. Calculate delta = timestamp - lastTime.
  3. Update lastTime = timestamp.
  4. Update timeAccumulator += delta.
  5. While timeAccumulator >= dropInterval: Call softDrop(). timeAccumulator -= dropInterval.
  6. If isGameOver: requestAnimationFrame(gameLoop). Return.
  7. Call render().

## Render strategy
Canvas 2D context is cleared every frame. The board grid is drawn first, followed by locked cells, then the ghost piece, and finally the current piece. UI elements (score, next piece) are drawn last.

## Render integration (CRITICAL)
CRITICAL: render() must draw the board grid lines, all locked cells from board[][] with their colors, the ghost piece at ghostY with 50% opacity, the current piece at currentPiece.x/currentPiece.y, and the UI panel showing score, lines, and nextPiece shape. Drawing only the board or missing the ghost piece is incorrect.

## Timing (CRITICAL)
Use requestAnimationFrame for the game loop. Accumulate delta time in timeAccumulator. When timeAccumulator >= dropInterval, call softDrop() and subtract dropInterval from timeAccumulator. Handle soft drop by calling softDrop() immediately on keydown or by adding extra time to accumulator. Pause must reset timeAccumulator to 0 and lastTime to current timestamp to prevent time jump.

## Critical mechanisms
- Hard drop sequence: Loop movePiece(0, 1) until collision, then immediately call lockPiece() which triggers clearLines() and spawnPiece().
- Rotation validation: Calculate new shape, check bounds and collision, only apply if valid.
- Speed increase: Calculate level as Math.floor(lines / 10), update dropInterval = 1000 * Math.pow(0.9, level).

## Pitfalls
- Using requestAnimationFrame without time accumulation causes pieces to fall at 60fps instead of the configured dropInterval.
- Not resetting timeAccumulator and lastTime on pause causes a massive time jump and erratic movement upon resume.
- Subtracting dropInterval only once from timeAccumulator leaves a large remainder, causing erratic movement or frame skipping.
- Rotation without checking collision against board boundaries causes pieces to clip or get stuck.
- Hard drop not locking the piece immediately causes the piece to continue falling or disappear.
- Line clear not shifting rows correctly causes gaps or duplicate rows.