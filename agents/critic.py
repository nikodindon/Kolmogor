"""
critic.py
"""

import re
from core.llm import LLMClient
from agents.prompts import CRITIC


class Critic:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def review(self, spec: str, snapshot: str) -> tuple[str, list[str], str]:
        """
        Returns (verdict, issues, raw_response).
        verdict: "ALL_COMPLETE" or "NEEDS_FIXES" or "STALL"
        issues: list of issue strings
        """
        user_message = f"SPEC:\n{spec}\n\nPROJECT FILES:\n{snapshot}"
        raw = self.llm.complete(
            system_prompt=CRITIC,
            user_message=user_message,
            label="critic",
        )

        verdict = "NEEDS_FIXES"
        if "VERDICT: ALL_COMPLETE" in raw:
            verdict = "ALL_COMPLETE"

        issues = []
        if verdict == "NEEDS_FIXES":
            # Extract numbered issues after "Issues:" block
            issues_section = re.search(r"Issues:(.*?)$", raw, re.DOTALL | re.IGNORECASE)
            if issues_section:
                raw_issues = issues_section.group(1).strip()
                for line in raw_issues.split("\n"):
                    line = line.strip()
                    if re.match(r"^\d+\.", line):
                        issues.append(line)

        return verdict, issues, raw
