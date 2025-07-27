import sys
import os
import time

# Ensure modules folder is added to Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

from fileflow.watcher import start_watcher
from fileflow.batcher import process_batch
from fileflow.mover import undo_last_move
from config.env import load_env

def run():
    print("🌀 Initializing QiFileFlow... please wait")
    queue = []

    # Load config
    cfg = load_env()

    # Auto-create source and processed folders
    os.makedirs(cfg['SOURCE_FOLDER'], exist_ok=True)
    os.makedirs(cfg['PROCESSED_FOLDER'], exist_ok=True)

    # Debug prints
    print(f"DEBUG: Watching {cfg['SOURCE_FOLDER']} - Exists: {os.path.exists(cfg['SOURCE_FOLDER'])}")
    print(f"DEBUG: Processed folder exists: {os.path.exists(cfg['PROCESSED_FOLDER'])}")

    print(f"📂 Source folder: {cfg['SOURCE_FOLDER']}")
    print(f"📁 Processed folder: {cfg['PROCESSED_FOLDER']}")
    print(f"🔁 Batch size: {cfg['BATCH_SIZE']}")

    # Start watcher
    observer = start_watcher(queue, cfg["SOURCE_FOLDER"])
    print(f"👁️ Watching folder: {cfg['SOURCE_FOLDER']} (Ctrl+C to stop)")

    try:
        while True:
            if queue:
                print(f"🧾 Queue size: {len(queue)}")
                process_batch(queue, cfg)
            time.sleep(2)
    except KeyboardInterrupt:
        print("🛑 Stopping watcher...")
        observer.stop()

    observer.join()
    print("✅ Done.")

if __name__ == "__main__":
    print("🌀 QiFileFlow Mini App")
    while True:
        print("\nOptions:\n1. Start watching\n2. Undo last move\n3. Quit")
        choice = input("Select: ").strip()
        if choice == "1":
            run()
        elif choice == "2":
            undo_last_move()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
