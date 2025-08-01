import os
import argparse
from datetime import datetime

def print_directory_tree(root_dir, show_files=True, max_depth=None, current_depth=0, prefix='', log_file=None, include_hidden=True, exclude_dirs=None):
    """
    Recursively prints the directory tree structure up to the specified depth and writes to a log file.
    """
    if exclude_dirs is None:
        exclude_dirs = [
            'venv', '__pycache__', 'data', 'logs',
            '.git', '.vscode', '.idea', '.pytest_cache',
            '.venv', '.DS_Store', '.env', '.env.local',
            '.env.development.local', '.env.test.local',
            '.env.production.local', 'Empty_Folders',
            '.docusaurus', '.docusaurus-plugin-content-docs-current',
            # Node / frontend bloat
            'node_modules', '.node_modules',
            # Tools/programs we don’t want
            'mpc-hc', 'losslesscut', 'OCR', 'pdf-main', 'my-pdf-main',
            # Tests (ignore any folder containing these patterns)
            'test', 'tests', '__tests__',
            # Plugins and cache
            'plugins', '.local'
        ]

    if max_depth is not None and current_depth >= max_depth:
        return

    try:
        # Get the list of items in the directory
        items = os.listdir(root_dir)
    except PermissionError:
        message = prefix + "└── [Permission Denied]"
        print(message)
        if log_file:
            log_file.write(message + "\n")
        return
    except FileNotFoundError:
        message = prefix + "└── [Directory Not Found]"
        print(message)
        if log_file:
            log_file.write(message + "\n")
        return

    # Sort items: directories first, then files
    items = sorted(items, key=lambda s: s.lower())
    directories = [item for item in items if os.path.isdir(os.path.join(root_dir, item))]
    files = [item for item in items if not os.path.isdir(os.path.join(root_dir, item))]

    # Exclude directories that match or contain any exclude pattern
    directories = [
        item for item in directories
        if not any(ex.lower() in item.lower() for ex in exclude_dirs)
    ]

    # Show files or just folders
    items = directories if not show_files else directories + files

    for index, item in enumerate(items):
        if not include_hidden and item.startswith('.'):
            continue

        path = os.path.join(root_dir, item)
        # Determine tree connector style
        if index == len(items) - 1:
            connector = '└── '
            extension = '    '
        else:
            connector = '├── '
            extension = '│   '

        # Print and log
        message = prefix + connector + item
        print(message)
        if log_file:
            log_file.write(message + "\n")

        # Recurse into directories
        if os.path.isdir(path):
            print_directory_tree(path, show_files, max_depth, current_depth + 1,
                                 prefix + extension, log_file, include_hidden, exclude_dirs)

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description='Map and print the directory structure of a given top-level directory.')
    parser.add_argument('directory', nargs='?', default=None, help='Path to the top-level directory (optional)')
    return parser.parse_args()

def get_valid_directory(initial_path=None):
    """Prompts for a valid directory path, or uses initial_path if valid."""
    if initial_path:
        root_dir = os.path.abspath(initial_path)
        if os.path.isdir(root_dir):
            return root_dir
        else:
            print(f"Error: The provided path '{root_dir}' is not a valid directory.")

    while True:
        user_input = input("Enter the parent directory path: ").strip()
        root_dir = os.path.abspath(user_input)
        if os.path.isdir(root_dir):
            return root_dir
        else:
            print(f"Error: The path '{root_dir}' is not a valid directory. Please try again.")

def get_user_choice():
    """Prompt: Show folders only or folders + files?"""
    while True:
        choice = input("Do you want to display (1) Only Folders or (2) Both Folders and Files? Enter 1 or 2: ").strip()
        if choice == "1":
            return False
        elif choice == "2":
            return True
        else:
            print("Invalid choice. Please enter 1 or 2.")

def get_max_depth():
    """Prompt: Max depth (1-5 or all)"""
    while True:
        choice = input("Enter the maximum depth to display (1, 2, 3, 4, 5, or 'all' for unlimited): ").strip()
        if choice.lower() == 'all':
            return None
        if choice.isdigit() and int(choice) in {1, 2, 3, 4, 5}:
            return int(choice)
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 'all'.")

def create_log_file(filename_prefix, suffix=""):
    """Creates a timestamped log file in Downloads."""
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")

    sanitized_prefix = "".join(c for c in filename_prefix if c.isalnum() or c in (' ', '_', '-')).strip()
    if not sanitized_prefix:
        sanitized_prefix = "log"

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_log_file_name = f"{sanitized_prefix}_{timestamp}{suffix}"
    log_file_name = f"{base_log_file_name}.txt"
    log_file_path = os.path.join(downloads_dir, log_file_name)

    counter = 1
    while os.path.exists(log_file_path):
        log_file_name = f"{base_log_file_name}_{counter}.txt"
        log_file_path = os.path.join(downloads_dir, log_file_name)
        counter += 1

    return open(log_file_path, "w", encoding="utf-8")

def run_again_prompt():
    """Asks the user if they want to run the program again."""
    while True:
        choice = input("Run the program again? (yes/no): ").lower()
        if choice in ('yes', 'y'):
            return True
        elif choice in ('no', 'n'):
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def main(root_dir):
    """Main orchestrator for generating directory tree."""
    try:
        show_files = get_user_choice()
        max_depth = get_max_depth()

        log_file_tree = create_log_file(os.path.basename(root_dir), "_tree")
        print(f"Log file created: {log_file_tree.name}")
        print(f"Resolved path: {root_dir}")
        log_file_tree.write(f"Resolved path: {root_dir}\n")

        print_directory_tree(root_dir, show_files, max_depth, log_file=log_file_tree)
        log_file_tree.close()
        print(f"Directory structure logged in: {log_file_tree.name}")

    except Exception as e:
        print(f"An unexpected error occurred in main: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    while True:
        current_root_dir = get_valid_directory(args.directory)
        main(current_root_dir)
        args.directory = None
        if not run_again_prompt():
            break
