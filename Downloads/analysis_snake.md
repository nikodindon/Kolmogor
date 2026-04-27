# exp-002-snake — Analysis

## Objective

First successful experiment. Establish Snake as the baseline "simple game" benchmark:
minimal complexity, no rotation, no multi-piece state, single DOM element per game object.
Used to validate that the pipeline works end-to-end before tackling more complex prompts.

## Runs

| Run | Model | Target | Cycles | Verdict | Functional | Visual | Notes |
|---|---|---|---|---|---|---|---|
| run-001 | Qwen7B Q5_K_M | single_html | 1 | ALL_COMPLETE | null (no Playwright) | 0.0 (no Playwright) | First ALL_COMPLETE |
| run-002 | Qwen7B Q5_K_M | single_html | 1 | ALL_COMPLETE | false (executor bug) | 9.0/10 | False negative on executor |
| run-003 | Qwen7B Q5_K_M | single_html | 1 | TBD | TBD | TBD | Clean run with fixed executor |

## Key observations

**Snake is at or near the lower bound of model capability for this pipeline.** 1 cycle, ALL_COMPLETE, no stall, no fixes needed. The model knows Snake well enough to generate a complete, functional implementation in one shot from a spec.

**The model chooses DOM over Canvas consistently.** Both run-001 and run-002 produce div-based rendering (absolute-positioned divs for snake body and food), not a Canvas implementation. At temperature=0 this is deterministic — the model has a preference. This is a finding for the compression research: the model's default implementation choice is part of the decompressed output, not part of the seed.

**Designer works well on simple artifacts.** 9/10 in one audit cycle on run-002. First validated Designer result.

**Slight Coder output variance between runs despite temperature=0.** Run-001: 3936 chars, run-002: 4149 chars. Both Architect outputs are identical (797 chars). The variance comes from the Designer pre-code guidelines which differ slightly between runs — the Designer call is not fully deterministic. The guidelines propagate into the Coder prompt and shift the output. To investigate: cache Designer guidelines per experiment, or force temperature=0 explicitly in that call.

## Compression metrics

| Run | Seed bytes | Artifact bytes | Ratio |
|---|---|---|---|
| run-001 | 18 | 3936 | 0.0046 |
| run-002 | 18 | 4149 | 0.0043 |

18 bytes ("build a Snake game") expands to ~4000 bytes of functional HTML. Ratio ~0.0044.

## What changes for next experiments

- run-003: clean run with fixed executor, expect first fully green result
- exp-004: same Snake prompt with Qwen2.5-Coder-3B to find minimum viable Coder size
