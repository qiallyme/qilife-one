#!/usr/bin/env python3
import os

def convert_python_to_js(root_path: str) -> None:
    """
    Recursively finds all Python files in a given directory and
    lets the user choose to convert each file to a JavaScript
    file in the same folder or skip it. Supports "convert all"
    to batch the rest. Ignores virtual env, node_modules, DMV, etc.
    """

    # Directories to ignore (case-insensitive match)
    ignored_dirs = {'.git', '__pycache__', 'venv', 'node_modules', '.vscode', '.idea', 'dmv'}

    # Normalize and verify path
    root_path = os.path.expanduser(root_path).strip('"\'')
    root_path = os.path.normpath(root_path)

    if not os.path.exists(root_path):
        print(f"Error: The path '{root_path}' does not exist.")
        return
    if not os.path.isdir(root_path):
        print(f"Error: The path '{root_path}' is not a directory.")
        return

    print(f"Starting conversion process in '{root_path}', ignoring {ignored_dirs} directories...")

    convert_all = False  # Flag to apply convert-all option

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter ignored directories (case-insensitive)
        dirnames[:] = [d for d in dirnames if d.lower() not in ignored_dirs]

        for filename in filenames:
            if filename.endswith(".py"):
                py_file_path = os.path.join(dirpath, filename)
                js_filename = filename.replace(".py", ".js")
                js_file_path = os.path.join(dirpath, js_filename)

                if not convert_all:
                    # Prompt user for action
                    print(f"\nFound Python file: {py_file_path}")
                    choice = input("Convert (c), Skip (s), or Convert All (a)? ").strip().lower()

                    if choice == 's':
                        print(f"Skipped '{py_file_path}'.")
                        continue
                    elif choice == 'a':
                        convert_all = True
                        print("Will convert all remaining files without asking.")

                # Perform conversion
                try:
                    with open(py_file_path, 'r', encoding='utf-8') as py_file:
                        content = py_file.read()

                    with open(js_file_path, 'w', encoding='utf-8') as js_file:
                        js_file.write(content)

                    print(f"Converted '{py_file_path}' → '{js_file_path}'")

                except Exception as e:
                    print(f"Error converting '{py_file_path}': {e}")

    print("\nConversion process completed.")

if __name__ == "__main__":
    user_path = input("Please enter the root path to search for Python files: ")
    convert_python_to_js(user_path)
