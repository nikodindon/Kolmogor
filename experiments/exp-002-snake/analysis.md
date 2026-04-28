# exp-002-snake — Analysis

## Objective

Establish Snake as the pipeline validation benchmark and the simplest game baseline.
Minimal complexity: no rotation, no multi-piece state, single element per game object.

## Runs

| Run | Model | Target | Cycles | Verdict | Functional | Visual | Notes |
|---|---|---|---|---|---|---|---|
| run-001 | Qwen7B Q5_K_M | single_html | 1 | ALL_COMPLETE | null | 0.0 | No Playwright |
| run-002 | Qwen7B Q5_K_M | single_html | 1 | ALL_COMPLETE | false | 9.0/10 | Executor v1.0 false negative |
| run-003 | — | — | — | — | — | — | Skipped (run-002 already had Designer) |
| run-004 | Qwen7B Q5_K_M | single_html | 1 | ALL_COMPLETE | null | 0.0 | venv not active |
| run-005 | Qwen7B Q5_K_M | single_html | 1 | ALL_COMPLETE | false | 9.0/10 | executor.py not yet updated on disk |
| run-006 | Qwen7B Q5_K_M | single_html | 1 | ALL_COMPLETE | **PASS** | **9.0/10** | ✓ First fully clean run |

## Key findings

**The pipeline is validated end-to-end on Snake.** ALL_COMPLETE in 1 cycle, executor PASS (5/5 tests), Designer 9.0/10 VISUALLY_COMPLETE. Duration ~10 minutes total on Ryzen 5 5500U, CPU only.

**The 7B model chooses DOM rendering over Canvas.** Consistent across all 6 runs. The model generates absolute-positioned divs for snake segments and food, not a Canvas implementation. At temperature=0 this is deterministic — the model has a learned preference. This is a compression research observation: the rendering choice is implicit in the model, not in the seed.

**Coder output has two stable clusters despite temperature=0.** Runs 1 and 4 produce 3936 chars (911 tokens). Runs 2, 5, 6 produce 4149 chars (998 tokens). The difference traces to the Designer pre-code guidelines call which produces two different outputs non-deterministically. Caching guidelines within an experiment would collapse this to a single cluster.

**Architect is fully deterministic.** All runs produce identical spec (797 chars, 203 tokens). The Architect prompt + Snake prompt → always the same spec. This is the seed + model → stable decompression behavior we want to measure.

## Compression metrics (validated)

| Seed | Seed bytes | Artifact bytes | Ratio |
|---|---|---|---|
| "build a Snake game" | 18 | 4149 | **0.0043** |

First validated Kolmogorov compression data point for this project.

## What this experiment established

Snake defines the lower bound of prompt complexity that reliably succeeds with Qwen7B Q5_K_M in single_html mode. Any simpler prompt would likely also succeed in 1 cycle. The next question is the upper bound — where does complexity cause failure?

Planned next steps:
- exp-003-asteroid run-002: Asteroid without sounds (intermediate complexity)
- exp-001-baseline run-007: Tetris with max_out_tokens=12000 (upper complexity test)
- exp-004: Snake with Qwen2.5-Coder-3B (minimum viable model size)
