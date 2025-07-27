# src/config/rules.py
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

_RULES_PATH = Path(__file__).parent / "folder_rules.json"

def load_rules():
    """Read the JSON config (folder_rules.json)."""
    return json.loads(_RULES_PATH.read_text(encoding="utf-8"))

# Optional hot-reload
class _ReloadHandler(FileSystemEventHandler):
    def __init__(self, callback): self.callback = callback
    def on_modified(self, event):
        if Path(event.src_path) == _RULES_PATH:
            self.callback(load_rules())

_rules_cache = load_rules()

def watch_rules(on_change):
    """Call on_change(new_rules) when the file updates."""
    handler = _ReloadHandler(on_change)
    obs = Observer()
    obs.schedule(handler, _RULES_PATH.parent, recursive=False)
    obs.start()
    return obs  # keep reference if you want to stop()
