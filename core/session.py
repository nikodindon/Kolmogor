"""
session.py

Manages a single run: folder structure, file writes, metrics accumulation,
critic log, and the final result.json.
"""

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class RunMetrics:
    model: str = ""
    prompt: str = ""
    experiment: str = ""
    run_id: str = ""
    started_at: str = ""
    finished_at: str = ""
    cycles: int = 0
    verdict: str = ""
    stall_detected: bool = False
    stall_pattern: str = ""
    stall_diagnosis: str = ""
    executor_pass: Optional[bool] = None
    executor_details: dict = field(default_factory=dict)
    designer_score: Optional[float] = None
    designer_cycles: int = 0
    seed_bytes: int = 0
    artifact_bytes: int = 0
    compression_ratio: Optional[float] = None
    functional_hash: str = ""
    error: str = ""


class Session:
    def __init__(self, prompt: str, run_path: Path, config: dict, debug: bool = False):
        self.prompt = prompt
        self.run_path = run_path
        self.config = config
        self.debug = debug

        self.files_path = run_path / "files"
        self.files_path.mkdir(parents=True, exist_ok=True)

        self.critic_log_path = run_path / "critic_log.jsonl"

        self.metrics = RunMetrics(
            model=config.get("model", ""),
            prompt=prompt,
            run_id=run_path.name,
            experiment=run_path.parent.parent.name,
            started_at=datetime.now().isoformat(),
        )

        # In-memory project state
        self.spec: str = ""
        self.generated_files: dict[str, str] = {}  # filename -> content

    # --- File management ---

    def write_file(self, filename: str, content: str):
        """Write a generated file to the run folder and track it."""
        filepath = self.files_path / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        self.generated_files[filename] = content
        if self.debug:
            print(f"  [session] wrote {filename} ({len(content)} chars)")

    def write_spec(self, spec: str):
        self.spec = spec
        (self.run_path / "spec.md").write_text(spec, encoding="utf-8")

    def get_project_snapshot(self, token_limit: int = 800) -> str:
        """
        Returns a truncated snapshot of all generated files, for use as
        context in Critic and Coder prompts.
        """
        parts = [f"## SPEC\n{self.spec}\n"]
        for filename, content in self.generated_files.items():
            parts.append(f"## FILE: {filename}\n```\n{content}\n```\n")
        full = "\n".join(parts)

        # Rough token estimate: 1 token ~ 4 chars
        char_limit = token_limit * 4
        if len(full) > char_limit:
            full = full[:char_limit] + "\n...[snapshot truncated]"
        return full

    # --- Critic log ---

    def log_critic_cycle(self, cycle: int, verdict: str, issues: list[str], raw_response: str):
        entry = {
            "ts": datetime.now().isoformat(),
            "cycle": cycle,
            "verdict": verdict,
            "issues": issues,
            "raw_response": raw_response[:2000],  # cap for log size
        }
        with open(self.critic_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    # --- Artifact size measurement ---

    def measure_artifact(self):
        total = 0
        for f in self.files_path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        self.metrics.artifact_bytes = total

        seed_size = len(self.prompt.encode("utf-8"))
        self.metrics.seed_bytes = seed_size

        if total > 0:
            self.metrics.compression_ratio = round(seed_size / total, 4)

    # --- Final result ---

    def finish(self, verdict: str, error: str = ""):
        self.metrics.verdict = verdict
        self.metrics.error = error
        self.metrics.finished_at = datetime.now().isoformat()
        self.measure_artifact()
        self._write_result()

    def _write_result(self):
        result_path = self.run_path / "result.json"
        result_path.write_text(
            json.dumps(asdict(self.metrics), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if self.debug:
            print(f"  [session] result written to {result_path}")
