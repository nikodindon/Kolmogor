"""
spec_reviewer.py

Validates that the spec + technical design together are complete and consistent.
Part of the conception phase — runs before the Decomposer.

Checks:
- Every spec feature has an implementation path in the analysis
- Every state variable is written to by at least one algorithm
- Every algorithm reads initialized variables
- The render strategy covers all visual state changes

This prevents features from reaching development without a defined mechanism,
which was the root cause of the line-clearing bug in exp-006 run-005.
"""

import re
from core.llm import LLMClient
from agents.prompts import SPEC_REVIEWER
from agents.analyst import TechnicalDesign


class SpecReviewResult:
    def __init__(self, verdict: str, issues: list[str], raw: str):
        self.verdict = verdict        # "APPROVED" or "NEEDS_REVISION"
        self.issues = issues
        self.raw = raw

    def is_approved(self) -> bool:
        return self.verdict == "APPROVED"

    def __repr__(self):
        return f"SpecReviewResult({self.verdict}, {len(self.issues)} issues)"


class SpecReviewer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def review(self, spec: str, design: TechnicalDesign) -> SpecReviewResult:
        user_message = (
            f"SPECIFICATION:\n{spec}\n\n"
            f"TECHNICAL DESIGN:\n{design.to_markdown()}"
        )

        raw = self.llm.complete(
            system_prompt=SPEC_REVIEWER,
            user_message=user_message,
            label="spec-reviewer",
        )

        return self._parse(raw)

    def _parse(self, raw: str) -> SpecReviewResult:
        verdict = "NEEDS_REVISION"
        if "VERDICT: APPROVED" in raw:
            verdict = "APPROVED"

        issues = []
        if verdict == "NEEDS_REVISION":
            issues_section = re.search(r"Issues:(.*?)$", raw, re.DOTALL | re.IGNORECASE)
            if issues_section:
                for line in issues_section.group(1).strip().split("\n"):
                    line = line.strip()
                    if re.match(r"^\d+\.", line):
                        issues.append(line)

        return SpecReviewResult(verdict=verdict, issues=issues, raw=raw)
