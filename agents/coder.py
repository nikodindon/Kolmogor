"""
coder.py

Generates all files from the spec, or fixes a single file given an issue.
Parses markdown code blocks — more robust than tool-call formats with small models
(documented finding in nova-game-engine and local-intent-coder).
"""

import re
from core.llm import LLMClient
from agents.prompts import CODER, CODER_FIX


class Coder:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate_all(self, spec: str, visual_guidelines: str, session) -> dict:
        """
        Generate all files listed in the spec.
        Returns a dict of filename -> content.
        """
        user_message = (
            f"SPEC:\n{spec}\n\n"
            f"VISUAL GUIDELINES:\n{visual_guidelines}\n\n"
            "Generate all files."
        )
        raw = self.llm.complete(
            system_prompt=CODER,
            user_message=user_message,
            label="coder-generate",
            max_tokens_override=session.config.get("max_out_tokens", 3000),
        )
        return self._parse_code_blocks(raw)

    def fix_file(self, filename: str, current_content: str, reason: str, spec: str, session,
                 fix_history: list[str] = None) -> str:
        """
        Rewrite a single file to fix a described issue.
        fix_history: list of previous failed reasons for this file, injected to break
        deterministic loops (temperature=0 + same context = same output).
        """
        history_block = ""
        if fix_history:
            history_block = (
                f"\nPREVIOUS FAILED ATTEMPTS ON THIS FILE:\n"
                + "\n".join(f"- {h}" for h in fix_history[-3:])
                + "\nThe above attempts did not resolve the issue. You must take a different approach.\n"
            )

        user_message = (
            f"FILE: {filename}\n\n"
            f"CURRENT CONTENT:\n```\n{current_content}\n```\n"
            f"{history_block}\n"
            f"ISSUE TO FIX: {reason}\n\n"
            f"SPEC CONTEXT:\n{spec[:1000]}\n\n"
            "Rewrite the complete file with the fix applied."
        )
        raw = self.llm.complete(
            system_prompt=CODER_FIX,
            user_message=user_message,
            label=f"coder-fix:{filename}",
        )
        parsed = self._parse_code_blocks(raw)

        # If parsed has our filename, use it; otherwise use the entire response as content
        if filename in parsed:
            return parsed[filename]

        # Fallback: take the first code block found, whatever its filename comment
        if parsed:
            return list(parsed.values())[0]

        # Last resort: strip markdown fences and return raw
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
            cleaned = "\n".join(lines[1:end])
        return cleaned

    def _parse_code_blocks(self, raw: str) -> dict:
        """
        Parse markdown code blocks of the form:
            ```language
            // filename.ext   or   # filename.ext
            <code>
            ```
        Returns dict of filename -> code.
        """
        files = {}
        # Match fenced code blocks
        pattern = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)
        for match in pattern.finditer(raw):
            block = match.group(1)
            lines = block.split("\n")
            if not lines:
                continue

            # Try to extract filename from first line comment
            first = lines[0].strip()
            filename = None

            # Patterns: "// game.js", "# main.py", "/* style.css */", "<!-- index.html -->"
            for comment_pattern in [
                r"^//\s*([\w./\-]+\.\w+)",
                r"^#\s*([\w./\-]+\.\w+)",
                r"^/\*\s*([\w./\-]+\.\w+)",
                r"^<!--\s*([\w./\-]+\.\w+)",
            ]:
                m = re.match(comment_pattern, first)
                if m:
                    filename = m.group(1)
                    lines = lines[1:]  # strip the comment line
                    break

            if filename is None:
                # Cannot determine filename from this block — skip
                continue

            code = "\n".join(lines).strip()
            if code:
                files[filename] = code

        return files
