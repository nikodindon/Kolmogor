# Model Matrix

Comparison table updated after each experiment batch.
A dash means not yet tested. A question mark means tested but result inconclusive.

---

## Complexity threshold map — Qwen2.5-Coder-7B Q5_K_M, single_html

| Prompt | Seed bytes | Functions required | Status | Peak artifact | Cycles | Compression |
|---|---|---|---|---|---|---|
| build a Snake game | 18 | ~4 simple | ✓ ALL_COMPLETE | 4149 bytes | 1 | 0.0043 |
| build a Pong game | TBD | ~5 simple | To test | — | — | — |
| build a Tetris (minimal) | TBD | ~5 medium | To test | — | — | — |
| build a playable Tetris game | 28 | ~8 medium | ✗ STALL | 4569 bytes | 4 | — |
| build a classic Asteroid arcade game | 36 | ~8 complex | ✗ STALL | 5001 bytes | 4 | — |
| build a classic Asteroid + sounds | 67 | ~10 complex | ✗ STALL | 5393 bytes | 5 | — |

**Threshold location:** between Snake (~4 simple functions, succeeds) and Tetris (~8 medium functions, fails). The model can scaffold any of these but cannot fill all function bodies within its effective token generation budget.

---

## Model size comparison — Snake prompt (single_html)

| Model | Quant | Cycles | Verdict | Functional | Visual | Compression | Notes |
|---|---|---|---|---|---|---|---|
| Qwen2.5-Coder-7B | Q5_K_M | 1 | ✓ ALL_COMPLETE | PASS | 9.0/10 | 0.0043 | Baseline |
| Qwen2.5-Coder-3B | Q6_K | — | — | — | — | — | Planned exp-004 |
| Qwen2.5-Coder-1.5B | Q8 | — | — | — | — | — | Planned |

---

## Coder output variance — Snake, temperature=0

Two stable output clusters observed. Variance traces to Designer pre-code guidelines (not fully deterministic).

| Cluster | Coder tokens | Artifact chars | Runs |
|---|---|---|---|
| A | 911 | 3936 | run-001, run-004 |
| B | 998 | 4149 | run-002, run-005, run-006 |

Architect output is fully deterministic (797 chars, 203 tokens, identical across all Snake runs).

---

## Key findings

**Finding 1 — Multi-file is above repair loop capacity at 7B.** Multi-file Pygame or HTML/JS causes Critic cross-file hallucination. Single-file eliminates this entirely.

**Finding 2 — Token ceiling is the binding constraint for complex single-file prompts.** The 7B hits a generation ceiling of ~1100-1465 tokens per pass. Simple games (Snake) fit. Complex games (Tetris, Asteroid) overflow.

**Finding 3 — Coder output is deterministic given identical input.** Variance between runs traces entirely to non-deterministic Designer pre-code guidelines call.

**Finding 4 — The 7B model prefers DOM over Canvas.** All Snake runs produce div-based rendering. Observed in Tetris and Asteroid specs too (they use canvas for board but DOM for UI).

**Finding 5 — Compression baseline: 0.0043 for Snake.** 18 bytes → 4149 bytes. First validated data point.

**Finding 6 — Asteroid is above 7B threshold regardless of sound inclusion.** Both prompts (with and without sounds) stall at similar file sizes. Core game logic volume is the constraint.

**Finding 7 — HTTP timeout was masking progress.** Tetris run-007 showed 13% file growth between cycles when timeout was raised. But the stall is a token ceiling issue, not a time issue.

**Finding 8 — Token generation ceiling varies with input context size.** Ceiling is not fixed: ranges from 911 tokens (small context) to 1615 tokens (larger context). Depends on prompt token count.

**Finding 9 — Decompression threshold lies between Snake and Tetris.** 18-byte seed (Snake, ~4 functions) succeeds. 28-byte seed (Tetris, ~8 functions) fails. The boundary is function count and complexity, not seed byte count.

---

## Bug history

| Date | Component | Bug | Fix | First clean run |
|---|---|---|---|---|
| 2026-04-26 | loop.py | Planner called with empty issues | `if not issues: break` | run-005 exp-001 |
| 2026-04-26 | llm.py | HTTP timeout 600s | Raised to 900s | run-004 exp-001 |
| 2026-04-27 | planner.py | Same file duplicated in fix plan | `_deduplicate()` | run-005 exp-001 |
| 2026-04-27 | coder.py | Deterministic fix loop at temp=0 | fix_history injected | run-005 exp-001 |
| 2026-04-27 | executor.py | canvas_present false-negative on DOM | arcade_game_canvas/dom split | run-006 exp-002 ✓ |
| 2026-04-28 | llm.py | HTTP timeout 900s | Raised to 1800s | run-008 exp-001 |
