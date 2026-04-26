"""
stall_detector.py

Detects when a Critic/Coder repair loop is stuck and not converging.

A stall is not just the same message twice. It is a pattern of non-convergence:
the same category of issue recurring across multiple cycles despite Coder attempts
to fix it. The distinction matters because small models sometimes produce slightly
different wording for the same underlying failure.

StallDetector is stateful: it receives one CriticOutput per cycle and accumulates
history. Call check() after each cycle. It returns a StallReport when a stall is
detected, or None if the loop is still converging.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CriticOutput:
    cycle: int
    verdict: str          # "ALL_COMPLETE" or "NEEDS_FIXES"
    issues: list[str]     # raw issue strings from the Critic


@dataclass
class StallReport:
    cycle_detected: int
    pattern: str          # human-readable description of the stall pattern
    recurring_issues: list[str]
    cycles_blocked: int
    diagnosis: str        # hint toward likely cause


class StallDetector:
    """
    Monitors Critic outputs across cycles and detects non-convergence.

    Configuration:
        min_cycles_to_detect  minimum cycles before a stall can be declared
                              (avoids false positives on the first repetition)
        similarity_threshold  fraction of issues that must match to count as
                              a repeated pattern (0.0 to 1.0)
    """

    def __init__(self, min_cycles_to_detect: int = 3, similarity_threshold: float = 0.6):
        self.min_cycles_to_detect = min_cycles_to_detect
        self.similarity_threshold = similarity_threshold
        self.history: list[CriticOutput] = []

    def add(self, output: CriticOutput):
        self.history.append(output)

    def check(self) -> Optional[StallReport]:
        """
        Returns a StallReport if a stall is detected, None otherwise.
        Should be called after each add().
        """
        if len(self.history) < self.min_cycles_to_detect:
            return None

        # Only look at NEEDS_FIXES cycles (ALL_COMPLETE is not a stall)
        fix_cycles = [h for h in self.history if h.verdict == "NEEDS_FIXES"]
        if len(fix_cycles) < self.min_cycles_to_detect:
            return None

        # Take the last N fix cycles and check for issue recurrence
        recent = fix_cycles[-self.min_cycles_to_detect:]
        issue_sets = [set(self._normalize_issues(c.issues)) for c in recent]

        # Find issues that appear in all recent cycles
        recurring = issue_sets[0]
        for s in issue_sets[1:]:
            recurring = recurring & s

        if not recurring:
            return None

        # Check if recurring issues represent a significant fraction of total issues
        total_issues = set()
        for s in issue_sets:
            total_issues |= s
        ratio = len(recurring) / max(len(total_issues), 1)

        if ratio < self.similarity_threshold:
            return None

        # Stall confirmed — build the report
        pattern = self._describe_pattern(recurring)
        diagnosis = self._diagnose(recurring, recent)

        return StallReport(
            cycle_detected=recent[-1].cycle,
            pattern=pattern,
            recurring_issues=list(recurring),
            cycles_blocked=len(recent),
            diagnosis=diagnosis,
        )

    def _normalize_issues(self, issues: list[str]) -> list[str]:
        """
        Normalize issue strings to reduce surface variation while preserving
        the underlying error category. Strips line numbers, file paths,
        specific variable names, and lowercases everything.
        """
        normalized = []
        for issue in issues:
            s = issue.lower()
            # Remove line numbers like ":42" or "line 42"
            s = re.sub(r"line\s+\d+", "", s)
            s = re.sub(r":\d+", "", s)
            # Remove file paths
            s = re.sub(r"[\w./\\]+\.(js|py|html|css|ts)", "<file>", s)
            # Collapse whitespace
            s = " ".join(s.split())
            normalized.append(s)
        return normalized

    def _describe_pattern(self, recurring: set[str]) -> str:
        if not recurring:
            return "unknown pattern"
        samples = list(recurring)[:3]
        return f"recurring issue(s) across {self.min_cycles_to_detect}+ cycles: " + " | ".join(samples)

    def _diagnose(self, recurring: set[str], cycles: list[CriticOutput]) -> str:
        """
        Produce a diagnostic hint based on the nature of the recurring issues.
        This is a heuristic, not a definitive answer.
        """
        combined = " ".join(recurring).lower()

        if any(word in combined for word in ["import", "module", "not found", "undefined", "missing"]):
            return (
                "The Coder is not resolving missing imports or undefined references. "
                "Possible causes: model too small to track cross-file dependencies, "
                "or spec does not make file roles explicit enough."
            )

        if any(word in combined for word in ["syntax", "unexpected token", "invalid", "parse"]):
            return (
                "Persistent syntax errors suggest the model is generating malformed code "
                "that it cannot self-correct. Consider a larger Coder model or reducing "
                "file complexity in the spec."
            )

        if any(word in combined for word in ["logic", "never called", "not triggered", "missing call"]):
            return (
                "Logic errors that survive repeated fix cycles typically indicate the "
                "text-only Critic cannot see the runtime behavior. The Executor should "
                "catch these. If the Executor also passes, the issue description in the "
                "Critic prompt may be too vague."
            )

        if any(word in combined for word in ["css", "style", "color", "border", "layout"]):
            return (
                "Visual issues recurring despite fix cycles. The Coder tends to ignore "
                "CSS guidelines. The Designer post-render audit is the correct enforcement "
                "mechanism — check that it is enabled and that its threshold is appropriate."
            )

        return (
            "Pattern not matched to a known category. Review the full critic_log.jsonl "
            "for this run. Consider whether the issue is in the Architect spec (too vague), "
            "the Coder model (too small), or the Critic prompt (identifying impossible fixes)."
        )

    def reset(self):
        self.history = []
