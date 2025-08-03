import os
import subprocess
import json

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UNDO_LOG = os.path.join(ROOT_DIR, ".qilife_undo.json")

# Track actions for summary
SUMMARY_LOG = []

# Robust .gitignore template provided by user
GITIGNORE_CONTENT = """# (Full robust .gitignore content pasted here) ...
"""

# Load PolyForm license from file in root directory
with open(os.path.join(ROOT_DIR, "PolyForm-Noncommercial-1.0.0.txt"), "r", encoding="utf-8") as license_file:
    LICENSE_CONTENT = license_file.read()

# README and pyproject templates
README_CONTENT = """---
title: "{module_name} Overview"
tags:
  - qilife
  - module
  - documentation
---

# {module_name}

Overview and usage instructions for this QiLife module.
"""

PYPROJECT_CONTENT = """[build-system]
requires = ["setuptools", "wheel"]

[project]
name = "qi_{module_base}"
version = "0.1.0"
"""

# Starter file templates
STARTER_INIT = '"""\nqi_{module_base} package initialization.\n"""'
STARTER_MAIN = '''from .utils import helper_function

def main():
    """Entry point for qi_{module_base}."""
    helper_function()
    print("Hello from qi_{module_base}!")

if __name__ == "__main__":
    main()
'''
STARTER_UTILS = '''def helper_function():
    """Example helper function for qi_{module_base}."""
    print("Helper function called from qi_{module_base}")
'''
STARTER_TEST = '''from src.qi_{module_base}.main import main

def test_main_runs():
    assert main() is None
'''
STARTER_CONFIG = '''[default]
app_name = qi_{module_base}
version = 0.1.0
'''

# File structure
REQUIRED_STRUCTURE = {
    "src": {
        "qi_{module_base}": ["__init__.py", "main.py", "utils.py"]
    },
    "tests": ["__init__.py", "test_main.py"],
    "docs": ["index.rst"],
    "data": ["config.ini"],
    ".gitignore": GITIGNORE_CONTENT,
    "README.md": README_CONTENT,
    "LICENSE": LICENSE_CONTENT,
    "pyproject.toml": PYPROJECT_CONTENT,
    "requirements.txt": "requests\npytest\n"
}

# Logging helper
def log_created(path):
    if not os.path.exists(UNDO_LOG):
        with open(UNDO_LOG, "w") as f:
            json.dump([], f)
    with open(UNDO_LOG, "r") as f:
        data = json.load(f)
    data.append(path)
    with open(UNDO_LOG, "w") as f:
        json.dump(data, f)

# Create file with per-file prompt and track summary
def create_file(path, content="", overwrite=False, interactive=False):
    action = None

    if interactive and os.path.exists(path):
        print(f"File exists: {path}")
        choice = input("[O]verwrite, create [B]ackup (.bak), or [S]kip? (O/B/S): ").strip().lower()
        if choice == "o":
            action = "overwrite"
        elif choice == "b":
            action = "bak"
        else:
            print(f"Skipped {path}")
            SUMMARY_LOG.append((path, "skipped"))
            return

    if overwrite or action == "overwrite" or not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        log_created(path)
        SUMMARY_LOG.append((path, "overwritten" if os.path.exists(path) else "created"))
        return

    bak_path = path + ".bak"
    with open(bak_path, "w", encoding="utf-8") as f:
        f.write(content)
    log_created(bak_path)
    SUMMARY_LOG.append((bak_path, "backup created"))

# Preview structure
def preview_structure(base_path, module_base):
    print(f"\nChecking structure for: {base_path}")
    for key, value in REQUIRED_STRUCTURE.items():
        if isinstance(value, dict):
            folder_path = os.path.join(base_path, key, f"qi_{module_base}")
            for file in value["qi_{module_base}"]:
                file_path = os.path.join(folder_path, file)
                if not os.path.exists(file_path):
                    print(f"  [MISSING FILE] {file_path}")
                else:
                    print(f"  [EXISTS] {file_path}")
        elif isinstance(value, list):
            folder_path = os.path.join(base_path, key)
            for file in value:
                file_path = os.path.join(folder_path, file)
                if not os.path.exists(file_path):
                    print(f"  [MISSING FILE] {file_path}")
                else:
                    print(f"  [EXISTS] {file_path}")
        else:
            file_path = os.path.join(base_path, key)
            if not os.path.exists(file_path):
                print(f"  [MISSING FILE] {file_path}")
            else:
                print(f"  [EXISTS] {file_path}")

