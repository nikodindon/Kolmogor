"""
architect.py
"""

from core.llm import LLMClient
from agents.prompts import ARCHITECT


class Architect:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def build_spec(self, prompt: str, stack_decision: dict) -> str:
        user_message = (
            f"User prompt: {prompt}\n\n"
            f"Stack decision:\n{stack_decision}\n\n"
            "Produce the full SPEC.md."
        )
        return self.llm.complete(
            system_prompt=ARCHITECT,
            user_message=user_message,
            label="architect",
        )
