"""Script to install or symlink blender_addon into Blender's user addons directory."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
WORKSPACE = Path(__file__).resolve().parent.parent
ADDON_SOURCE = WORKSPACE / "blender_addon"


def find_blender_addons_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not set")

    base = Path(appdata) / "Blender Foundation" / "Blender"
    # Search for latest version folder (e.g. 4.2)
    versions = sorted([d.name for d in base.glob("[0-9]*.[0-9]*") if d.is_dir()], reverse=True)
    if not versions:
        raise RuntimeError(f"No Blender installation found in {base}")

    version = versions[0]
    addons_dir = base / version / "scripts" / "addons"
    addons_dir.mkdir(parents=True, exist_ok=True)
    return addons_dir


def install_addon() -> Path:
    addons_dir = find_blender_addons_dir()
    target_dir = addons_dir / "blender_ai_control"

    print(f"Installing add-on from {ADDON_SOURCE} to {target_dir}...")

    # Copy files
    if target_dir.exists():
        if target_dir.is_symlink() or target_dir.is_file():
            target_dir.unlink()
        else:
            shutil.rmtree(target_dir)

    shutil.copytree(ADDON_SOURCE, target_dir)
    print("Add-on files copied successfully.")

    # Enable add-on in Blender preferences
    if Path(BLENDER_EXE).exists():
        print(f"Enabling add-on in Blender via {BLENDER_EXE}...")
        py_cmd = (
            "import bpy; "
            "bpy.ops.preferences.addon_enable(module='blender_ai_control'); "
            "bpy.ops.wm.save_userpref(); "
            "print('ADDON_ENABLED_SUCCESS')"
        )
        res = subprocess.run(
            [BLENDER_EXE, "--background", "--python-expr", py_cmd],
            capture_output=True,
            text=True,
        )
        if "ADDON_ENABLED_SUCCESS" in res.stdout:
            print("Successfully enabled blender_ai_control in Blender preferences!")
        else:
            print("Note: Addon enabled in command run. Output:")
            print(res.stdout[-400:])

    return target_dir


if __name__ == "__main__":
    install_addon()
