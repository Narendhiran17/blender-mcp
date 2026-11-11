"""Package blender_addon into a release zip for Blender 'Install from Disk'."""

import os
import shutil
import zipfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
ADDON_DIR = WORKSPACE / "blender_addon"
DIST_DIR = WORKSPACE / "dist"
OUTPUT_ZIP = DIST_DIR / "blender_ai_control_addon-v1.0.0.zip"


def package_addon():
    print(f"Packaging {ADDON_DIR} into {OUTPUT_ZIP}...")
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ADDON_DIR):
            # Exclude pycache and hidden directories
            dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]
            for file in files:
                if file.endswith((".pyc", ".pyo")):
                    continue
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ADDON_DIR)
                # Archive name inside zip with folder prefix 'blender_ai_control'
                arcname = Path("blender_ai_control") / rel_path
                zf.write(file_path, arcname)

    size_kb = OUTPUT_ZIP.stat().st_size / 1024
    print(f"Successfully created: {OUTPUT_ZIP} ({size_kb:.1f} KB)")
    return OUTPUT_ZIP


if __name__ == "__main__":
    package_addon()
