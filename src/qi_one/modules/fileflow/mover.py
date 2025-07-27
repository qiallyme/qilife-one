import os
import shutil
from pathlib import Path

UNDO_LOG_PATH = "logs/undo.log"

def move_file(filepath, new_name, destination_folder):
    Path(destination_folder).mkdir(parents=True, exist_ok=True)
    dest_path = os.path.join(destination_folder, new_name)
    shutil.move(filepath, dest_path)

    with open(UNDO_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{filepath} -> {dest_path}\n")
    return dest_path

def undo_last_move():
    if not os.path.exists(UNDO_LOG_PATH):
        print("Nothing to undo.")
        return
    with open(UNDO_LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        print("Nothing to undo.")
        return
    last = lines[-1]
    original, moved = last.strip().split(" -> ")
    shutil.move(moved, original)
    with open(UNDO_LOG_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines[:-1])
    print(f"Undo complete: {moved} -> {original}")
