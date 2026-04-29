"""
project_loop.py

Orchestrates the project mode pipeline:

  Meta-Architect → Architect → Decomposer → [PM → TaskCoder → Reviewer] × N → Designer

The key difference from the simple loop:
- The Decomposer breaks the spec into atomic tasks
- The PM drives task selection and retry logic
- The TaskCoder implements one task at a time on the growing file
- The Reviewer checks each task against its done_when condition
- The PM logs every decision to pm_log.jsonl for research analysis

This loop is designed to handle projects that exceed the 7B model's
single-pass token budget by decomposing them into sub-budget tasks.
"""

import json
from datetime import datetime
from pathlib import Path

from core.session import Session
from core.llm import LLMClient
from agents.meta_architect import MetaArchitect
from agents.architect import Architect
from agents.decomposer import Decomposer, TaskPlan
from agents.task_coder import TaskCoder
from agents.reviewer import Reviewer
from agents.project_manager import ProjectManager, PMDecision
from agents.designer import Designer


def run_project_pipeline(session: Session, play: bool = True) -> dict:
    config = session.config
    llm = LLMClient(config)

    pm_log_path = session.run_path / "pm_log.jsonl"
    task_plan_path = session.run_path / "task_plan.md"

    def log_pm(decision: PMDecision, context: str = ""):
        entry = {
            "ts": datetime.now().isoformat(),
            "decision": decision.decision,
            "task_id": decision.task_id,
            "reason": decision.reason,
            "instruction": decision.instruction,
            "context": context[:200],
        }
        with open(pm_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    try:
        # Phase 0: Meta-Architect
        print("Phase 0  Meta-Architect...")
        meta = MetaArchitect(llm)
        stack_decision = meta.decide(session.prompt, forced_target=session.forced_target)
        print(f"  stack: {stack_decision.get('language', '?')} / {stack_decision.get('target', '?')}")

        # Phase 1: Architect
        print("Phase 1  Architect...")
        architect = Architect(llm)
        spec = architect.build_spec(session.prompt, stack_decision)
        session.write_spec(spec)
        print(f"  spec: {len(spec)} chars")

        # Phase 2: Decomposer
        print("Phase 2  Decomposer...")
        decomposer = Decomposer(llm)
        plan = decomposer.decompose(spec, stack_decision)
        task_plan_path.write_text(plan.to_markdown(), encoding="utf-8")
        print(f"  {len(plan.tasks)} tasks:")
        print(plan.summary())

        # Phase 3: Designer pre-code guidelines
        print("Phase 3  Designer (pre-code guidelines)...")
        designer = Designer(llm)
        visual_guidelines = designer.pre_code_guidelines(spec)

        # Phase 4: PM-driven task loop
        print("Phase 4  Project Manager loop...")
        task_coder = TaskCoder(llm)
        reviewer = Reviewer(llm)
        pm = ProjectManager(llm)

        current_task = plan.next_pending()
        last_report = "Project starting. No previous report."
        total_task_cycles = 0

        while current_task is not None:
            current_task.status = "IN_PROGRESS"

            print(f"\n  Task {current_task.id}: {current_task.title}")
            print(f"  done_when: {current_task.done_when[:80]}")

            # Get current file content
            current_content = session.generated_files.get(current_task.file, "")

            # Build instruction for this attempt (None on first try)
            instruction = getattr(current_task, "_instruction", None)

            # TaskCoder implements the task
            print(f"  Coder implementing {current_task.id} (retry {current_task.retry_count})...")
            new_content = task_coder.implement(
                task=current_task,
                current_content=current_content,
                spec_context=spec + "\n\nVISUAL GUIDELINES:\n" + visual_guidelines,
                instruction=instruction,
            )
            session.write_file(current_task.file, new_content)
            total_task_cycles += 1

            # Reviewer checks the task
            review = reviewer.review(current_task, new_content)
            last_report = review.raw
            print(f"  Reviewer: {review.status}" + (f" ({len(review.issues)} issues)" if review.issues else ""))

            session.log_critic_cycle(
                cycle=total_task_cycles,
                verdict=review.status,
                issues=review.issues,
                raw_response=review.raw,
            )

            if review.is_done():
                # Task complete — move to next without consulting PM
                current_task.status = "DONE"
                print(f"  ✓ {current_task.id} DONE")
                current_task = plan.next_pending()
                if current_task is None:
                    # No more tasks
                    break
            else:
                # Task failed — consult PM for retry/retrospective decision
                current_task.retry_count += 1
                decision = pm.decide(plan, last_report, current_task)
                log_pm(decision, last_report[:100])
                print(f"  PM: {decision.decision} — {decision.reason[:60]}")

                if decision.decision == "RETROSPECTIVE":
                    current_task.status = "FAILED"
                    session.metrics.stall_detected = True
                    session.metrics.stall_pattern = (
                        f"{current_task.id} failed {current_task.retry_count} times: "
                        f"{'; '.join(review.issues[:2])}"
                    )
                    session.metrics.stall_diagnosis = "Max retries reached. Human analysis needed."
                    print(f"  RETROSPECTIVE triggered on {current_task.id}.")
                    break

                # RETRY — attach instruction for next attempt
                current_task._instruction = decision.instruction
                # current_task stays the same, loop continues

        # Save final task plan state
        task_plan_path.write_text(plan.to_markdown(), encoding="utf-8")
        session.metrics.cycles = total_task_cycles

        # Determine verdict
        if plan.all_done():
            verdict = "ALL_COMPLETE"
        elif session.metrics.stall_detected:
            verdict = "RETROSPECTIVE"
        else:
            verdict = session.metrics.verdict or "INCOMPLETE"

        # Phase 5: Executor
        if verdict == "ALL_COMPLETE":
            print("\nPhase 5  Executor (functional tests)...")
            try:
                from core.executor import Executor
                executor = Executor()
                executor_result = executor.run(session.files_path)
                session.metrics.executor_pass = executor_result.get("pass", False)
                session.metrics.executor_details = executor_result
                print(f"  executor: {'PASS' if session.metrics.executor_pass else 'FAIL'}")
            except Exception as e:
                print(f"  Executor error: {e}")

            # Phase 6: Designer post-render audit
            print("Phase 6  Designer (visual audit)...")
            try:
                score, designer_cycles = designer.post_render_audit(
                    session.files_path, spec, visual_guidelines, task_coder, None, session
                )
                session.metrics.designer_score = score
                session.metrics.designer_cycles = designer_cycles
                print(f"  visual score: {score}/10 after {designer_cycles} audit cycle(s)")
            except Exception as e:
                print(f"  Designer audit error: {e}")

            if play:
                index = session.files_path / "index.html"
                if index.exists():
                    import subprocess
                    subprocess.Popen(["explorer.exe", str(index.resolve())])

        session.finish(verdict=verdict)
        return vars(session.metrics)

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"\nPipeline error: {e}")
        if session.debug:
            print(tb)
        session.finish(verdict="ERROR", error=str(e))
        return vars(session.metrics)
