# exp-001-baseline — Analysis

## Objective

Establish a baseline with the reference model (Qwen2.5-Coder-7B Q5_K_M) on a canonical prompt (Tetris). Validate the full pipeline runs end to end before starting model comparison experiments.

## Runs

| Run | Model | Target | Cycles | Verdict | Functional | Visual | Stall | Notes |
|---|---|---|---|---|---|---|---|---|
| run-001 | Qwen7B Q5_K_M | auto → python_pygame | 5 | STALL | N/A | N/A | rotate_piece / drop_piece / clear_lines | First run, bug in Planner (empty issues) |
| run-002 | Qwen7B Q5_K_M | auto → python_pygame | 5 | STALL | N/A | N/A | Same pattern | snapshot_limit 1500, same result |
| run-003 | Qwen7B Q5_K_M | auto → python_pygame | 6 | ERROR | N/A | N/A | None (timeout before stall) | HTTP timeout at 600s, cycle 5 tetris.py 4583 chars |
| run-004 | Qwen7B Q5_K_M | forced html_js | TBD | TBD | TBD | TBD | TBD | |

## Key observations

**Meta-Architect always picks Pygame for a Tetris prompt.** Across 3 runs with temperature=0, the decision was deterministic and consistently wrong for this model. The model associates "game" with Pygame. The --target flag is the right fix for controlled experiments.

**Multi-file Pygame is above the 7B repair loop capacity.** The Coder can write correct Python code for each file individually, but cannot maintain cross-file consistency through fix cycles. The Critic verification is unreliable on multi-file snapshots: run-002's final tetris.py contains all required methods, but the Critic kept marking them as missing.

**The Coder self-consolidates toward a single file given enough cycles.** In run-003, tetris.py grew from 550 to 4583 chars across 6 cycles — the model was pulling logic from utils.py into tetris.py on its own. This suggests a single-file constraint in the Architect prompt would accelerate convergence.

**Critic hallucination on multi-file context is a real phenomenon.** The critic_log for run-002 shows the Critic marking rotate_piece as missing on cycles 3-5, but the method is present in the actual file. This is the most important finding of this experiment: the Critic's text-only review of a multi-file snapshot is not reliable enough to drive a repair loop.

## What changes for run-004

- `--target html_js` forces single-file HTML/JS canvas, bypasses Meta-Architect LLM call
- Bug fix: empty issues list no longer triggers Planner (loop.py)
- HTTP timeout raised to 900s (llm.py)
- Hypothesis: single-file HTML reduces cross-file verification burden on Critic → fewer false positives → faster convergence

## Longer-term questions this experiment opens

Should the Critic be given each file separately rather than a combined snapshot? A per-file Critic call would avoid the truncation and cross-file hallucination problem, at the cost of more LLM calls per cycle.

Is Pygame viable at all with this architecture, or should it be reserved for experiments with a larger context window model?
