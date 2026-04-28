# Model Matrix

Comparison table updated after each experiment batch.
A dash means not yet tested. A question mark means tested but result inconclusive.

---

## Full pipeline results — single_html target

| Model | Quant | Prompt | Cycles | Stall | Functional | Visual | Compression | Duration | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Qwen2.5-Coder-7B | Q5_K_M | Snake | 1 | No | ✓ PASS | 9.0/10 | 0.0043 | ~10 min | **Baseline.** DOM rendering. First-shot success. |
| Qwen2.5-Coder-7B | Q5_K_M | Asteroid (no sounds) | TBD | TBD | TBD | TBD | TBD | TBD | |
| Qwen2.5-Coder-7B | Q5_K_M | Tetris | TBD | TBD | TBD | TBD | TBD | TBD | max_out_tokens=12000 |
| Qwen2.5-Coder-3B | Q6_K | Snake | — | — | — | — | — | — | Planned exp-004 |
| Qwen2.5-Coder-1.5B | Q8 | Snake | — | — | — | — | — | — | Planned |

---

## Role: Architect — spec quality by model

| Model | Quant | Prompt | Spec chars | Spec tokens | Deterministic? | Notes |
|---|---|---|---|---|---|---|
| Qwen2.5-Coder-7B | Q5_K_M | Snake | 797 | 203 | Yes (identical across all runs) | Clean, well-structured |
| Qwen2.5-Coder-7B | Q5_K_M | Tetris | ~925-1185 | ~276-291 | Yes per run, slight variance across runs | |
| Qwen2.5-Coder-7B | Q5_K_M | Asteroid | 1079 | 270 | TBD | |

---

## Role: Coder — output variance at temperature=0

| Model | Quant | Prompt | Run | Tokens | Chars | Notes |
|---|---|---|---|---|---|---|
| Qwen2.5-Coder-7B | Q5_K_M | Snake | run-001 | 911 | 3936 | Designer guidelines variant A |
| Qwen2.5-Coder-7B | Q5_K_M | Snake | run-002 | 998 | 4149 | Designer guidelines variant B |
| Qwen2.5-Coder-7B | Q5_K_M | Snake | run-004 | 911 | 3936 | Same as run-001 (Designer variant A) |
| Qwen2.5-Coder-7B | Q5_K_M | Snake | run-005/006 | 998 | 4149 | Same as run-002 (Designer variant B) |

Observation: Coder output is deterministic given identical input. Variance between runs comes
from Designer pre-code guidelines (not fully deterministic). Two stable clusters observed:
911 tokens / 3936 chars and 998 tokens / 4149 chars. To investigate: cache Designer guidelines.

---

## Compression metrics

| Experiment | Prompt | Seed bytes | Artifact bytes | Ratio | Status |
|---|---|---|---|---|---|
| exp-002-snake | build a Snake game | 18 | 4149 | 0.0043 | ✓ Validated |
| exp-001-baseline | build a playable Tetris game | 28 | TBD | TBD | Pending |
| exp-003-asteroid | build a classic Asteroid arcade game | TBD | TBD | TBD | Pending |

---

## Stall patterns catalogue

| Experiment | Run | Model | Pattern | Root cause | Resolution |
|---|---|---|---|---|---|
| exp-001-baseline | run-001/002 | Qwen7B | rotate_piece / drop_piece / clear_lines undefined | Multi-file Pygame: Critic hallucinates missing methods that exist in file | Switch to single_html |
| exp-001-baseline | run-005/006 | Qwen7B | update / drawTetrimino undefined (multi-file HTML) | Same root cause, different target | Switch to single_html |
| exp-001-baseline | run-006 | Qwen7B | Timeout (no stall pattern) | index.html hits token ceiling at ~1465 tokens | Raise max_out_tokens to 12000 |
| exp-003-asteroid | run-001 | Qwen7B | moveBullet undefined | Token ceiling — Web Audio API fills budget before game logic | Remove sounds from prompt |

---

## Bug history (pipeline)

| Date | Component | Bug | Fix | First clean run |
|---|---|---|---|---|
| 2026-04-26 | loop.py | Planner called with empty issues list | `if not issues: break` | run-005 exp-001 |
| 2026-04-26 | llm.py | HTTP timeout 600s | Raised to 900s | run-004 exp-001 |
| 2026-04-27 | planner.py | Same file duplicated in fix plan | `_deduplicate()` | run-005 exp-001 |
| 2026-04-27 | coder.py | Deterministic fix loop at temp=0 | fix_history injected | run-005 exp-001 |
| 2026-04-27 | executor.py | `canvas_present` false-negative on DOM games | Split arcade_game → canvas/dom subtypes | run-006 exp-002 ✓ |

---

## Key findings so far

**Finding 1 — Multi-file is above repair loop capacity at 7B.** Whether Pygame or HTML/JS, splitting a game across 3+ files causes the Critic to hallucinate cross-file dependency errors that the Coder cannot resolve. The Critic's text-only snapshot verification is unreliable across file boundaries. Single-file artifacts avoid this entirely.

**Finding 2 — Token ceiling is the binding constraint for complex prompts.** The 7B model generates ~1200-1465 completion tokens maximum for a fix call before truncating. Simple games (Snake: 911-998 tokens) fit comfortably. Complex games (Tetris, Asteroid with sounds) hit the ceiling. Raising max_out_tokens to 12000 in config allows llama-server to generate more — whether the model actually uses the budget is the next test.

**Finding 3 — Coder output is deterministic given identical input.** Two stable output clusters observed for Snake across 6 runs. The variance comes entirely from the Designer pre-code guidelines call. Caching guidelines within an experiment would make all runs fully reproducible.

**Finding 4 — The 7B model prefers DOM over Canvas for arcade games.** All Snake runs produce div-based rendering. Whether this holds for Tetris and Asteroid is an open question.

**Finding 5 — Compression ratio baseline: 0.0043 for Snake.** 18 bytes → 4149 bytes. This is the first validated data point for the Kolmogorov compression research axis.

---

## Updated findings — 2026-04-28

**Finding 6 — Asteroid is above the 7B single_html threshold.** Both runs (with and without
sounds) produce identical stalls at 5260 chars. The game logic volume alone exceeds the
~1260 token output budget. Sounds were not a factor.

**Finding 7 — HTTP timeout was masking progress on Tetris.** run-007 shows the file growing
from 5381 to 6088 chars (13% growth) between fix cycles — genuine iterative improvement.
The timeout at 900s cut it short. With 1800s timeout, Tetris may complete.

**Finding 8 — Token ceiling varies by fix cycle context size.** Generation ceiling:
- Initial generation: ~1465 tokens (clean context)
- Fix cycle with history: ~1258-1615 tokens (larger input context = different ceiling)
The model doesn't have a fixed ceiling — it depends on the prompt token count.
