# Project: Tetris Game
## Target
JavaScript (single_html)
## Files
- `index.html` — Contains the complete HTML structure, embedded CSS, and inline JavaScript for Tetris game logic, with no external dependencies
## Features
1. A 10x20 grid of colored blocks rendered as `<div>` elements with dynamic positioning and collision detection
2. Piece rotation, movement, and line-clearing mechanics with score tracking (score variable increments by 100 per line cleared)
## Visual guidelines
- Background: `#1e1e1e`
- Grid lines: `#000` (black)
- Block colors: `#00ff00` (green), `#0000ff` (blue), `#ff0000` (red), `#ffff00` (yellow), `#00ffff` (cyan), `#ff00ff` (magenta)
- Typography: `sans-serif`, font size `16px`
- Button hover state: `background-color: #333`
## Controls
- Arrow keys (left/right/down) for piece movement
- Up arrow for rotation
- Spacebar to drop piece instantly
- "Start/Pause" button click
## Technical constraints
- All CSS must be in a `<style>` tag within index.html
- All JavaScript must be in a `<script>` tag within index.html
- No external files, imports, or libraries allowed
- Game state must be implemented with pure DOM manipulation and JavaScript timers

## Revision notes
1. The "Start/Pause" button functionality is not implemented. The technical design lacks a state variable to track game state (paused or not) and no algorithm handles pausing/resuming the game when the button is clicked.
2. The `currentPiece` color is initialized to green, but the specification requires multiple block colors (green, blue, red, etc.). The technical design does not define how different tetromino types map to their respective colors, leading to potential rendering inconsistencies.
3. The `checkCollision` function is referenced in multiple algorithms but is not defined in the technical design. This critical mechanism is required for collision detection during movement and rotation, but its implementation is missing.