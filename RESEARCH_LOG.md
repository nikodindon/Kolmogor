# Research Log

Chronological record of every run. One entry per run, in order. Nothing is deleted or edited after the fact — corrections go in a new entry.

Format per entry:

- **Date**: when the run happened
- **Experiment**: link to the experiment folder
- **Run**: run number within the experiment
- **Model**: exact model and quantization
- **Target**: stack used (auto or forced)
- **Prompt**: the user prompt (short version, full text in experiment folder)
- **Result**: COMPLETE / STALL / ERROR
- **Cycles**: number of Critic/Coder iterations
- **Functional**: pass/fail on executor tests
- **Visual**: designer score out of 10, or N/A
- **Notes**: what was learned, what changes for next run

---

## Log

### 2026-04-26 — run-001 — exp-001-baseline

- **Model**: Qwen2.5-Coder-7B Q5_K_M
- **Target**: auto (Meta-Architect chose python_pygame)
- **Prompt**: build a playable Tetris game
- **Result**: STALL
- **Cycles**: 5
- **Functional**: N/A
- **Visual**: N/A
- **Notes**: First run ever. Meta-Architect chose python_pygame multi-file (main.py + tetris.py + utils.py). Coder generated method stubs referenced but not defined. Bug discovered: Critic cycle 1 returned 0 issues but Planner hallucinated a config.ini fix plan anyway — empty issues list must short-circuit the Planner. Stall detector fired correctly at cycle 3 pattern repetition.

---

### 2026-04-26 — run-002 — exp-001-baseline

- **Model**: Qwen2.5-Coder-7B Q5_K_M
- **Target**: auto (Meta-Architect chose python_pygame again)
- **Prompt**: build a playable Tetris game
- **Result**: STALL
- **Cycles**: 5
- **Functional**: N/A
- **Visual**: N/A
- **Notes**: snapshot_limit raised to 1500 from 800. Same stall pattern: rotate_piece, drop_piece, clear_lines referenced but not defined across 3+ cycles. Confirmed snapshot size was not the cause. The core issue is that Pygame multi-file exceeds repair capacity at 7B: the Coder cannot maintain cross-file consistency across tetris.py and utils.py over multiple fix cycles. The model converges toward a single large file naturally (tetris.py grew from 768 to 2341 chars) but not fast enough before the stall detector fires.

  Key finding: `cat files/tetris.py` after run-002 shows rotate_piece IS defined in the final output. This means the Critic was reporting missing methods that actually existed. The snapshot fed to the Critic was either truncated or the Critic hallucinated issues it could not verify from a multi-file text context. Multi-file Pygame is unreliable not because the Coder can't write the methods, but because the Critic can't verify them across files.

---

### 2026-04-26 — run-003 — exp-001-baseline

- **Model**: Qwen2.5-Coder-7B Q5_K_M
- **Target**: auto (Meta-Architect chose python_pygame again)
- **Prompt**: build a playable Tetris game
- **Result**: ERROR (HTTP timeout)
- **Cycles**: 6
- **Functional**: N/A
- **Visual**: N/A
- **Notes**: Ran 6 full cycles before timeout. At cycle 5, the Coder produced a 4583-char tetris.py (1232 completion tokens, 477s) — it had started consolidating all logic into one file, which is the right direction. Then the next fix call timed out at the 600s HTTP limit. Two fixes needed: raise HTTP timeout to 900s, and add --target flag to force html_js for comparative run-004.

  Critic log shows interesting progression: cycle 1-2 report missing methods, cycle 3-5 shift to reporting logic errors (rotation incorrect, game over wrong). This is qualitatively different from run-002 — the model is making progress but slowly. The multi-file architecture is the bottleneck, not the model's code generation ability per se.

---

## Planned runs

- **run-004**: same prompt, `--target html_js` forced. Hypothesis: single-file HTML/JS canvas Tetris will complete in 3-4 cycles as seen in prior local-intent-coder work.
- **run-005**: if run-004 succeeds, repeat with `--target python_pygame` but Architect prompt updated to enforce single-file constraint.
- **run-006**: same prompt, swap Coder to Qwen2.5-Coder-3B Q6_K, keep html_js target. Test minimum Coder model size.

