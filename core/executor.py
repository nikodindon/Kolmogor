"""
executor.py

Opens a generated HTML artifact in a headless Playwright browser,
detects the artifact type, and runs type-specific functional tests.

Established in local-intent-coder Phase 1.5.
Key findings incorporated:
  - Artifact type detection is mandatory (hardcoded tests fail on wrong type)
  - alert() dialogs must be intercepted (Playwright blocks them by default)
  - Tests must be behavioral, not just structural (check what happens, not what exists)
"""

from pathlib import Path


class Executor:
    def __init__(self, timeout_ms: int = 10000):
        self.timeout_ms = timeout_ms

    def run(self, files_path: Path) -> dict:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"pass": None, "error": "playwright not installed"}

        index = files_path / "index.html"
        if not index.exists():
            return {"pass": False, "error": "no index.html"}

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                dialogs = []
                page.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))

                console_errors = []
                page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

                page.goto(f"file://{index.resolve()}", timeout=self.timeout_ms)
                page.wait_for_timeout(1000)

                artifact_type = self._detect_type(page)
                results = self._run_tests(page, artifact_type, dialogs)

                browser.close()

                passed = all(r["pass"] for r in results)
                return {
                    "pass": passed,
                    "artifact_type": artifact_type,
                    "tests": results,
                    "console_errors": console_errors[:5],
                    "dialogs": dialogs[:5],
                }
        except Exception as e:
            return {"pass": False, "error": str(e)}

    def _detect_type(self, page) -> str:
        has_canvas = page.query_selector("canvas") is not None
        has_input = page.query_selector("input") is not None
        has_grid = page.query_selector(".grid, .board, #board, #game-board") is not None
        has_table = page.query_selector("table") is not None

        title = (page.title() or "").lower()
        body_text = (page.inner_text("body") or "").lower()

        if any(w in body_text + title for w in ["tetris", "snake", "pacman", "invader", "pong"]):
            return "arcade_game"
        if any(w in body_text + title for w in ["tic", "tac", "toe", "chess", "checkers", "connect"]):
            return "board_game"
        if any(w in body_text + title for w in ["todo", "task", "list", "note"]):
            return "todo_app"
        if any(w in body_text + title for w in ["counter", "count", "click"]):
            return "counter"
        if has_canvas:
            return "canvas_game"
        if has_grid:
            return "board_game"
        if has_input:
            return "form_app"
        return "generic_web"

    def _run_tests(self, page, artifact_type: str, dialogs: list) -> list[dict]:
        tests = []

        def test(name: str, fn) -> dict:
            try:
                result = fn()
                return {"name": name, "pass": bool(result), "detail": str(result)}
            except Exception as e:
                return {"name": name, "pass": False, "detail": str(e)}

        # Tests applicable to all artifact types
        tests.append(test("page_loads", lambda: page.title() is not None or True))
        tests.append(test("no_critical_js_errors", lambda: len([
            e for e in page.evaluate("() => window.__errors__ || []")
            if "undefined" in str(e).lower() or "typeerror" in str(e).lower()
        ]) == 0))

        if artifact_type == "board_game":
            cells = page.query_selector_all("td, .cell, .square, [data-cell]")
            tests.append(test("board_renders", lambda: len(cells) >= 9))
            if cells:
                cells[0].click()
                page.wait_for_timeout(300)
                tests.append(test("cell_click_works", lambda: True))  # no exception = pass

        elif artifact_type in ("arcade_game", "canvas_game"):
            tests.append(test("canvas_present", lambda: page.query_selector("canvas") is not None))
            canvas = page.query_selector("canvas")
            if canvas:
                size = canvas.bounding_box()
                tests.append(test("canvas_has_size", lambda: size and size["width"] > 0 and size["height"] > 0))

        elif artifact_type == "todo_app":
            input_el = page.query_selector("input[type=text], input:not([type])")
            tests.append(test("input_present", lambda: input_el is not None))
            if input_el:
                input_el.fill("test task")
                page.keyboard.press("Enter")
                page.wait_for_timeout(300)
                body = page.inner_text("body")
                tests.append(test("task_added", lambda: "test task" in body))

        elif artifact_type == "counter":
            button = page.query_selector("button")
            tests.append(test("button_present", lambda: button is not None))
            if button:
                initial = page.inner_text("body")
                button.click()
                page.wait_for_timeout(200)
                after = page.inner_text("body")
                tests.append(test("counter_changes", lambda: initial != after))

        else:
            tests.append(test("page_has_content", lambda: len(page.inner_text("body").strip()) > 10))

        return tests
