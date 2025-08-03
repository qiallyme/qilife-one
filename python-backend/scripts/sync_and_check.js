import os
import subprocess
import json
from pathlib import Path
import tomllib  # Python 3.11+; use `import tomli as tomllib` for earlier versions

ROOT_DIR = Path(__file__).parent

PYPROJECT_TEMPLATE = """[build-system]
requires = ["setuptools", "wheel"]

[project]
name = "{module_name}"
version = "0.1.0"
dependencies = [
    "requests",
    "pytest"
]
"""

REQUIREMENTS_TEMPLATE = """requests
pytest
"""

SUMMARY_LOG = []

def run_git_command(args, cwd):
    """Run a git command and return code + output."""
    try:
        result = subprocess.run(args, cwd=cwd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout.strip() + result.stderr.strip()
    except Exception as e:
        return 1, str(e)

# ----------- PYPROJECT + REQUIREMENTS SYNC -----------
def sync_pyproject_and_requirements(module_path: Path, dry_run=False):
    pyproject_path = module_path / "pyproject.toml"
    requirements_path = module_path / "requirements.txt"

    # Create pyproject.toml if missing
    if not pyproject_path.exists():
        module_name = module_path.name.replace("-", "_")
        content = PYPROJECT_TEMPLATE.format(module_name=module_name)
        if dry_run:
            print(f"[Dry Run] Would create {pyproject_path}")
        else:
            pyproject_path.write_text(content)
        SUMMARY_LOG.append((str(pyproject_path), "created"))

    # Load dependencies from pyproject
    deps = ["requests", "pytest"]
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            deps = data.get("project", {}).get("dependencies", deps)

    # Convert to requirements format
    req_content = "\n".join(deps) + "\n"

    # Check if requirements.txt exists
    if not requirements_path.exists():
        if dry_run:
            print(f"[Dry Run] Would create {requirements_path}")
        else:
            requirements_path.write_text(req_content)
        SUMMARY_LOG.append((str(requirements_path), "created"))
    else:
        # Compare contents
        existing = requirements_path.read_text().strip()
        if existing != req_content.strip():
            print(f"Mismatch in {requirements_path}:")
            print(f"Current:\n{existing}")
            print(f"New:\n{req_content}")
            choice = input("Overwrite requirements.txt? (y/N): ").strip().lower()
            if choice == "y":
                if not dry_run:
                    requirements_path.write_text(req_content)
                SUMMARY_LOG.append((str(requirements_path), "overwritten"))
            else:
                SUMMARY_LOG.append((str(requirements_path), "kept"))

# ----------- NODE MODULES CHECK -----------
def check_node_modules(dry_run=False):
    node_paths = list(ROOT_DIR.rglob("node_modules"))
    for path in node_paths:
        code, output = run_git_command("git ls-files node_modules", ROOT_DIR)
        if output:
            print(f"[Warning] node_modules tracked in Git: {path}")
            if not dry_run:
                choice = input(f"Remove node_modules from Git tracking? (y/N): ").strip().lower()
                if choice == "y":
                    run_git_command("git rm -r --cached node_modules", ROOT_DIR)
                    SUMMARY_LOG.append((str(path), "removed from git"))
        else:
            print(f"node_modules found but not tracked: {path} (safe)")

# ----------- INIT FILE DUPLICATION CHECK -----------
def check_init_duplicates(dry_run=False):
    for module in ROOT_DIR.iterdir():
        if module.is_dir() and module.name.startswith("qilife-"):
            init_path = module / "__init__.py"
            src_path = module / "src"
            if init_path.exists() and not src_path.exists():
                print(f"Duplicate __init__.py at root: {init_path}")
                choice = input("Delete this duplicate? (y/N): ").strip().lower()
                if choice == "y" and not dry_run:
                    init_path.unlink()
                    SUMMARY_LOG.append((str(init_path), "deleted duplicate"))

# ----------- MAIN SCRIPT -----------
def main():
    dry_run = input("Dry run? (y/N): ").strip().lower() == "y"

    # Sync pyproject & requirements
    for module in ROOT_DIR.iterdir():
        if module.is_dir() and module.name.startswith("qilife-"):
            sync_pyproject_and_requirements(module, dry_run=dry_run)

    # Check node_modules
    check_node_modules(dry_run=dry_run)

    # Check duplicate __init__.py
    check_init_duplicates(dry_run=dry_run)

    # Summary
    print("\n=== Summary ===")
    for path, action in SUMMARY_LOG:
        print(f"{action.upper()}: {path}")
    if not SUMMARY_LOG:
        print("No changes made.")

if __name__ == "__main__":
    main()
