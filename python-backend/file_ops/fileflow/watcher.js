from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class FileWatcher(FileSystemEventHandler):
    def __init__(self, queue, watch_folder):
        self.queue = queue
        self.watch_folder = watch_folder

    def on_created(self, event):
        if not event.is_directory:
            self.queue.append(event.src_path)

def start_watcher(queue, watch_folder):
    observer = Observer()
    event_handler = FileWatcher(queue, watch_folder)
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()
    return observer
