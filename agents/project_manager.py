"""
project_manager.py

The PM orchestrates the project mode pipeline. It does not generate code.
It reads status reports and decides what happens next.

This is the agent that prevents endless stall loops by:
- Tracking retry counts per task
- Triggering RETROSPECTIVE after 3 failed retries
- Passing specific instructions to the Coder on retry
- Recognizing when the project is complete

The PM is intentionally simple in v1.0 — it uses LLM for decisions but
has hard-coded guardrails (max retries, COMPLETE detection) to prevent
the PM itself from getting confused.
"""

import json
from dataclasses import dataclass
from typing import Optional
from core.llm import LLMClient
from agents.prompts import PROJECT_MANAGER
from agents.decomposer import TaskPlan, Task


@dataclass
class PMDecision:
    decision: str           # NEXT_TASK | RETRY | RETROSPECTIVE | COMPLETE | BLOCKED
    task_id: Optional[str]
    reason: str
    instruction: Optional[str] = None

    def __repr__(self):
        return f"PMDecision({self.decision}, task={self.task_id}, '{self.reason[:60]}')"


class ProjectManager:
    MAX_RETRIES = 3

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def decide(self, plan: TaskPlan, last_report: str, current_task: Optional[Task]) -> PMDecision:
        """
        Given the current plan state and last agent report, decide what to do next.
        Hard-coded guardrails take priority over LLM decision.
        """
        # Guardrail 1: if all tasks are done, always COMPLETE
        if plan.all_done():
            return PMDecision(
                decision="COMPLETE",
                task_id=None,
                reason="All tasks are marked DONE.",
            )

        # Guardrail 2: if current task exceeded max retries, force RETROSPECTIVE
        if current_task and current_task.retry_count >= self.MAX_RETRIES:
            return PMDecision(
                decision="RETROSPECTIVE",
                task_id=current_task.id,
                reason=f"{current_task.id} failed {current_task.retry_count} times. Human analysis needed.",
            )

        # Guardrail 3: if no current task and there's a next pending, always NEXT_TASK
        if current_task is None:
            next_task = plan.next_pending()
            if next_task:
                return PMDecision(
                    decision="NEXT_TASK",
                    task_id=next_task.id,
                    reason="Starting next pending task.",
                )
            return PMDecision(
                decision="BLOCKED",
                task_id=None,
                reason="No pending tasks available and project not complete.",
            )

        # Use LLM for nuanced decisions within guardrails
        return self._llm_decide(plan, last_report, current_task)

    def _llm_decide(self, plan: TaskPlan, last_report: str, current_task: Task) -> PMDecision:
        """Ask the LLM to make a decision, then validate it against guardrails."""

        plan_summary = plan.summary()
        state_lines = []
        for t in plan.tasks:
            state_lines.append(f"{t.id}: {t.status} (retries: {t.retry_count})")
        state_summary = "\n".join(state_lines)

        user_message = (
            f"TASK PLAN:\n{plan_summary}\n\n"
            f"CURRENT STATE:\n{state_summary}\n\n"
            f"CURRENT TASK: {current_task.id} — {current_task.title}\n"
            f"RETRY COUNT: {current_task.retry_count}/{self.MAX_RETRIES}\n\n"
            f"LAST AGENT REPORT:\n{last_report}\n\n"
            "What is your decision?"
        )

        raw = self.llm.complete(
            system_prompt=PROJECT_MANAGER,
            user_message=user_message,
            label="pm",
        )

        decision = self._parse(raw)

        # Validate: if LLM says NEXT_TASK, confirm the task actually exists
        if decision.decision == "NEXT_TASK":
            next_task = plan.next_pending()
            if next_task is None:
                if plan.all_done():
                    decision.decision = "COMPLETE"
                    decision.reason = "All tasks done."
                else:
                    decision.decision = "BLOCKED"
                    decision.reason = "No pending task available."
            else:
                decision.task_id = next_task.id

        return decision

    def _parse(self, raw: str) -> PMDecision:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
            cleaned = "\n".join(lines[1:end])

        try:
            data = json.loads(cleaned)
            return PMDecision(
                decision=data.get("decision", "RETRY"),
                task_id=data.get("task_id"),
                reason=data.get("reason", ""),
                instruction=data.get("instruction"),
            )
        except (json.JSONDecodeError, KeyError):
            # Fallback: safe default is RETRY
            return PMDecision(
                decision="RETRY",
                task_id=None,
                reason="PM parse failed, defaulting to RETRY.",
            )
