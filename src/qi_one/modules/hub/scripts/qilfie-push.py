import os
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_git_command(command, cwd):
    """Run a git command and return output or error."""
    try:
        result = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout.strip() + result.stderr.strip()
    except Exception as e:
        return 1, str(e)

def push_modules():
    # Prompt for dry run
    dry = input("Dry run only? (y/N): ").strip().lower() == "y"
    commit_msg = input("Commit message (default: 'Standardize module structure'): ").strip()
    if not commit_msg:
        commit_msg = "Standardize module structure"

    summary = []

    for folder in os.listdir(ROOT_DIR):
        path = os.path.join(ROOT_DIR, folder)
        if os.path.isdir(path) and folder.startswith("qilife-"):
            print(f"\n=== Processing {folder} ===")

            # Check if git repo exists
            if not os.path.exists(os.path.join(path, ".git")):
                init_choice = input(f"{folder} is not a git repo. Initialize and add remote? (y/N): ").strip().lower()
                if init_choice != "y":
                    summary.append((folder, "Skipped (no git)"))
                    continue

                # Initialize repo
                if not dry:
                    code, msg = run_git_command("git init", path)
                    print(msg)

                    # Set main branch
                    run_git_command("git branch -M main", path)

                    # Prompt for remote
                    remote_url = input(f"Enter remote URL for {folder}: ").strip()
                    if remote_url:
                        run_git_command(f"git remote add origin {remote_url}", path)
                else:
                    print(f"[Dry Run] Would init git and add remote for {folder}")
                    summary.append((folder, "Would init + add remote"))
                    continue

            # Stage all changes
            if not dry:
                run_git_command("git add .", path)
                code, msg = run_git_command(f'git commit -m "{commit_msg}"', path)
                print(msg if msg else "Committed")

                # Push to main
                code, msg = run_git_command("git push origin main", path)
                print(msg if msg else "Pushed")
                summary.append((folder, "Pushed"))
            else:
                print(f"[Dry Run] Would commit & push {folder}")
                summary.append((folder, "Would push"))

    # Summary
    print("\n=== Summary ===")
    for mod, status in summary:
        print(f"{mod}: {status}")

if __name__ == "__main__":
    push_modules()
