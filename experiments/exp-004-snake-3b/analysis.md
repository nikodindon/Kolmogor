# exp-004-snake-3b — Analysis

## Objective

First model size comparison. Test Qwen2.5-Coder-3B Q5_K_M on the Snake baseline.
Hypothesis: the 3B can generate functional Snake but may struggle with constraints.

## Runs

| Run | Model | Cycles | Verdict | Functional | Visual | Notes |
|---|---|---|---|---|---|---|
| run-001 | Qwen2.5-3B Q5_K_M | 1 | ALL_COMPLETE* | PASS* | 2.0/10 | Constraint violation |

*Verdict is technically correct but output is architecturally wrong.

## Key findings

**The 3B fails on constraint following, not code generation.** The game logic is correct — executor passes 5/5 functional tests. But the 3B ignores the single_html constraint entirely and generates index.html + game.js (multi-file). This is a qualitative architectural difference from the 7B.

**The Critic is unreliable at 3B.** It produces a malformed response: `VERDICT: NEEDS_FIXES` with feature failures listed but no `Issues:` block. Our parser guards against empty issues (treats as ALL_COMPLETE), which is correct behavior but masks the underlying problem.

**The Designer loop fails at 3B.** 3 audit cycles, score drops from 3.0 to 2.0. The Designer identifies visual issues, the Planner generates phantom files (styles.css, header.html, footer.html, utils.js), the Coder generates minimal stubs, the Designer score doesn't improve. The 3B doesn't understand that it needs to consolidate everything into one file.

**ERR_FILE_NOT_FOUND in console** confirms broken references — the 3B generates calls to files it didn't create.

## What this means for the research

The 3B is not just a "smaller 7B". It has qualitatively different failure modes:
- 7B: follows constraints, fails on complexity (token ceiling)
- 3B: ignores constraints, generates functional code but wrong architecture

For the multi-agent architecture, the 3B may be viable as a Coder for small, bounded tasks with a very explicit spec — but it cannot serve as its own Architect or interpret high-level constraints. The role separation in the planned architecture becomes even more important at smaller model sizes.
