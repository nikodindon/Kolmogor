# Model Matrix

Comparison table updated after each experiment batch.
A dash means not yet tested. A question mark means inconclusive.

---

## Complexity threshold map — Qwen2.5-Coder-7B Q5_K_M, single_html

| Prompt | Seed bytes | Functions | Status | Cycles | Artifact | Compression |
|---|---|---|---|---|---|---|
| build a Pong game | 17 | ~4 simple | ✓ ALL_COMPLETE | 1 | 3026 bytes | 0.0056 |
| build a Snake game | 18 | ~4 simple | ✓ ALL_COMPLETE | 1 | 4149 bytes | 0.0043 |
| build a minimal Tetris (scope reduced) | 99 | ~4 medium | ✓ ALL_COMPLETE | 2 | 3059 bytes | 0.0324 |
| build a playable Tetris game | 28 | ~8 medium | ✗ STALL | 4 | 4569 bytes | — |
| build a classic Asteroid arcade game | 36 | ~8 complex | ✗ STALL | 4 | 5001 bytes | — |

**Threshold**: ~4 fully implemented functions fit in budget. ~8 do not. Scope reduction via enriched seed works but degrades compression ratio dramatically (0.0043 → 0.0324).

---

## Model size comparison — Snake prompt, single_html

| Model | Quant | Cycles | Verdict | Functional | Visual | Compression | Constraint following | Notes |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-Coder-7B | Q5_K_M | 1 | ✓ ALL_COMPLETE | PASS | 9.0/10 | 0.0043 | ✓ single file | Baseline |
| Qwen2.5-Coder-3B | Q5_K_M | 1 | ALL_COMPLETE* | PASS* | 2.0/10 | 0.0040 | ✗ generates multi-file | Ignores single_html constraint |

*The 3B verdict is technically ALL_COMPLETE but the output is architecturally wrong. The game works because game.js loads, but the constraint was violated and the Designer loop failed to fix it (generated phantom files).

---

## Rendering approach by game type — Qwen2.5-Coder-7B

| Game | Rendering | Consistent? | Notes |
|---|---|---|---|
| Snake | DOM (div grid) | Yes (all runs) | Model preference |
| Pong | Canvas | Yes (1 run) | Correct: continuous ball trajectory |
| Tetris | DOM (div grid) | Yes | Consistent with Snake |
| Asteroid | Canvas | Yes | Consistent with Pong |

The 7B correctly infers rendering approach from game type. Games with continuous motion (Pong, Asteroid) → Canvas. Games with discrete grid state (Snake, Tetris) → DOM. This is implicit architectural knowledge in the model, not specified in any prompt.

---

## Compression analysis

| Prompt | Seed bytes | Artifact bytes | Ratio | Strategy | Notes |
|---|---|---|---|---|---|
| build a Pong game | 17 | 3026 | 0.0056 | Full scope | ✓ Best ratio for a complete game |
| build a Snake game | 18 | 4149 | 0.0043 | Full scope | ✓ Validated baseline |
| build a minimal Tetris (reduced) | 99 | 3059 | 0.0324 | Scope reduced | ✗ 7x worse — human fills what model can't |
| build a playable Tetris game | 28 | — | — | Full scope | ✗ Exceeds model capacity |

**Key insight**: the optimal compression ratio requires that the model can fully decompress the seed without scope reduction. When scope reduction is needed, the human must add information to the seed — which directly increases Kolmogorov complexity. The model's decompression capacity is the binding constraint on compression efficiency.

---

## Key findings (complete)

**Finding 1** — Multi-file is above repair loop capacity at 7B. Single-file eliminates cross-file Critic hallucination.

**Finding 2** — Token ceiling is the binding constraint for complex prompts. The 7B ceiling is ~900-1465 tokens per completion.

**Finding 3** — Coder output is deterministic given identical input. Variance traces to Designer pre-code call.

**Finding 4** — The 7B selects rendering approach from game semantics. Canvas for continuous motion, DOM for discrete grid state.

**Finding 5** — Compression baseline: Pong 0.0056, Snake 0.0043. Both complete and validated.

**Finding 6** — Asteroid is above 7B threshold regardless of sound inclusion. Core game logic volume is the constraint.

**Finding 7** — Scope reduction via enriched seed works but degrades compression ratio 7x (0.0043 → 0.0324). Human adds what model can't generate.

**Finding 8** — Token generation ceiling varies with input context size (911-1615 tokens observed).

**Finding 9** — Decompression threshold: ~4 fully implemented functions (Snake, Pong) succeeds. ~8 (Tetris, Asteroid) fails.

**Finding 10** — The 3B fails on constraint following, not code generation. It can write functional Snake but ignores single-file architectural constraints. Produces multi-file output with broken cross-references. The 7B respects architectural constraints; the 3B does not.

**Finding 11** — Executor has a false negative on minimal Tetris DOM structure. The `game_area_present` selector does not match all possible DOM game structures. Needs broadening.

---

## Bug history

| Date | Component | Bug | Fix | Status |
|---|---|---|---|---|
| 2026-04-26 | loop.py | Planner called with empty issues | `if not issues: break` | Fixed |
| 2026-04-26 | llm.py | HTTP timeout 600s | Raised to 900s → 1800s | Fixed |
| 2026-04-27 | planner.py | Same file duplicated in fix plan | `_deduplicate()` | Fixed |
| 2026-04-27 | coder.py | Deterministic fix loop at temp=0 | fix_history injected | Fixed |
| 2026-04-27 | executor.py | canvas_present false-negative on DOM | arcade_game_canvas/dom split | Fixed |
| 2026-04-29 | executor.py | game_area_present false-negative on non-standard DOM structures | Needs broadening — open | Open |
| 2026-04-29 | critic output parser | NEEDS_FIXES with 0 issues treated as ALL_COMPLETE | Guard works but masks 3B Critic malformed output | To investigate |
