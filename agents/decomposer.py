"""
decomposer.py

Receives SPEC.md and breaks it into atomic implementation tasks ordered by dependency.
Each task is small enough to fit in a single Coder pass (~600 tokens max).

This is the key agent that enables complex projects with small models:
instead of asking the Coder to implement everything at once (which causes truncation
and token ceiling failures), the Decomposer creates a step-by-step plan where each
step is within the model's effective generation budget.

Finding from exp-001-baseline: Tetris fails because it needs ~8 functions
implemented simultaneously. A Decomposer would split this into 8 tasks of ~1 function
each, all within budget.
"""

import json
from core.llm import LLMClient
from agents.prompts import DECOMPOSER


class Task:
    """Single atomic implementation task."""

    def __init__(self, data: dict):
        self.id: str = data.get("id", "task-???")
        self.title: str = data.get("title", "")
        self.description: str = data.get("description", "")
        self.file: str = data.get("file", "index.html")
        self.depends_on: list[str] = data.get("depends_on", [])
        self.done_when: str = data.get("done_when", "")
        self.estimated_tokens: int = data.get("estimated_tokens", 400)
        self.status: str = "PENDING"  # PENDING | IN_PROGRESS | DONE | FAILED
        self.retry_count: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "file": self.file,
            "depends_on": self.depends_on,
            "done_when": self.done_when,
            "estimated_tokens": self.estimated_tokens,
            "status": self.status,
            "retry_count": self.retry_count,
        }

    def __repr__(self):
        return f"Task({self.id}, {self.status}, '{self.title[:40]}')"


class TaskPlan:
    """Ordered list of tasks produced by the Decomposer."""

    def __init__(self, tasks: list[Task]):
        self.tasks = tasks
        self._index = {t.id: t for t in tasks}

    def get(self, task_id: str) -> Task | None:
        return self._index.get(task_id)

    def next_pending(self) -> Task | None:
        """Return the first PENDING task whose dependencies are all DONE."""
        for task in self.tasks:
            if task.status != "PENDING":
                continue
            deps_done = all(
                self._index.get(dep, Task({"id": dep, "status": "DONE"})).status == "DONE"
                for dep in task.depends_on
            )
            if deps_done:
                return task
        return None

    def all_done(self) -> bool:
        return all(t.status == "DONE" for t in self.tasks)

    def summary(self) -> str:
        lines = []
        for t in self.tasks:
            icon = {"PENDING": "○", "IN_PROGRESS": "◎", "DONE": "✓", "FAILED": "✗"}.get(t.status, "?")
            lines.append(f"  {icon} {t.id} — {t.title} ({t.estimated_tokens} tokens est.)")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        lines = ["# Task Plan\n"]
        for t in self.tasks:
            lines.append(f"## {t.id}: {t.title}")
            lines.append(f"- **File**: `{t.file}`")
            lines.append(f"- **Status**: {t.status}")
            lines.append(f"- **Depends on**: {', '.join(t.depends_on) or 'none'}")
            lines.append(f"- **Estimated tokens**: {t.estimated_tokens}")
            lines.append(f"- **Done when**: {t.done_when}")
            lines.append(f"\n{t.description}\n")
        return "\n".join(lines)


class Decomposer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def decompose(self, spec: str, stack_decision: dict, design=None) -> TaskPlan:
        """
        Takes a SPEC.md, stack decision, and optional TechnicalDesign from the Analyst.
        Returns an ordered TaskPlan.
        """
        target = stack_decision.get("target", "single_html")
        constraints = stack_decision.get("constraints", [])

        design_context = ""
        if design is not None:
            design_context = f"\nTECHNICAL DESIGN FROM ANALYST:\n{design.to_context_string()}\n"

        user_message = (
            f"TARGET: {target}\n"
            f"CONSTRAINTS: {', '.join(constraints)}\n"
            f"{design_context}\n"
            f"SPEC:\n{spec}"
        )

        raw = self.llm.complete(
            system_prompt=DECOMPOSER,
            user_message=user_message,
            label="decomposer",
        )

        tasks = self._parse(raw)
        return TaskPlan(tasks)

    def _parse(self, raw: str) -> list[Task]:
        cleaned = raw.strip()

        # Strip markdown fences
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
            cleaned = "\n".join(lines[1:end])

        try:
            data = json.loads(cleaned)
            if isinstance(data, list):
                return [Task(t) for t in data[:10]]
        except json.JSONDecodeError as e:
            print(f"  [decomposer] JSON parse error: {e}")
            print(f"  [decomposer] raw output: {cleaned[:200]}")

        # Fallback: return a single catch-all task so the pipeline doesn't crash
        return [Task({
            "id": "task-001",
            "title": "full implementation (decomposer parse failed)",
            "description": "Implement the full project as specified.",
            "file": "index.html",
            "depends_on": [],
            "done_when": "project runs without errors",
            "estimated_tokens": 1000,
        })]
