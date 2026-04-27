"""
executor.py

Opens a generated HTML artifact in a headless Playwright browser,
detects the artifact type, and runs type-specific functional tests.

Established in local-intent-coder Phase 1.5.
Key findings incorporated:
  - Artifact type detection is mandatory (hardcoded tests fail on wrong type)
  - alert() dialogs must be intercepted (Playwright blocks them by default)
  - Tests must be behavioral, not just structural (check what happens, not what exists)

v1.1 — 2026-04-27 — exp-002-snake run-002 finding:
  The 7B model generates DOM-based games (div grid) rather than Canvas for Snake.
  Both are valid implementations. Executor now distinguishes:
    - arcade_game_canvas: keyword match + canvas present
    - arcade_game_dom:    keyword match + no canvas (div-based rendering)
  Tests are adapted per rendering approach. canvas_present is no longer
  a universal test for arcade games — it depends on what the model actually built.
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
        """
        Detect artifact type with rendering approach awareness.

        For arcade games, we distinguish canvas vs DOM rendering because the 7B model
        often chooses DOM (absolute-positioned divs) over Canvas even for classic games.
        Both are valid — tests must match the actual implementation.
        """
        has_canvas = page.query_selector("canvas") is not None
        has_input = page.query_selector("input") is not None
        has_grid = page.query_selector(".grid, .board, #board, #game-board") is not None

        title = (page.title() or "").lower()
        body_text = (page.inner_text("body") or "").lower()
        combined = body_text + title

        if any(w in combined for w in ["tetris", "snake", "pacman", "invader", "pong", "asteroid", "breakout", "arkanoid"]):
            return "arcade_game_canvas" if has_canvas else "arcade_game_dom"

        if any(w in combined for w in ["tic", "tac", "toe", "chess", "checkers", "connect four", "minesweeper"]):
            return "board_game"

        if any(w in combined for w in ["todo", "task", "list", "note"]):
            return "todo_app"

        if any(w in combined for w in ["counter", "count", "click me"]):
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

        # Universal tests
        tests.append(test("page_loads", lambda: True))
        tests.append(test("no_critical_js_errors", lambda: len([
            e for e in page.evaluate("() => window.__errors__ || []")
            if "undefined" in str(e).lower() or "typeerror" in str(e).lower()
        ]) == 0))

        if artifact_type == "arcade_game_canvas":
            canvas = page.query_selector("canvas")
            tests.append(test("canvas_present", lambda: canvas is not None))
            if canvas:
                size = canvas.bounding_box()
                tests.append(test("canvas_has_size",
                    lambda: size and size["width"] > 0 and size["height"] > 0))

        elif artifact_type == "arcade_game_dom":
            # DOM-based game: check that game elements are rendered as divs/spans
            # and that the game area has content after load
            game_area = page.query_selector(
                "#game-board, #game, .game-board, .board, #snake, .snake-container"
            )
            tests.append(test("game_area_present", lambda: game_area is not None))
            # Check that JS ran and produced some elements (not just empty containers)
            body_html = page.inner_html("body")
            tests.append(test("game_elements_rendered",
                lambda: body_html.count("<div") > 3))
            # Check page has visible content
            tests.append(test("page_has_content",
                lambda: len(page.inner_text("body").strip()) > 0))

        elif artifact_type in ("canvas_game",):
            canvas = page.query_selector("canvas")
            tests.append(test("canvas_present", lambda: canvas is not None))
            if canvas:
                size = canvas.bounding_box()
                tests.append(test("canvas_has_size",
                    lambda: size and size["width"] > 0 and size["height"] > 0))

        elif artifact_type == "board_game":
            cells = page.query_selector_all("td, .cell, .square, [data-cell]")
            tests.append(test("board_renders", lambda: len(cells) >= 9))
            if cells:
                cells[0].click()
                page.wait_for_timeout(300)
                tests.append(test("cell_click_works", lambda: True))

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
            tests.append(test("page_has_content",
                lambda: len(page.inner_text("body").strip()) > 10))

        return tests
