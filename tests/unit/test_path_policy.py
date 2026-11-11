"""Unit tests for path policy security checks."""

import os
from pathlib import Path
from blender_addon.security.path_policy import is_safe_workspace_path


def test_path_policy_system_root():
    sys_root = os.environ.get("SystemRoot", r"C:\Windows")
    bad_path = os.path.join(sys_root, "System32", "evil.blend")
    assert is_safe_workspace_path(bad_path) is False


def test_path_policy_allowed_workspace():
    workspace = r"C:\Users\test\project"
    good_path = r"C:\Users\test\project\scenes\model.blend"
    bad_path = r"C:\Users\test\other\model.blend"

    assert is_safe_workspace_path(good_path, allowed_workspace=workspace) is True
    assert is_safe_workspace_path(bad_path, allowed_workspace=workspace) is False


def test_path_policy_empty_path():
    assert is_safe_workspace_path("") is False
    assert is_safe_workspace_path(None) is False
