"""
analyst.py

The Analyst is the key to making the Decomposer generic.

It receives the Architect's spec and produces a technical design document:
- state_variables: all data that persists between frames/events
- algorithms: all state transitions implied by the features
- render_strategy: how visual and data state stay in sync
- critical_mechanisms: non-obvious patterns a Coder might miss
- pitfalls: common mistakes for this type of project

The Analyst infers all of this from the spec features alone.
It has no hardcoded domain knowledge — it reasons about any project type.

This solves the core problem discovered in exp-006 run-004/run-005:
the Decomposer was generating vague done_when conditions because it didn't
know what mechanisms were needed. The Analyst fills that gap generically.
"""

import json
from dataclasses import dataclass, field
from core.llm import LLMClient
from agents.prompts import ANALYST


@dataclass
class TechnicalDesign:
    project_type: str = "other"
    state_variables: list[dict] = field(default_factory=list)
    algorithms: list[dict] = field(default_factory=list)
    render_strategy: str = ""
    render_integration: str = ""
    timing: str = ""
    critical_mechanisms: list[str] = field(default_factory=list)
    pitfalls: list[str] = field(default_factory=list)
    raw: str = ""

    def to_markdown(self) -> str:
        lines = [f"# Technical Design\n\n**Project type**: {self.project_type}\n"]

        lines.append("## State variables")
        for v in self.state_variables:
            lines.append(f"- `{v.get('name')}` ({v.get('type')}, {v.get('shape', '')}) — {v.get('purpose')} — init: `{v.get('initial_value', '?')}`")

        lines.append("\n## Algorithms")
        for a in self.algorithms:
            lines.append(f"\n### {a.get('name')}")
            lines.append(f"Triggered by: {a.get('triggered_by', '?')}")
            lines.append(f"Reads: {', '.join(a.get('reads', []))}")
            lines.append(f"Writes: {', '.join(a.get('writes', []))}")
            lines.append(f"Calls: {', '.join(a.get('calls', []))}")
            for i, step in enumerate(a.get('steps', []), 1):
                lines.append(f"  {i}. {step}")

        lines.append(f"\n## Render strategy\n{self.render_strategy}")
        if self.render_integration:
            lines.append(f"\n## Render integration (CRITICAL)\n{self.render_integration}")
        if self.timing:
            lines.append(f"\n## Timing (CRITICAL)\n{self.timing}")

        lines.append("\n## Critical mechanisms")
        for m in self.critical_mechanisms:
            lines.append(f"- {m}")

        lines.append("\n## Pitfalls")
        for p in self.pitfalls:
            lines.append(f"- {p}")

        return "\n".join(lines)

    def to_context_string(self) -> str:
        """Compact version to pass as context to Decomposer and TaskCoder."""
        parts = [f"PROJECT TYPE: {self.project_type}\n"]

        parts.append("STATE VARIABLES:")
        for v in self.state_variables:
            parts.append(f"  {v.get('name')}: {v.get('type')} {v.get('shape', '')} — {v.get('purpose')}")

        if self.render_integration:
            parts.append(f"\nRENDER INTEGRATION (CRITICAL): {self.render_integration}")

        if self.timing:
            parts.append(f"\nTIMING (CRITICAL): {self.timing}")

        parts.append("\nCRITICAL MECHANISMS:")
        for m in self.critical_mechanisms:
            parts.append(f"  - {m}")

        parts.append("\nPITFALLS:")
        for p in self.pitfalls:
            parts.append(f"  - {p}")

        parts.append("\nALGORITHMS:")
        for a in self.algorithms:
            steps = " → ".join(a.get('steps', [])[:3])
            calls = ", ".join(a.get('calls', []))
            parts.append(f"  {a.get('name')}: triggered by {a.get('triggered_by', '?')} → {steps}"
                        + (f" → calls: {calls}" if calls else ""))

        parts.append(f"\nRENDER STRATEGY: {self.render_strategy}")

        return "\n".join(parts)


class Analyst:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def analyse(self, spec: str) -> TechnicalDesign:
        raw = self.llm.complete(
            system_prompt=ANALYST,
            user_message=f"SPEC:\n{spec}",
            label="analyst",
        )

        design = self._parse(raw)
        design.raw = raw
        return design

    def _parse(self, raw: str) -> TechnicalDesign:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
            cleaned = "\n".join(lines[1:end])

        try:
            data = json.loads(cleaned)
            return TechnicalDesign(
                project_type=data.get("project_type", "other"),
                state_variables=data.get("state_variables", []),
                algorithms=data.get("algorithms", []),
                render_strategy=data.get("render_strategy", ""),
                render_integration=data.get("render_integration", ""),
                timing=data.get("timing", ""),
                critical_mechanisms=data.get("critical_mechanisms", []),
                pitfalls=data.get("pitfalls", []),
            )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  [analyst] parse error: {e}")
            # Return minimal design so pipeline doesn't crash
            return TechnicalDesign(
                project_type="other",
                critical_mechanisms=["Analyst parse failed — proceeding without technical design"],
                pitfalls=[],
            )
