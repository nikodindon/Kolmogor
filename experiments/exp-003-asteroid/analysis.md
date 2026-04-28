# exp-003-asteroid — Analysis

## Objective

Test whether a more complex prompt (Asteroid game with sounds) succeeds with the 7B model
in single_html mode. Intermediate complexity between Snake (trivial) and Tetris (too large).

## Runs

| Run | Model | Target | Cycles | Verdict | Functional | Visual | Notes |
|---|---|---|---|---|---|---|---|
| run-001 | Qwen7B Q5_K_M | single_html | 5 | STALL | N/A | N/A | Prompt too rich (sounds) |
| run-002 | Qwen7B Q5_K_M | single_html | TBD | TBD | TBD | TBD | Without sounds |

## Key observations

**Critic hallucination on complex prompts.** Cycles 1-2 produced five identical issues claiming five different functions all lack "collision logic". This is a copy-paste hallucination pattern: the Critic generates a plausible-sounding issue and applies it to every function it lists. Not a real analysis. The stall detector fires on the real issue at cycles 3-5: `moveBullet` not defined.

**Token ceiling is the binding constraint, not loop logic.** index.html stays at exactly 5393 chars through all cycles. The fix_history mechanism was designed to break deterministic loops — it changes the prompt context — but when the model is hitting its generation ceiling, a larger context does not help: it still produces the same truncated file. The issue is output budget, not input variety.

**"With sounds" is above the single_html budget for 7B.** Web Audio API adds ~400-600 chars of boilerplate per sound. On a file that already fills the token budget with game logic, there is no room for sounds. This is a clear example of prompt complexity exceeding model capacity: the seed contains more information than the model can decompress in one generation pass.

## What changes for run-002

Remove "with shot and explosion sounds" from the prompt. Test if the core Asteroid game
logic fits within the token budget without audio. If run-002 succeeds, the finding is:
sounds specifically push this prompt over the 7B single_html threshold.

## Updated after run-002

run-002 (without sounds) produces the same stall at cycle 4 with the same root cause.
The sounds were not the issue — the core Asteroid game logic (ship, asteroids, bullets,
collision detection, splitting) already exceeds the 7B single_html token budget.

**Revised finding:** Asteroid is above the 7B complexity threshold for single_html,
regardless of sound inclusion. The compression seed "build a classic Asteroid arcade game"
(36 bytes) encodes more information than the 7B model can decompress in ~1260 tokens.

Next test: run-003 with HTTP timeout raised to 1800s, to separate timeout from token ceiling.
If run-003 still stalls at 5260 chars, token ceiling is confirmed. If it progresses, timeout was the issue.
