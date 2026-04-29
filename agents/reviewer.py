"""
reviewer.py

Reviews a single task implementation, not the whole project.
This is the key difference from the Critic: bounded scope = fewer false positives.

The Critic (mode simple) reviews all files against the full spec.
The Reviewer (mode project) reviews one task against its done_when condition.

Finding from experiments: the Critic hallucinates on large multi-function files
because it cannot hold the full context. The Reviewer operates on a single
task's code change, making verification tractable.
"""

import re
from core.llm import LLMClient
from agents.prompts import REVIEWER
from agents.decomposer import Task


class ReviewResult:
    def __init__(self, task_id: str, status: str, issues: list[str], raw: str):
        self.task_id = task_id
        self.status = status       # "DONE" or "NEEDS_FIXES"
        self.issues = issues
        self.raw = raw

    def is_done(self) -> bool:
        return self.status == "DONE"

    def __repr__(self):
        return f"ReviewResult({self.task_id}, {self.status}, {len(self.issues)} issues)"


class Reviewer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def review(self, task: Task, file_content: str) -> ReviewResult:
        """
        Review a single task against its done_when condition.
        """
        user_message = (
            f"TASK ID: {task.id}\n"
            f"TASK TITLE: {task.title}\n"
            f"DONE WHEN: {task.done_when}\n\n"
            f"TASK DESCRIPTION:\n{task.description}\n\n"
            f"CURRENT FILE CONTENT ({task.file}):\n"
            f"```\n{file_content}\n```"
        )

        raw = self.llm.complete(
            system_prompt=REVIEWER,
            user_message=user_message,
            label=f"reviewer:{task.id}",
        )

        return self._parse(task.id, raw)

    def _parse(self, task_id: str, raw: str) -> ReviewResult:
        status = "NEEDS_FIXES"
        if "STATUS: DONE" in raw:
            status = "DONE"

        issues = []
        if status == "NEEDS_FIXES":
            issues_section = re.search(r"Issues:(.*?)$", raw, re.DOTALL | re.IGNORECASE)
            if issues_section:
                for line in issues_section.group(1).strip().split("\n"):
                    line = line.strip()
                    if re.match(r"^\d+\.", line):
                        issues.append(line)

        return ReviewResult(task_id=task_id, status=status, issues=issues, raw=raw)
