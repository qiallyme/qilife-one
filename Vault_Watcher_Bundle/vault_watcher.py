import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

class VaultChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        print(f"[Vault Watcher] Change detected: {event.src_path}")
        try:
            subprocess.run(["python", "scripts/auto_push_vault.py"], check=True)
            subprocess.run(["python", "rag-backend/embedder.py"], check=True)
            print("[Vault Watcher] Vault embedded and pushed to GitHub.")
        except subprocess.CalledProcessError as e:
            print("[Vault Watcher] Error during sync:", e)

if __name__ == "__main__":
    path_to_watch = "vault"
    print(f"[Vault Watcher] Watching: {path_to_watch}")
    observer = Observer()
    observer.schedule(VaultChangeHandler(), path=path_to_watch, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()