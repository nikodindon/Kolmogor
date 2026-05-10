# Project: Tetris Game
## Target
JavaScript in browser (single HTML file)
## Files
- `index.html` — Contains HTML structure, embedded CSS for styling, and embedded JavaScript for game logic, rendering, and input handling.
## Features
1. Board renders as a 10-column by 20-row grid with visible cell boundaries.
2. Seven distinct tetromino shapes (I, O, T, S, Z, J, L) spawn with unique colors.
3. Active piece moves left or right when corresponding arrow key is pressed and path is valid.
4. Active piece rotates 90 degrees clockwise when Up arrow is pressed and rotation is valid.
5. Active piece descends faster when Down arrow is held.
6. Active piece instantly moves to lowest valid position when Space is pressed.
7. Full rows are removed, upper rows shift down, and score increases by 100, 300, 500, or 800 points for 1 to 4 lines cleared.
8. Game ends when a new piece cannot spawn without immediate collision with existing blocks or boundaries.
9. Next piece shape is rendered in a dedicated preview panel.
10. Drop speed increases by 10% for every 10 lines cleared.
## Visual guidelines
- Background: #202028
- Grid cells: #101018
- Grid borders: #303038
- Board frame: #000000
- Text color: #e0e0e0
- Font: 'Courier New', monospace
- Layout: Flexbox centered container, board 300px wide, side panel 150px wide
- Interactive states: Ghost piece rendered at 50% opacity indicating landing position
- Piece colors: #00f0f0 (Cyan), #f0f000 (Yellow), #a000f0 (Purple), #00f000 (Green), #f00000 (Red), #0000f0 (Blue), #f0a000 (Orange)
## Controls
- Arrow Left: Move piece left
- Arrow Right: Move piece right
- Arrow Down: Soft drop (accelerate descent)
- Arrow Up: Rotate piece clockwise
- Space: Hard drop (instant placement)
- P: Pause/Resume game
## Technical constraints
- Single file `index.html` only
- All CSS inside `<style>` tag
- All JavaScript inside `<script>` tag
- No external files, imports, or libraries
- Rendering via Canvas 2D context
- Game loop driven by `requestAnimationFrame`

## Revision notes
1. Missing `movePiece` algorithm: `handleInput` references it for Left/Right movement, but no implementation or movement step logic is provided in the Algorithms section.
2. Missing `rotatePiece` algorithm: `handleInput` references it for Up arrow rotation, but no implementation or collision-checking logic is provided in the Algorithms section.
3. `clearLines` speed increase condition `lines >= 10` does not match the spec requirement "every 10 lines cleared"; it lacks a modulo check or level tracking to correctly trigger the speed increase at intervals of 10.
4. `handleInput` toggles `isPaused` but does not reset `lastTime` or `timeAccumulator`, which will cause a massive time jump and erratic movement upon resuming the game.
5. `gameLoop` timing subtraction: `subtract dropInterval from timeAccumulator` only subtracts once, leaving a large remainder if `timeAccumulator` exceeds `dropInterval` significantly (e.g., during soft drop or browser throttling), causing erratic movement or frame skipping.

## Revision notes
1. `clearLines` scoring formula uses the total `lines` counter instead of the number of lines cleared in the current lock, and the additive expression `100 * lines + 300 * lines + 500 * lines + 800 * lines` does not implement the spec's tiered scoring (100/300/500/800 for 1-4 lines).
2. `checkCollision` is referenced by `movePiece`, `rotatePiece`, `spawnPiece`, and `calculateGhostY` but is not defined as an algorithm or mechanism in the Technical Design.
3. `calculateGhostY` sets `ghostY = currentPiece.y - 1` after the descent loop breaks on collision. Since `movePiece` does not update coordinates when a collision is detected, `currentPiece.y` is already at the lowest valid position, causing the ghost piece to render one cell too high.
4. `handleInput` toggles `isPaused` but only resets `timeAccumulator` and `lastTime` when `isPaused` evaluates to true. Upon resuming (when `isPaused` becomes false), these variables are not reset, causing a massive time jump and erratic movement on the next frame.
5. `handleInput` only calls `softDrop()` on keydown events. It lacks logic to handle the Down arrow being held continuously, leaving the "descends faster when held" feature without an implementation path.