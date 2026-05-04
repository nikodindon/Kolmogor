"""
project_loop.py

Orchestrates the project mode pipeline:

  CONCEPTION: Meta-Architect → Architect → Analyst → Spec Reviewer → Decomposer → Plan Reviewer
  DEVELOPMENT: [PM → TaskCoder → Reviewer] × N
  VALIDATION:  Executor → Designer

The conception phase (phases 0-4) ensures the project is fully designed
before any code is written. Agents validate each other's output.
The development phase (phase 5) implements tasks one at a time.
"""

import json
from datetime import datetime
from pathlib import Path

from core.session import Session
from core.llm import LLMClient
from agents.meta_architect import MetaArchitect
from agents.architect import Architect
from agents.analyst import Analyst
from agents.spec_reviewer import SpecReviewer
from agents.decomposer import Decomposer, TaskPlan
from agents.plan_reviewer import PlanReviewer
from agents.task_coder import TaskCoder
from agents.reviewer import Reviewer
from agents.project_manager import ProjectManager, PMDecision
from agents.designer import Designer

MAX_CONCEPTION_LOOPS = 3
MAX_PLAN_LOOPS = 3


def run_project_pipeline(session: Session, play: bool = True) -> dict:
    config = session.config
    llm = LLMClient(config)

    pm_log_path = session.run_path / "pm_log.jsonl"
    task_plan_path = session.run_path / "task_plan.md"
    design_path = session.run_path / "technical_design.md"

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
        # ── CONCEPTION PHASE ────────────────────────────────────────────────

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

        # Phase 2: Analyst + Spec Reviewer loop
        print("Phase 2  Analyst...")
        analyst_agent = Analyst(llm)
        spec_reviewer_agent = SpecReviewer(llm)
        design = None

        for attempt in range(MAX_CONCEPTION_LOOPS):
            design = analyst_agent.analyse(spec)
            design_path.write_text(design.to_markdown(), encoding="utf-8")
            print(f"  [{attempt+1}] {design.project_type} — "
                  f"{len(design.state_variables)} vars, "
                  f"{len(design.algorithms)} algos, "
                  f"{len(design.critical_mechanisms)} mechanisms")

            print(f"  [{attempt+1}] Spec Reviewer...")
            spec_review = spec_reviewer_agent.review(spec, design)
            print(f"  [{attempt+1}] {spec_review.verdict}"
                  + (f" — {len(spec_review.issues)} issues" if spec_review.issues else ""))

            if spec_review.is_approved():
                break
            if attempt < MAX_CONCEPTION_LOOPS - 1:
                issues_text = "\n".join(spec_review.issues)
                spec = f"{spec}\n\n## Revision notes\n{issues_text}"
                session.write_spec(spec)
            else:
                print(f"  Max conception loops — proceeding with current design")

        # Phase 3: Designer pre-code guidelines
        print("Phase 3  Designer (pre-code guidelines)...")
        designer = Designer(llm)
        visual_guidelines = designer.pre_code_guidelines(spec)

        # Phase 4: Decomposer + Plan Reviewer loop
        print("Phase 4  Decomposer...")
        decomposer = Decomposer(llm)
        plan_reviewer_agent = PlanReviewer(llm)
        plan = None

        for attempt in range(MAX_PLAN_LOOPS):
            plan = decomposer.decompose(spec, stack_decision, design)
            task_plan_path.write_text(plan.to_markdown(), encoding="utf-8")
            print(f"  [{attempt+1}] {len(plan.tasks)} tasks:")
            print(plan.summary())

            print(f"  [{attempt+1}] Plan Reviewer...")
            plan_review = plan_reviewer_agent.review(design, plan)
            print(f"  [{attempt+1}] {plan_review.verdict}"
                  + (f" — {len(plan_review.issues)} issues" if plan_review.issues else ""))

            if plan_review.is_approved():
                break
            if attempt < MAX_PLAN_LOOPS - 1:
                issues_text = "\n".join(plan_review.issues)
                spec = f"{spec}\n\n## Plan revision notes\n{issues_text}"
            else:
                print(f"  Max plan loops — proceeding with current plan")

        # ── DEVELOPMENT PHASE ───────────────────────────────────────────────

        print("\nPhase 5  Project Manager loop...")
        task_coder = TaskCoder(llm)
        reviewer = Reviewer(llm)
        pm = ProjectManager(llm)

        current_task = plan.next_pending()
        total_task_cycles = 0

        # Build design context string to pass to TaskCoder
        design_context = design.to_context_string() if design else ""

        while current_task is not None:
            current_task.status = "IN_PROGRESS"
            print(f"\n  Task {current_task.id}: {current_task.title}")
            print(f"  done_when: {current_task.done_when[:80]}")

            current_content = session.generated_files.get(current_task.file, "")
            instruction = getattr(current_task, "_instruction", None)

            print(f"  Coder implementing {current_task.id} (retry {current_task.retry_count})...")
            new_content = task_coder.implement(
                task=current_task,
                current_content=current_content,
                spec_context=spec + "\n\nVISUAL GUIDELINES:\n" + visual_guidelines
                              + "\n\nTECHNICAL DESIGN:\n" + design_context,
                instruction=instruction,
            )
            session.write_file(current_task.file, new_content)
            total_task_cycles += 1

            review = reviewer.review(current_task, new_content)
            print(f"  Reviewer: {review.status}"
                  + (f" ({len(review.issues)} issues)" if review.issues else ""))

            session.log_critic_cycle(
                cycle=total_task_cycles,
                verdict=review.status,
                issues=review.issues,
                raw_response=review.raw,
            )

            if review.is_done():
                current_task.status = "DONE"
                print(f"  ✓ {current_task.id} DONE")
                current_task = plan.next_pending()
            else:
                current_task.retry_count += 1
                decision = pm.decide(plan, review.raw, current_task)
                log_pm(decision, review.raw[:100])
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

                current_task._instruction = decision.instruction

        task_plan_path.write_text(plan.to_markdown(), encoding="utf-8")
        session.metrics.cycles = total_task_cycles

        verdict = "ALL_COMPLETE" if plan.all_done() else (
            "RETROSPECTIVE" if session.metrics.stall_detected else "INCOMPLETE"
        )

        # ── VALIDATION PHASE ────────────────────────────────────────────────

        if verdict == "ALL_COMPLETE":
            print("\nPhase 6  Executor (functional tests)...")
            try:
                from core.executor import Executor
                executor = Executor()
                executor_result = executor.run(session.files_path)
                session.metrics.executor_pass = executor_result.get("pass", False)
                session.metrics.executor_details = executor_result
                print(f"  executor: {'PASS' if session.metrics.executor_pass else 'FAIL'}")
            except Exception as e:
                print(f"  Executor error: {e}")

            print("Phase 7  Designer (visual audit)...")
            try:
                from agents.planner import Planner
                planner = Planner(llm)
                score, designer_cycles = designer.post_render_audit(
                    session.files_path, spec, visual_guidelines, task_coder, planner, session
                )
                session.metrics.designer_score = score
                session.metrics.designer_cycles = designer_cycles
                print(f"  visual score: {score}/10 after {designer_cycles} cycle(s)")
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
