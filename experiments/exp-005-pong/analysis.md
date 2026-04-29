# exp-005-pong — Analysis

## Objective

Map the complexity threshold between Snake (succeeds) and Tetris (fails).
Pong is simpler than Tetris but has continuous motion physics — tests Canvas rendering.

## Runs

| Run | Model | Cycles | Verdict | Functional | Visual | Compression |
|---|---|---|---|---|---|---|
| run-001 | Qwen7B Q5_K_M | 1 | ✓ ALL_COMPLETE | PASS | 8.0/10 | 0.0056 |

## Key findings

Pong succeeds cleanly in 1 cycle. The model correctly chose Canvas over DOM — the first Canvas success observed. This confirms that rendering choice is implicit in the model's architectural knowledge, not prompted.

0.0056 compression ratio is better than Snake (0.0043). Pong is conceptually denser: same seed size, smaller artifact, more game logic per byte. This is a strong data point for the compression research: Pong is a more efficiently compressible concept than Snake for this model.

8.0/10 visual score — just above the 7 threshold. The Designer fired but did not trigger a fix cycle (threshold is 7, not 8). To get 10/10, a second visual cycle would likely be needed.
