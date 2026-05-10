# Project: Pong AI
## Target
JavaScript (single_html)
## Files
- `index.html` — Contains HTML structure, embedded CSS for styling, and inline JavaScript for game logic and AI control
## Features
1. Player controls paddle movement via keyboard (W/S or arrow keys) to hit ball, with collision detection and scoring
2. AI opponent moves to intercept ball using simple predictive algorithm, with score tracking and game reset functionality
## Visual guidelines
- Background: `#000000`
- Player paddle: `#00FF00`
- AI paddle: `#0000FF`
- Ball: `#FFFFFF`
- Score text: `#FFFFFF` with `font-family: sans-serif` and `font-size: 24px`
- Reset button: `background: #FF0000` on normal state, `background: #CC0000` on hover
## Controls
- Player up: W or ↑
- Player down: S or ↓
- Reset game: Click "Reset" button
## Technical constraints
- All code must be contained within a single `index.html` file
- No external resources, imports, or network requests allowed
- All CSS must be in a `<style>` tag, all JS in a `<script>` tag
- Game state must be managed entirely through JavaScript DOM manipulation