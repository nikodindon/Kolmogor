"""
hasher.py

Functional hashing: hash the execution output of a generated artifact,
not its source code.

Why: two machines running the same model may generate slightly different
source code due to floating-point accumulation differences between CPU
and GPU inference. But if both programs print "1\n2\n...100\n", their
execution outputs are identical. The functional hash is cross-machine stable.

Established in mnemo Phase 6. Used here as the primary integrity measure.
"""

import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


def hash_execution_output(
    script_path: Path,
    timeout: int = 30,
    input_data: Optional[str] = None,
) -> dict:
    """
    Run a Python script in a subprocess, capture stdout, return SHA256 of output.

    Returns a dict with:
        success:    bool
        hash:       SHA256 hex string (empty if execution failed)
        stdout:     captured output (truncated)
        stderr:     captured errors (truncated)
        exit_code:  process return code
    """
    try:
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            input=input_data,
        )
        stdout = result.stdout
        h = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
        return {
            "success": result.returncode == 0,
            "hash": h,
            "stdout": stdout[:2000],
            "stderr": result.stderr[:500],
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "hash": "",
            "stdout": "",
            "stderr": "timeout",
            "exit_code": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "hash": "",
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
        }


def hash_source(content: str) -> str:
    """SHA256 of source text. Same-machine only — not cross-machine stable."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
