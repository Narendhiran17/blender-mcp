"""Path policy and workspace sandboxing for file operations."""

import os
from pathlib import Path
from typing import Optional


def is_safe_workspace_path(filepath: str, allowed_workspace: Optional[str] = None) -> bool:
    """Validate that a filepath is within allowed workspace and not a sensitive system directory."""
    if not filepath or not filepath.strip():
        return False

    resolved = Path(filepath).resolve()

    # Reject dangerous Windows system roots
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    try:
        resolved.relative_to(Path(system_root).resolve())
        return False  # Target is inside Windows directory
    except ValueError:
        pass

    # Program files restriction
    for prog_env in ("ProgramFiles", "ProgramFiles(x86)"):
        prog_dir = os.environ.get(prog_env)
        if prog_dir:
            try:
                resolved.relative_to(Path(prog_dir).resolve())
                return False
            except ValueError:
                pass

    # If explicit workspace restriction is provided
    if allowed_workspace and allowed_workspace.strip():
        workspace_resolved = Path(allowed_workspace).resolve()
        try:
            resolved.relative_to(workspace_resolved)
            return True
        except ValueError:
            return False

    return True
