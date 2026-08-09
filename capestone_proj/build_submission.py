"""
Automated Submission Builder.
Syncs capestone_proj files into 'capestone_proj - submit' directory and builds capestone_proj - submit.zip.
"""

import os
import shutil
import zipfile
from pathlib import Path

def build_submission():
    root_dir = Path(__file__).resolve().parent
    submit_dir = root_dir.parent / "capestone_proj - submit"
    zip_path = root_dir.parent / "capestone_proj - submit.zip"

    print(f"Building submission from {root_dir}...")
    print(f"Target directory: {submit_dir}")
    print(f"Target zip: {zip_path}")

    # Exclude directories/files
    ignore_dirs = {".git", "__pycache__", ".venv", ".pytest_cache", ".streamlit", "storage"}
    ignore_files = {".env", "build_submission.py", "capestone_proj - submit.zip"}

    if submit_dir.exists():
        shutil.rmtree(submit_dir)
    submit_dir.mkdir(parents=True, exist_ok=True)

    # Copy files to submit_dir
    for item in root_dir.rglob("*"):
        if any(ignored in item.parts for ignored in ignore_dirs):
            continue
        if item.name in ignore_files:
            continue
        
        rel_path = item.relative_to(root_dir)
        target_path = submit_dir / rel_path

        if item.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_path)

    print("Copy completed. Creating zip package...")

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in submit_dir.rglob("*"):
            if file.is_file():
                rel_zip_path = file.relative_to(submit_dir)
                zipf.write(file, rel_zip_path)

    print(f"SUCCESS: Package created at {zip_path} ({zip_path.stat().st_size:,} bytes).")

if __name__ == "__main__":
    build_submission()
