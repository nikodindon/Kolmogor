# Model Matrix

Comparison table updated after each experiment batch.
Columns: model, role tested, prompt type, cycles to completion, stall detected, functional pass, visual score, compression ratio, notes.

A dash means not yet tested. A question mark means tested but result inconclusive.

---

## Full pipeline (all roles, one model)

| Model | Quant | Prompt | Cycles | Stall | Functional | Visual | Compression | Notes |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-Coder-7B | Q4_K_M | Tetris | TBD | TBD | TBD | TBD | TBD | Baseline |
| Qwen2.5-Coder-7B | Q4_K_M | Snake | TBD | TBD | TBD | TBD | TBD | |
| Qwen2.5-Coder-7B | Q4_K_M | Todo app | TBD | TBD | TBD | TBD | TBD | |

---

## Role: Architect

Testing which models can produce a usable SPEC.md (complete, verifiable, role-annotated files).

| Model | Quant | Prompt | Spec quality (1-5) | Avg Coder cycles needed | Notes |
|---|---|---|---|---|---|
| Qwen2.5-Coder-1.5B | Q8 | Tetris | TBD | TBD | |
| Qwen2.5-Coder-3B | Q6_K | Tetris | TBD | TBD | |
| Qwen2.5-Coder-7B | Q4_K_M | Tetris | TBD | TBD | Reference |
| Mistral-7B | Q4_K_M | Tetris | TBD | TBD | Generalist comparison |

---

## Role: Coder

Testing which models can generate syntactically valid, complete files from a spec.

| Model | Quant | Task | Files correct / total | Syntax errors | Cross-file consistency | Notes |
|---|---|---|---|---|---|---|
| Qwen2.5-Coder-1.5B | Q8 | Tetris | TBD | TBD | TBD | |
| Qwen2.5-Coder-3B | Q6_K | Tetris | TBD | TBD | TBD | |
| Qwen2.5-Coder-7B | Q4_K_M | Tetris | TBD | TBD | TBD | Reference |

---

## Role: Critic

Testing which models can identify blocking issues without false positives or missed bugs.

| Model | Quant | Task | False positives | Missed bugs | Stall loops caused | Notes |
|---|---|---|---|---|---|---|
| Qwen2.5-Coder-3B | Q6_K | Tetris | TBD | TBD | TBD | |
| Qwen2.5-Coder-7B | Q4_K_M | Tetris | TBD | TBD | TBD | Reference |

---

## Role: Planner

Testing which models can parse Critic output and produce a valid JSON fix plan.

| Model | Quant | JSON parse success rate | Plan quality (1-5) | Notes |
|---|---|---|---|---|
| Qwen2.5-Coder-1.5B | Q8 | TBD | TBD | Smallest viable candidate |
| Qwen2.5-Coder-3B | Q6_K | TBD | TBD | |
| Qwen2.5-Coder-7B | Q4_K_M | TBD | TBD | Reference |

---

## Stall patterns catalogue

All detected stalls, indexed for cross-experiment analysis.

| Experiment | Run | Model | Role | Pattern | Diagnosis | Resolution |
|---|---|---|---|---|---|---|
| | | | | | | |

---

## Key findings

*Updated as experiments produce results.*

No findings yet. First entry will appear after exp-001.
