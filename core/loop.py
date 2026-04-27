"""
loop.py

Orchestrates the full pipeline for a single run.
Calls agents in sequence, manages the repair loop,
invokes the stall detector after each cycle.
"""

from core.session import Session
from core.stall_detector import StallDetector, CriticOutput
from agents.meta_architect import MetaArchitect
from agents.architect import Architect
from agents.coder import Coder
from agents.critic import Critic
from agents.planner import Planner
from agents.designer import Designer
from core.llm import LLMClient


def run_pipeline(session: Session, max_cycles: int = 6, play: bool = True) -> dict:
    config = session.config
    llm = LLMClient(config)

    stall_detector = StallDetector(min_cycles_to_detect=3, similarity_threshold=0.6)

    try:
        # Phase 0: Meta-Architect decides stack and language
        print("Phase 0  Meta-Architect...")
        meta = MetaArchitect(llm)
        stack_decision = meta.decide(session.prompt, forced_target=session.forced_target)
        print(f"  stack: {stack_decision.get('language', '?')} / {stack_decision.get('target', '?')}")

        # Phase 1: Architect produces SPEC.md
        print("Phase 1  Architect...")
        architect = Architect(llm)
        spec = architect.build_spec(session.prompt, stack_decision)
        session.write_spec(spec)
        print(f"  spec: {len(spec)} chars")

        # Phase 2: Designer adds visual guidelines to spec (pre-code)
        print("Phase 2  Designer (pre-code guidelines)...")
        designer = Designer(llm)
        visual_guidelines = designer.pre_code_guidelines(spec)

        # Phase 3: Main repair loop (Coder → Critic → Planner)
        print("Phase 3  Coder/Critic loop...")
        coder = Coder(llm)
        critic = Critic(llm)
        planner = Planner(llm)

        # Initial code generation
        files = coder.generate_all(spec, visual_guidelines, session)
        for filename, content in files.items():
            session.write_file(filename, content)

        cycle = 0
        verdict = "NEEDS_FIXES"
        # Tracks failed fix reasons per file across cycles to break deterministic loops.
        # Key: filename, Value: list of reason strings from previous cycles.
        fix_history: dict[str, list[str]] = {}

        while verdict != "ALL_COMPLETE" and cycle < max_cycles:
            cycle += 1
            print(f"  Critic cycle {cycle}...")

            snapshot = session.get_project_snapshot(token_limit=config.get("snapshot_limit", 800))
            verdict, issues, raw = critic.review(spec, snapshot)

            session.log_critic_cycle(cycle, verdict, issues, raw)
            session.metrics.cycles = cycle

            critic_output = CriticOutput(cycle=cycle, verdict=verdict, issues=issues)
            stall_detector.add(critic_output)

            if verdict == "ALL_COMPLETE":
                print(f"  ALL_COMPLETE at cycle {cycle}")
                break

            # Check for stall before attempting a fix
            stall = stall_detector.check()
            if stall:
                print(f"  STALL detected at cycle {cycle}: {stall.pattern[:80]}")
                session.metrics.stall_detected = True
                session.metrics.stall_pattern = stall.pattern
                session.metrics.stall_diagnosis = stall.diagnosis
                print(f"  Diagnosis: {stall.diagnosis[:120]}")
                verdict = "STALL"
                break

            if not issues:
                # Critic said NEEDS_FIXES but listed no issues — treat as complete
                print(f"  NEEDS_FIXES with no listed issues, treating as ALL_COMPLETE")
                verdict = "ALL_COMPLETE"
                break

            print(f"  {len(issues)} issue(s) — running Planner...")
            fix_plan = planner.plan(issues)

            print(f"  Coder fixing {len(fix_plan)} file(s)...")
            for fix in fix_plan:
                filename = fix.get("file")
                reason = fix.get("reason", "")
                current_content = session.generated_files.get(filename, "")
                history = fix_history.get(filename, [])
                fixed_content = coder.fix_file(filename, current_content, reason, spec, session,
                                               fix_history=history)
                session.write_file(filename, fixed_content)
                # Accumulate this reason in history for next cycle
                if filename not in fix_history:
                    fix_history[filename] = []
                fix_history[filename].append(reason)

        # Phase 4: Executor (functional tests)
        if verdict == "ALL_COMPLETE":
            print("Phase 4  Executor (functional tests)...")
            try:
                from core.executor import Executor
                executor = Executor()
                executor_result = executor.run(session.files_path)
                session.metrics.executor_pass = executor_result.get("pass", False)
                session.metrics.executor_details = executor_result
                print(f"  executor: {'PASS' if session.metrics.executor_pass else 'FAIL'}")
            except ImportError:
                print("  Executor not available (playwright not installed)")
                session.metrics.executor_pass = None

            # Phase 5: Designer post-render audit
            print("Phase 5  Designer (visual audit)...")
            try:
                score, designer_cycles = designer.post_render_audit(
                    session.files_path, spec, visual_guidelines, coder, planner, session
                )
                session.metrics.designer_score = score
                session.metrics.designer_cycles = designer_cycles
                print(f"  visual score: {score}/10 after {designer_cycles} audit cycle(s)")
            except Exception as e:
                print(f"  Designer audit failed: {e}")

            # Open in browser if requested
            if play:
                index = session.files_path / "index.html"
                if index.exists():
                    import subprocess
                    subprocess.Popen(["explorer.exe", str(index.resolve())])

        final_verdict = verdict
        session.finish(verdict=final_verdict)
        return vars(session.metrics)

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"\nPipeline error: {e}")
        if session.debug:
            print(tb)
        session.finish(verdict="ERROR", error=str(e))
        return vars(session.metrics)
