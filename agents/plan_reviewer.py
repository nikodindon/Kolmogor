"""
plan_reviewer.py

Validates that the task plan correctly covers all mechanisms from the technical design.
Part of the conception phase — runs after the Decomposer, before development starts.

Checks:
- Every critical_mechanism from the analysis has a task with a behavioral done_when
- Every done_when is behavioral (not structural)
- Task dependencies are coherent (no task reads state from a task it doesn't depend on)
- No mechanism is missing or duplicated

This is the last gate before development. If it approves the plan,
the PM can start TaskCoder cycles with confidence that the plan is complete.
"""

import re
from core.llm import LLMClient
from agents.prompts import PLAN_REVIEWER
from agents.analyst import TechnicalDesign
from agents.decomposer import TaskPlan


class PlanReviewResult:
    def __init__(self, verdict: str, issues: list[str], raw: str):
        self.verdict = verdict        # "APPROVED" or "NEEDS_REVISION"
        self.issues = issues
        self.raw = raw

    def is_approved(self) -> bool:
        return self.verdict == "APPROVED"

    def __repr__(self):
        return f"PlanReviewResult({self.verdict}, {len(self.issues)} issues)"


class PlanReviewer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def review(self, design: TechnicalDesign, plan: TaskPlan) -> PlanReviewResult:
        user_message = (
            f"TECHNICAL DESIGN:\n{design.to_markdown()}\n\n"
            f"TASK PLAN:\n{plan.to_markdown()}"
        )

        raw = self.llm.complete(
            system_prompt=PLAN_REVIEWER,
            user_message=user_message,
            label="plan-reviewer",
        )

        return self._parse(raw)

    def _parse(self, raw: str) -> PlanReviewResult:
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

        return PlanReviewResult(verdict=verdict, issues=issues, raw=raw)
