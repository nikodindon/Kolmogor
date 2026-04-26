# kolmogor

*What is the shortest description a small local language model needs to reconstruct a working software artifact?*

This is a personal research project. It runs slowly, on modest hardware, with CPU-only inference. Every run is documented. Every failure is kept. Nothing is cleaned up to look better than it is.

---

## The question

In algorithmic information theory, the Kolmogorov complexity of a string is the length of the shortest program that produces it. It is the theoretical minimum description of any piece of data. For most human-authored programs, that minimum is far shorter than the source code itself: a Tetris clone, a sorting algorithm, a todo app all encode structured, intentional patterns that a sufficiently informed observer could reconstruct from a much shorter cue.

Large language models, trained on the entire corpus of human-written code, are a strange kind of learned decompressor. Feed them a terse description. They expand it into a full implementation. The description is the compressed form. The output is the decompressed form.

This project asks: how short can the description get, for a specific model at a specific size, before reconstruction fails? Where exactly does a 1.5B model break that a 3B does not? Is the Architect role harder than the Coder role for a generalist model? Does a code-specialized model outperform a general-instruction model when the task is pure code generation?

These are not theoretical questions. They are empirical ones. This project measures them.

---

## The setup

Everything here runs on a laptop, CPU only, no cloud, no API fees.

| Machine | CPU | RAM | GPU | Inference |
|---|---|---|---|---|
| Asus VivoBook 15 | Ryzen 5 5500U | 20 GB | None | CPU only, llama.cpp |

Development environment: WSL2 on Windows 11. All models are GGUF quantized, served via llama-server. The choice of CPU-only is deliberate: sequential floating-point operations on a fixed CPU architecture are fully deterministic across runs, which matters a great deal for a project that relies on reproducible measurements.

The model family tested is Qwen2.5-Coder, from 1.5B to 7B, with occasional comparisons against generalist models at equivalent sizes.

---

## The pipeline

A user writes a plain natural language prompt. A chain of specialized agents handles everything from there.

```
Plain prompt
    |
    v
Meta-Architect      decides: language, stack, file structure
    |
    v
Architect           produces a structured spec (SPEC.md)
    |
    v
Coder               generates each file completely, no stubs
    |
    v
    +---> Critic    reviews the full project, lists blocking issues
    |         |
    |         v
    |     Planner   converts issues into a minimal fix plan
    |         |
    +<---------+    loop until ALL_COMPLETE or stall detected
    |
    v
Executor            opens the artifact in a headless browser (Playwright)
                    runs type-specific functional tests
    |
    v
Designer            audits visual quality against pre-set guidelines
                    scores 1 to 10, triggers CSS fix cycles if needed
    |
    v
Runnable artifact + functional hash (SHA256 of execution output, not source)
```

The Meta-Architect is the layer that makes the pipeline truly general. It receives a raw prompt like "build me a snake game" or "make a CLI tool that monitors a folder for changes" and decides autonomously what language, what file structure, and what constraints to pass to the Architect. The user never specifies a stack.

---

## Stall detection

One of the central engineering challenges is knowing when to stop. A small model in a repair loop can get stuck: the Critic identifies an issue, the Coder produces a fix, the Critic identifies the exact same issue again. This can repeat indefinitely without any progress.

The stall detector monitors the history of Critic outputs across cycles. It identifies when the same error category recurs without resolution, and halts the run cleanly with a structured report. That report includes the pattern detected, the number of blocked cycles, and a diagnostic hint pointing toward likely causes: a prompt that is too vague, a model that is too small for this role, or a structural problem in the generated spec.

When a stall is detected, the run stops. A human reads the report, decides what to change, and opens a new run with updated parameters.

---

## What gets measured

Each run produces a `result.json` with the following fields:

- `model`: the exact model identifier and quantization
- `prompt`: the original user input
- `cycles`: number of Critic/Coder iterations
- `stall_detected`: boolean, with pattern description if true
- `executor_pass`: boolean, functional test results
- `designer_score`: visual quality score out of 10
- `seed_bytes`: size of the compressed prompt seed
- `artifact_bytes`: total size of generated files
- `compression_ratio`: seed_bytes / artifact_bytes
- `functional_hash`: SHA256 of execution output

Over time these results fill a comparison matrix across models and roles. That matrix is the actual research output.

---

## Repository structure