---

## Stall index

| Date | Experiment | Run | Model | Stall pattern | Diagnosis |
|---|---|---|---|---|---|
| 2026-04-26 | exp-001-baseline | run-001 | Qwen7B Q5_K_M | rotate_piece / drop_piece / clear_lines referenced but not defined | Multi-file Pygame: Critic cannot verify cross-file consistency. Methods likely exist but Critic marks them missing from truncated snapshot. |
| 2026-04-26 | exp-001-baseline | run-002 | Qwen7B Q5_K_M | Same as run-001 | Confirmed: snapshot_limit not the cause. Root cause is multi-file architecture combined with Critic verification limitations. |

---

## Prompt evolution log

| Date | Agent | Change summary | Motivation | First run |
|---|---|---|---|---|
| 2026-04-27 | MetaArchitect | Added --target flag bypass (forced_target skips LLM entirely) | Enable controlled comparative experiments without LLM non-determinism in stack choice | run-004 |
| 2026-04-27 | loop.py | Empty issues list now short-circuits Planner | Bug fix: Critic returning NEEDS_FIXES with 0 issues caused Planner hallucination (config.ini phantom) | run-004 |

---

## Bug log

| Date | Component | Description | Fix | Status |
|---|---|---|---|---|
| 2026-04-26 | loop.py | Planner called when issues list empty, hallucinated fix targets | Added `if not issues: break` guard before Planner call | Fixed |
| 2026-04-26 | llm.py | HTTP timeout 600s too short for large fix cycles (~1232 tokens at 4.8 tok/s) | Raised to 900s | Fixed |

---

### 2026-04-27 — run-005 — exp-001-baseline

- **Model**: Qwen2.5-Coder-7B Q5_K_M
- **Target**: forced html_js (3 files: index.html + game.js + style.css)
- **Prompt**: build a playable Tetris game
- **Result**: STALL
- **Cycles**: 5
- **Functional**: N/A
- **Visual**: N/A
- **Notes**: First html_js run. Same stall pattern as Pygame but different root cause. game.js locked at exactly 3863 chars from cycle 2 onward — 1232 completion tokens, identical output every cycle. Temperature=0 determinism confirmed: same prompt + same file + same issue = strictly identical output. Two bugs surfaced: (1) Planner produced game.js twice in the fix plan (cycles 2-4), causing two identical Coder calls per cycle wasting ~500s each. (2) Coder fix loop has no mechanism to escape deterministic repetition. Multi-file HTML/JS stalls for the same reason as Pygame: the Critic keeps reporting functions as missing even though game.js grows to a reasonable size, suggesting Critic is hallucinating or the snapshot truncation hides the implementations.

  Key finding: the stall is architectural, not model-capability. The repair loop needs (a) deduplication in the Planner output and (b) fix history injection in the Coder to break the deterministic loop. Also: single_html target added — all code in one index.html file — to eliminate multi-file Critic verification issues entirely.

---

## Planned runs

- **run-006**: same prompt, `--target single_html`. All code in index.html. Hypothesis: eliminates Critic cross-file hallucination and Coder multi-file inconsistency in one move.
- **run-007**: if run-006 succeeds, same prompt `--target html_js` with fixes applied (Planner deduplication + Coder fix history). Tests if fixes are sufficient for multi-file.
- **run-008**: if run-006 succeeds, same prompt `--target single_html` with Qwen2.5-Coder-3B Q6_K. Test minimum Coder model size.

---

## Bug log

| Date | Component | Description | Fix | Status |
|---|---|---|---|---|
| 2026-04-26 | loop.py | Planner called when issues list empty, hallucinated fix targets | Added `if not issues: break` guard | Fixed |
| 2026-04-26 | llm.py | HTTP timeout 600s too short for large fix cycles | Raised to 900s | Fixed |
| 2026-04-27 | planner.py | Same file appeared twice in fix plan (game.js x2 in run-005) | Added `_deduplicate()` method merging same-file entries | Fixed |
| 2026-04-27 | coder.py/loop.py | Deterministic fix loop: temp=0 + same context = same output forever | Injected fix_history accumulator into Coder fix prompt | Fixed |
