from fileflow.analyzer import analyze_file
from fileflow.renamer import generate_new_name
from fileflow.approval import get_user_approval
from fileflow.mover import move_file
import time

def process_batch(queue, config):
    for _ in range(min(config["BATCH_SIZE"], len(queue))):
        path = queue.pop(0)
        try:
            meta = analyze_file(path)
            new_name = generate_new_name(path, meta)
            approved = get_user_approval(path, new_name)
            if approved:
                move_file(path, new_name, config["PROCESSED_FOLDER"])
            else:
                print("Skipped.")
        except Exception as e:
            print(f"Error processing {path}: {e}")
        time.sleep(1)