```
kolmogor/
|
├── README.md                       this file
├── RESEARCH_LOG.md                 chronological log of every run
|
├── config/
│   ├── models.json                 catalogue of tested models (size, quant, port, notes)
│   └── config.json                 active config (llama.cpp endpoint, model, params)
|
├── experiments/                    one folder per named experiment
│   └── exp-001-baseline/
│       ├── prompt.txt              the user prompt for this experiment
│       ├── config_snapshot.json    exact config at run time (frozen)
│       ├── runs/
│       │   ├── run-001/
│       │   │   ├── spec.md         generated spec
│       │   │   ├── files/          generated artifact files
│       │   │   ├── critic_log.jsonl  one JSON line per Critic cycle
│       │   │   └── result.json     full metrics for this run
│       │   └── run-002/
│       └── analysis.md             human analysis of this experiment
|
├── agents/
│   ├── meta_architect.py           decides stack and language from a raw prompt
│   ├── architect.py                prompt to structured SPEC.md
│   ├── coder.py                    spec to complete files, no stubs
│   ├── critic.py                   reviews full project, lists blocking issues only
│   ├── planner.py                  converts critic output to minimal fix plan
│   ├── designer.py                 visual guidelines + post-render style audit
│   └── prompts.py                  all system prompts, the primary tuning surface
|
├── core/
│   ├── llm.py                      HTTP client for llama-server (OpenAI-compat)
│   ├── loop.py                     orchestrates all pipeline phases
│   ├── stall_detector.py           detects stuck repair loops, produces StallReport
│   ├── session.py                  session state, project snapshot, metrics
│   ├── hasher.py                   functional hashing (hash execution output)
│   └── executor.py                 Playwright browser test runner
|
├── storage/
│   └── dns_layer.py                optional: store seeds in Cloudflare DNS TXT records
|
├── results/
│   └── model_matrix.md             comparison table: models x roles x metrics
|
├── main.py                         entry point
├── validate.py                     post-generation validation script
├── config.example.json             example config, safe to commit
├── requirements.txt
└── .gitignore
```

---

## Experiment log summary

A full chronological log lives in `RESEARCH_LOG.md`. This table is a high-level summary updated after each experiment batch.

| Experiment | Model | Role tested | Prompt | Cycles | Stall | Functional | Visual | Notes |
|---|---|---|---|---|---|---|---|---|
| exp-001 | TBD | Full pipeline | TBD | TBD | TBD | TBD | TBD | Baseline run |

---

## The model catalogue

Models are tested in order of increasing size. The goal is to find the minimum viable size for each role, not to demonstrate that bigger is better.

| Model | Size | Quant | Role candidates | Status |
|---|---|---|---|---|
| Qwen2.5-Coder-1.5B-Instruct | 1.5B | Q8 | Planner only | To test |
| Qwen2.5-Coder-3B-Instruct | 3B | Q6_K | Coder, Critic | To test |
| Qwen2.5-Coder-7B-Instruct | 7B | Q4_K_M | Full pipeline | Tested in prior projects |
| Mistral-7B-Instruct | 7B | Q4_K_M | Architect, Meta-Architect | To test |
| Llama3-8B-Instruct | 8B | Q4_K_M | Architect, Critic | To test |

The hypothesis driving the ordering: the Planner needs the least capability (bounded JSON output from a structured input), the Coder needs code specialization more than raw size, the Architect needs reasoning and structure over code fluency, and the Meta-Architect needs the broadest generalization of all.

---

## Prior work

This project is the consolidation of four earlier experiments, listed in order:

**[mnemo](https://github.com/nikodindon/mnemo)** established the theoretical framing: DNS as a generative filesystem, LLM as a learned decompressor, temperature=0 determinism, functional hashing as the cross-machine solution. The question was born here.

**[local-agent-tetris](https://github.com/nikodindon/local-agent-tetris)** was the first practical test: can a local agent on modest hardware build a concrete multi-file project from a single prompt? It documented real hardware benchmarks, the failure of generic tool harnesses with small models, and the necessity of a minimal custom agent loop.

**[nova-game-engine](https://github.com/nikodindon/nova-game-engine)** generalized the agent to a Pygame/Python target and introduced cleaner session management and structured debug logging.

**[local-intent-coder](https://github.com/nikodindon/local-intent-coder)** brought the pipeline closest to its final form: five phases, Playwright execution testing, visual design audit, and the first concrete measurement of the full loop. Tic-Tac-Toe reached 10/10 visual quality in two cycles on CPU-only hardware.

Kolmogor is where those threads converge into a single structured research platform.

---

## What this is not

This is not a product. It does not compete with Cursor, Copilot, or any cloud coding assistant. It runs at 4 tokens per second on a laptop with no GPU.

It is not trying to prove that local models are as good as large cloud models. They are not, and that gap is part of what makes the research interesting.

It is a slow, careful, personal investigation into a question that information theory poses in the abstract and that this project makes concrete and measurable.

---

## Following along

The research log is the living document. Each run gets an entry. Each stall gets an analysis. Each prompt change gets a justification. If you are reading this and find it interesting, the log is the place to start.

Feedback, results from other hardware, and prompt ideas are welcome once the project is stable enough to open up. For now it is a one-person experiment in progress.

---

## License

MIT