# Ensure structure
def ensure_structure(base_path, module_base, overwrite=False, interactive=False):
    for key, value in REQUIRED_STRUCTURE.items():
        if isinstance(value, dict):
            folder_path = os.path.join(base_path, key)
            os.makedirs(folder_path, exist_ok=True)
            module_path = os.path.join(folder_path, f"qi_{module_base}")
            os.makedirs(module_path, exist_ok=True)
            for file in value["qi_{module_base}"]:
                content = STARTER_INIT if file == "__init__.py" else STARTER_MAIN if file == "main.py" else STARTER_UTILS
                create_file(os.path.join(module_path, file), content.format(module_base=module_base), overwrite, interactive)
        elif isinstance(value, list):
            folder_path = os.path.join(base_path, key)
            os.makedirs(folder_path, exist_ok=True)
            for file in value:
                content = STARTER_TEST if file == "test_main.py" else ""
                create_file(os.path.join(folder_path, file), content.format(module_base=module_base), overwrite, interactive)
        else:
            file_path = os.path.join(base_path, key)
            if key == "data":
                content = STARTER_CONFIG.format(module_base=module_base)
            else:
                content = value.format(module_name=f"qi_{module_base}", module_base=module_base)
            create_file(file_path, content, overwrite, interactive)

# Virtual environment setup
def ensure_venv(base_path, dry_run=False):
    venv_path = os.path.join(base_path, ".venv")
    if not os.path.exists(venv_path):
        print(f"  [MISSING VENV] {venv_path}")
        if not dry_run:
            print(f"[+] Creating virtual env in: {base_path}")
            subprocess.run(["python3", "-m", "venv", ".venv"], cwd=base_path)
            log_created(venv_path)
    else:
        print(f"  [OK] Virtual env exists")

# Rollback function
def rollback():
    if not os.path.exists(UNDO_LOG):
        print("No undo log found.")
        return
    with open(UNDO_LOG, "r") as f:
        files = json.load(f)
    for path in files:
        if os.path.exists(path):
            if os.path.isdir(path):
                try:
                    os.rmdir(path)
                except OSError:
                    pass
            else:
                os.remove(path)
    os.remove(UNDO_LOG)
    print("Rollback completed.")

# Choose mode
def choose_mode():
    print("Select run mode:")
    print("1) Dry Run")
    print("2) Standard Run")
    print("3) Rollback")
    choice = input("Enter choice (1/2/3): ").strip()
    if choice == "1":
        return "dry"
    elif choice == "2":
        return "standard"
    elif choice == "3":
        return "rollback"
    else:
        print("Invalid choice, defaulting to Dry Run.")
        return "dry"

# Display summary
def display_summary():
    if SUMMARY_LOG:
        print("\nSummary of actions:")
        for path, action in SUMMARY_LOG:
            print(f"- {action.upper()}: {path}")
    else:
        print("\nNo changes made.")

# Main flow
def main():
    mode = choose_mode()

    if mode == "rollback":
        rollback()
        return

    dry_run = (mode == "dry")
    overwrite = False
    interactive = False

    if not dry_run:
        choice = input("Do you want per-file prompts for overwrite/backup? (y/N): ").strip().lower()
        interactive = (choice == "y")
        if not interactive:
            overwrite_input = input("Overwrite all existing files instead of .bak? (y/N): ").strip().lower()
            overwrite = (overwrite_input == "y")

    for item in os.listdir(ROOT_DIR):
        subfolder_path = os.path.join(ROOT_DIR, item)
        if os.path.isdir(subfolder_path) and item.startswith("qilife-"):
            module_base = item.replace("qilife-", "")
            print(f"\n=== Processing {item} ===")

            preview_structure(subfolder_path, module_base)
            ensure_venv(subfolder_path, dry_run=dry_run)

            if dry_run:
                proceed = input(f"Apply changes to {item}? (y/N): ").strip().lower()
                if proceed != "y":
                    print(f"Skipped {item}.")
                    continue

            ensure_structure(subfolder_path, module_base, overwrite, interactive)
            if not dry_run:
                print(f"[DONE] {item} standardized.")

    display_summary()

if __name__ == "__main__":
    main()
