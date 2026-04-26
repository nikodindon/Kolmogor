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

    def decide(self, prompt: str) -> dict:
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
