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

        Guarantees: one entry per file, no duplicates.
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

        plan = []
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                plan = parsed
        except json.JSONDecodeError:
            # Fallback: extract file + reason pairs from plain text
            for issue in issues:
                m = re.search(r"([\w./\-]+\.\w+)\s*[—\-–:]\s*(.+)", issue)
                if m:
                    plan.append({"file": m.group(1), "reason": m.group(2).strip()})

        return self._deduplicate(plan)

    def _deduplicate(self, plan: list[dict]) -> list[dict]:
        """
        Merge entries for the same file into one, concatenating reasons.
        Then cap at 3 files. This fixes the Planner doublon bug observed in run-005
        where game.js appeared twice causing two identical Coder fix calls.
        """
        merged: dict[str, list[str]] = {}
        for entry in plan:
            filename = entry.get("file", "").strip()
            reason = entry.get("reason", "").strip()
            if not filename:
                continue
            if filename not in merged:
                merged[filename] = []
            if reason and reason not in merged[filename]:
                merged[filename].append(reason)

        result = [
            {"file": f, "reason": " | ".join(reasons)}
            for f, reasons in merged.items()
        ]
        return result[:3]
