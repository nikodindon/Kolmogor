"""
task_coder.py

A Coder specialized for single atomic tasks in project mode.
Unlike the simple-mode Coder which generates all files at once,
the TaskCoder receives one task at a time and patches the existing file.

Key difference: it receives the CURRENT file content and adds/modifies
only what the task requires. This prevents the token ceiling problem
by keeping each generation pass small and focused.
"""

import re
from core.llm import LLMClient
from agents.decomposer import Task

TASK_CODER_PROMPT = """You are a focused code implementation agent. You receive a single task to implement and the current file content. You add or modify only what the task requires.

Rules:
- Output the COMPLETE updated file — not a diff, not a patch, the full file.
- Implement ONLY what the task description says. Do not implement future tasks.
- Do not remove or break existing code from previous tasks.
- The done_when condition is your implementation target. Meet it exactly.
- CRITICAL: No stubs, no empty function bodies, no TODO comments, no placeholder logic.
  Every function you write must contain real, working implementation code.
  A function with just `// TODO` or `console.log('placeholder')` is a failure.
- If a function needs to track state (current piece position, score, board state),
  declare the state variable at the top of the script and use it properly.
- If a previous instruction is provided, it means your last attempt had a specific problem — fix it.
- Output as a markdown code block with the filename as a comment on the first line.
- Do not explain. Output only the code block."""


class TaskCoder:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def implement(
        self,
        task: Task,
        current_content: str,
        spec_context: str,
        instruction: str = None,
    ) -> str:
        """
        Implement a single task on top of the current file content.
        Returns the updated file content.
        """
        instruction_block = ""
        if instruction:
            instruction_block = f"\nSPECIFIC INSTRUCTION FOR THIS ATTEMPT:\n{instruction}\n"

        user_message = (
            f"TASK: {task.id} — {task.title}\n"
            f"DESCRIPTION: {task.description}\n"
            f"DONE WHEN: {task.done_when}\n"
            f"FILE TO MODIFY: {task.file}\n"
            f"{instruction_block}\n"
            f"SPEC CONTEXT (for reference):\n{spec_context[:800]}\n\n"
            f"CURRENT FILE CONTENT:\n"
            f"```\n{current_content or '(empty — create from scratch)'}\n```\n\n"
            f"Implement task {task.id}. Output the complete updated file."
        )

        raw = self.llm.complete(
            system_prompt=TASK_CODER_PROMPT,
            user_message=user_message,
            label=f"task-coder:{task.id}",
        )

        return self._extract(raw, task.file)

    def _extract(self, raw: str, filename: str) -> str:
        """Extract code from the first markdown code block."""
        pattern = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)
        for match in pattern.finditer(raw):
            block = match.group(1)
            lines = block.split("\n")
            # Strip filename comment if present
            first = lines[0].strip() if lines else ""
            for comment_pat in [
                r"^//\s*[\w./\-]+\.\w+",
                r"^#\s*[\w./\-]+\.\w+",
                r"^<!--\s*[\w./\-]+\.\w+",
            ]:
                if re.match(comment_pat, first):
                    lines = lines[1:]
                    break
            code = "\n".join(lines).strip()
            if code:
                return code

        # Fallback: return raw stripped
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            parts = cleaned.split("\n")
            end = len(parts) - 1 if parts[-1].strip() == "```" else len(parts)
            cleaned = "\n".join(parts[1:end])
        return cleaned
