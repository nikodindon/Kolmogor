"""
planner.py
"""

import json
import re
from core.llm import LLMClient
from agents.prompts import PLANNER


class Planner:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def plan(self, issues: list[str]) -> list[dict]:
        """
        Takes a list of issue strings, returns a list of fix dicts:
        [{"file": "...", "reason": "..."}, ...]
        """
        user_message = "Issues to fix:\n" + "\n".join(issues)
        raw = self.llm.complete(
            system_prompt=PLANNER,
            user_message=user_message,
            label="planner",
        )

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
            cleaned = "\n".join(lines[1:end])

        try:
            plan = json.loads(cleaned)
            if isinstance(plan, list):
                return plan[:3]  # cap at 3 per cycle
        except json.JSONDecodeError:
            pass

        # Fallback: try to extract file + reason pairs from plain text
        plan = []
        for issue in issues[:3]:
            m = re.search(r"([\w./\-]+\.\w+)\s*[—\-–:]\s*(.+)", issue)
            if m:
                plan.append({"file": m.group(1), "reason": m.group(2).strip()})
        return plan
