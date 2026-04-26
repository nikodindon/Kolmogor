"""
designer.py

Two-phase visual quality agent.

Phase 1 (pre-code): enriches the spec with concrete visual guidelines
before the Coder runs.

Phase 2 (post-render): opens the generated artifact in Playwright,
extracts computed styles, audits against guidelines, scores 1-10,
and triggers CSS fix cycles if below threshold.
"""

from pathlib import Path
from core.llm import LLMClient
from agents.prompts import DESIGNER_PRE, DESIGNER_POST

VISUAL_SCORE_THRESHOLD = 7


class Designer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def pre_code_guidelines(self, spec: str) -> str:
        return self.llm.complete(
            system_prompt=DESIGNER_PRE,
            user_message=f"SPEC:\n{spec}",
            label="designer-pre",
        )

    def post_render_audit(
        self, files_path: Path, spec: str, guidelines: str, coder, planner, session
    ) -> tuple[float, int]:
        """
        Opens index.html in a headless browser, extracts styles,
        runs audit cycles until score >= threshold or max cycles reached.
        Returns (final_score, audit_cycles_used).
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("  [designer] playwright not installed, skipping visual audit")
            return 0.0, 0

        index = files_path / "index.html"
        if not index.exists():
            print("  [designer] no index.html, skipping visual audit")
            return 0.0, 0

        audit_cycle = 0
        max_audit_cycles = 3
        score = 0.0

        while audit_cycle < max_audit_cycles:
            audit_cycle += 1
            computed_styles = self._extract_styles(index)
            score, verdict, issues = self._audit(spec, guidelines, computed_styles)

            print(f"  [designer] audit cycle {audit_cycle}: {score}/10 — {verdict}")

            if verdict == "VISUALLY_COMPLETE" or score >= VISUAL_SCORE_THRESHOLD:
                break

            if not issues:
                break

            # Trigger CSS fix
            fix_plan = planner.plan(issues)
            for fix in fix_plan:
                filename = fix.get("file")
                reason = fix.get("reason", "")
                if not filename:
                    continue
                current_content = session.generated_files.get(filename, "")
                fixed = coder.fix_file(filename, current_content, reason, spec, session)
                session.write_file(filename, fixed)

        return score, audit_cycle

    def _extract_styles(self, index_path: Path) -> str:
        """
        Open the page in Playwright, extract key computed styles via JS.
        Returns a plain text summary.
        """
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f"file://{index_path.resolve()}", timeout=10000)
                page.wait_for_timeout(1000)

                styles = page.evaluate("""() => {
                    const results = [];
                    const selectors = ['body', 'h1', 'h2', 'button', 'input', '.grid', '.board', '#game'];
                    selectors.forEach(sel => {
                        const el = document.querySelector(sel);
                        if (el) {
                            const s = window.getComputedStyle(el);
                            results.push({
                                selector: sel,
                                backgroundColor: s.backgroundColor,
                                color: s.color,
                                fontFamily: s.fontFamily,
                                fontSize: s.fontSize,
                                border: s.border,
                                borderRadius: s.borderRadius,
                                display: s.display,
                                justifyContent: s.justifyContent,
                                alignItems: s.alignItems
                            });
                        }
                    });
                    return JSON.stringify(results, null, 2);
                }""")

                browser.close()
                return styles or "No styles extracted."
        except Exception as e:
            return f"Style extraction failed: {e}"

    def _audit(self, spec: str, guidelines: str, computed_styles: str) -> tuple[float, str, list[str]]:
        user_message = (
            f"VISUAL GUIDELINES:\n{guidelines}\n\n"
            f"COMPUTED STYLES FROM BROWSER:\n{computed_styles}"
        )
        raw = self.llm.complete(
            system_prompt=DESIGNER_POST,
            user_message=user_message,
            label="designer-audit",
        )

        # Parse score
        import re
        score = 5.0
        m = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)\s*/\s*10", raw)
        if m:
            score = float(m.group(1))

        verdict = "NEEDS_VISUAL_FIXES"
        if "VERDICT: VISUALLY_COMPLETE" in raw:
            verdict = "VISUALLY_COMPLETE"

        issues = []
        issues_section = re.search(r"Issues:(.*?)(?:VERDICT:|$)", raw, re.DOTALL | re.IGNORECASE)
        if issues_section:
            for line in issues_section.group(1).strip().split("\n"):
                line = line.strip()
                if re.match(r"^\d+\.", line):
                    issues.append(line)

        return score, verdict, issues
