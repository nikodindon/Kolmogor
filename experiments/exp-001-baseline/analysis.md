# exp-001-baseline — Analysis

## Objective

Establish the pipeline baseline with Qwen2.5-Coder-7B Q5_K_M on a Tetris prompt.
Tetris was chosen as the canonical "non-trivial game" benchmark — more complex than Snake,
well-known enough that a 7B model should have strong training signal on it.

## Runs

| Run | Target | Cycles | Verdict | Notes |
|---|---|---|---|---|
| run-001 | auto → python_pygame | 5 | STALL | Multi-file Pygame, first run ever |
| run-002 | auto → python_pygame | 5 | STALL | snapshot_limit 1500, same result |
| run-003 | auto → python_pygame | 6 | ERROR | HTTP timeout 600s |
| run-004 | auto → python_pygame | — | — | (skipped in log, part of run-003 batch) |
| run-005 | forced html_js | 5 | STALL | Multi-file HTML, same cross-file issue |
| run-006 | forced single_html | 2 | ERROR | HTTP timeout 600s, token ceiling |
| run-007 | forced single_html | 3 | ERROR | HTTP timeout 900s, file grew to 6088 chars |
| run-008 | forced single_html | 4 | STALL | HTTP timeout 1800s, token ceiling confirmed |

## Conclusion

**Tetris is above the Qwen2.5-Coder-7B Q5_K_M decompression threshold for single_html.**

This is not a pipeline failure. Every pipeline bug has been found and fixed. The stall in
run-008 is clean — the model generates a correct scaffold with all function calls present,
then runs out of token budget before implementing the function bodies.

The specific functions that fail across all runs: `moveTetrimino`, `rotateTetrimino`,
`dropTetrimino`, `clearLines`, `startGame`, `pauseGame`. These are the most logic-dense
functions in a Tetris implementation. The model knows they are needed (it calls them)
but cannot generate their bodies within its effective generation window.

## What the multi-file runs taught us (run-001 to run-005)

These runs revealed two distinct failure modes:

The first is **Critic cross-file hallucination**: the Critic reports missing methods that
actually exist in the generated files. The text-only snapshot fed to the Critic truncates
or presents files in a way that causes phantom missing-method reports.

The second is the **token ceiling problem**, which only became visible once we switched to
single_html. Previously, the multi-file failures were masking it.

## The token ceiling problem in detail

The 7B model generates approximately 900-1465 tokens per completion call. Tetris requires
approximately 1800-2200 tokens of JS logic for a complete single-file implementation.
The gap between model capacity and artifact requirement is ~400-700 tokens.

No amount of fix cycling closes this gap because the fix calls regenerate the same
truncated file — the model always runs out of budget at the same logical point.

## Path forward

Two approaches to explore:

**Scope reduction**: "build a minimal Tetris — falling pieces, left/right movement only.
No rotation, no line clearing, no scoring." Reduces required functions from ~8 to ~4.

**Explicit budget prompting**: Give the Coder an explicit instruction: "implement all
functions completely. If you must choose, implement the game loop and movement first.
Do not write function stubs." Tests whether the model can prioritize within its budget.
