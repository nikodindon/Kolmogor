"""
meta_architect.py

Receives a raw natural language prompt, decides the technical stack,
and returns a stack decision dict for the Architect.

This is the layer that makes the pipeline truly general: the user never
specifies a language or framework. The Meta-Architect reads the intent
and chooses the minimal viable stack for a local 7B model.
"""

import json
from core.llm import LLMClient
from agents.prompts import META_ARCHITECT


class MetaArchitect:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def decide(self, prompt: str, forced_target: str = None) -> dict:
        # If target is forced, bypass LLM and build decision directly
        if forced_target:
            language_map = {
                "html_js": "JavaScript",
                "single_html": "JavaScript",
                "python_pygame": "Python",
                "python_cli": "Python",
            }
            file_hints_map = {
                "html_js": ["index.html", "game.js", "style.css"],
                "single_html": ["index.html"],
                "python_pygame": ["main.py"],
                "python_cli": ["main.py"],
            }
            constraints_map = {
                "html_js": ["self-contained single HTML file preferred", "no external dependencies", "canvas or DOM"],
                "single_html": ["single file only: index.html", "all CSS in <style> tag", "all JS in <script> tag", "no external files", "no imports"],
                "python_pygame": ["single file preferred", "pygame only", "no external assets"],
                "python_cli": ["single file", "stdlib only unless specified"],
            }
            return {
                "language": language_map.get(forced_target, "JavaScript"),
                "target": forced_target,
                "rationale": f"Forced by --target flag",
                "constraints": constraints_map.get(forced_target, []),
                "file_hints": file_hints_map.get(forced_target, ["index.html"]),
            }
        raw = self.llm.complete(
            system_prompt=META_ARCHITECT,
            user_message=prompt,
            label="meta-architect",
        )

        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        try:
            decision = json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback: default to HTML/JS if parsing fails
            print(f"  [meta-architect] JSON parse failed, defaulting to html_js")
            decision = {
                "language": "JavaScript",
                "target": "html_js",
                "rationale": "Default fallback (JSON parse failed)",
                "constraints": ["self-contained", "no external dependencies"],
                "file_hints": ["index.html", "game.js", "style.css"],
            }

        return decision
