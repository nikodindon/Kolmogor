"""
kolmogor — entry point

Usage:
    python main.py "build a snake game"
    python main.py "build a snake game" --experiment exp-002 --max_cycles 8
    python main.py "build a snake game" --target html_js --no-play --debug
    python main.py "build a Tetris game" --mode project --target single_html --debug
    python main.py --list
    python main.py --play exp-001/run-001

--target forces the Meta-Architect stack decision.
--mode simple (default): single-pass Coder/Critic loop
--mode project: Decomposer + PM + TaskCoder + Reviewer loop
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from core.config import load_config
from core.session import Session
from core.loop import run_pipeline
from core.project_loop import run_project_pipeline


def list_experiments():
    exp_root = Path("experiments")
    if not exp_root.exists():
        print("No experiments yet.")
        return
    for exp in sorted(exp_root.iterdir()):
        if not exp.is_dir():
            continue
        runs = sorted((exp / "runs").iterdir()) if (exp / "runs").exists() else []
        print(f"\n{exp.name}  ({len(runs)} run(s))")
        for run in runs:
            result_file = run / "result.json"
            if result_file.exists():
                result = json.loads(result_file.read_text())
                verdict = result.get("verdict", "?")
                cycles = result.get("cycles", "?")
                model = result.get("model", "?")
                print(f"  {run.name}  verdict={verdict}  cycles={cycles}  model={model}")
            else:
                print(f"  {run.name}  (no result.json)")


def next_run_id(experiment_path: Path) -> str:
    runs_path = experiment_path / "runs"
    runs_path.mkdir(parents=True, exist_ok=True)
    existing = [d.name for d in runs_path.iterdir() if d.is_dir()]
    existing_numbers = []
    for name in existing:
        try:
            existing_numbers.append(int(name.replace("run-", "")))
        except ValueError:
            pass
    next_n = max(existing_numbers, default=0) + 1
    return f"run-{next_n:03d}"


def main():
    parser = argparse.ArgumentParser(description="kolmogor pipeline runner")
    parser.add_argument("prompt", nargs="?", help="Natural language prompt")
    parser.add_argument("--experiment", default=None, help="Experiment name (default: auto)")
    parser.add_argument("--max_cycles", type=int, default=6)
    parser.add_argument("--mode", default="simple", choices=["simple", "project"],
                        help="Pipeline mode: simple (default) or project (Decomposer+PM)")
    parser.add_argument("--target", default="auto",
                        choices=["auto", "html_js", "single_html", "python_pygame", "python_cli"],
                        help="Force stack target (default: auto, Meta-Architect decides)")
    parser.add_argument("--no-play", action="store_true", help="Generate but do not open in browser")
    parser.add_argument("--debug", action="store_true", help="Verbose logging")
    parser.add_argument("--list", action="store_true", help="List all experiments and runs")
    parser.add_argument("--play", default=None, help="Replay an existing run: exp-001/run-001")
    args = parser.parse_args()

    if args.list:
        list_experiments()
        return

    if args.play:
        parts = args.play.split("/")
        artifact_path = Path("experiments") / parts[0] / "runs" / parts[1] / "files"
        index = artifact_path / "index.html"
        if index.exists():
            import subprocess
            subprocess.Popen(["explorer.exe", str(index.resolve())])
        else:
            print(f"No index.html found at {artifact_path}")
        return

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    config = load_config()

    # Resolve experiment folder
    if args.experiment:
        exp_name = args.experiment
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exp_name = f"exp-{timestamp}"

    exp_path = Path("experiments") / exp_name
    run_id = next_run_id(exp_path)
    run_path = exp_path / "runs" / run_id

    print(f"\nkolmogor")
    print(f"  experiment : {exp_name}")
    print(f"  run        : {run_id}")
    print(f"  model      : {config.get('model', '?')}")
    print(f"  prompt     : {args.prompt[:80]}")
    print(f"  target     : {args.target}")
    print(f"  mode       : {args.mode}")
    print(f"  max_cycles : {args.max_cycles}")
    print()

    session = Session(
        prompt=args.prompt,
        run_path=run_path,
        config=config,
        debug=args.debug,
        forced_target=args.target if args.target != "auto" else None,
    )

    if args.mode == "project":
        result = run_project_pipeline(session, play=not args.no_play)
    else:
        result = run_pipeline(session, max_cycles=args.max_cycles, play=not args.no_play)

    # Summary
    print(f"\nRun complete.")
    print(f"  verdict   : {result.get('verdict')}")
    print(f"  mode      : {args.mode}")
    print(f"  cycles    : {result.get('cycles')}")
    print(f"  target    : {result.get('forced_target') or 'auto'}")
    print(f"  functional: {result.get('executor_pass')}")
    print(f"  visual    : {result.get('designer_score')}/10")
    if result.get("stall_detected"):
        print(f"  STALL     : {result.get('stall_pattern')}")
    print(f"\nFull results: {run_path / 'result.json'}")


if __name__ == "__main__":
    main()
