import os
import shutil
import subprocess
import uuid
import time
import argparse
import concurrent.futures
import multiprocessing
import sys
import send2trash

# NEW: Import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from send2trash import send2trash
except ImportError:
    print("Warning: 'send2trash' library not found. Files will be permanently deleted instead of moved to Recycle Bin.")
    print("To install: pip install send2trash")
    send2trash = os.remove # Fallback to permanent delete if send2trash is not installed

# --- Configuration ---
BATCH_SIZE = 100 # Still used for sequential mode, less relevant for parallel
MEDIA_EXTENSIONS = ['.media', '.mp4', '.avi', '.mov', '.mkv', '.webm'] # MODIFIED: Added more example extensions
CONVERTED_EXTENSION = '.mp4'
# !! IMPORTANT: Verify this FFmpeg path is correct for your system !!
FFMPEG_PATH = r"C:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
WATCH_INTERVAL_SECONDS = 5 # NEW: How often the watcher should check for events (can be adjusted)

# NEW: Global (or passed) queue/executor for processing new files
# This will be initialized in main and passed to the handler
processing_executor = None
source_folder_global = None
converted_folder_global = None
error_folder_global = None
ffmpeg_preset_global = None
initial_scan_dirs_global = None # To prevent deleting initially existing dirs

# --- Helper Functions (No changes to these for watchdog integration, they are called by the handler) ---

def sanitize_path(path_str):
    """Strips leading/trailing whitespace and quotes from a path string."""
    return path_str.strip().strip('"').strip("'")

def check_ffmpeg():
    """Checks if the FFmpeg executable is accessible and functioning."""
    print(f"\nChecking FFmpeg at: '{FFMPEG_PATH}'")
    if not os.path.isfile(FFMPEG_PATH):
        print(f"Error: FFmpeg executable not found at the specified path: '{FFMPEG_PATH}'")
        print("Please ensure the path is correct and the file exists.")
        return False
    try:
        process = subprocess.run([FFMPEG_PATH, '-version'], capture_output=True, text=True, check=False, timeout=10)
        if process.returncode == 0:
            print(f"FFmpeg found and accessible: {process.stdout.splitlines()[0]}")
            return True
        else:
            print(f"Error: FFmpeg command '-version' failed using path '{FFMPEG_PATH}'. Return code: {process.returncode}")
            print(f"FFmpeg stdout: {process.stdout}")
            print(f"FFmpeg stderr: {process.stderr}")
            return False
    except FileNotFoundError:
        print(f"Error: FFmpeg not found at '{FFMPEG_PATH}'. (FileNotFoundError)")
        return False
    except subprocess.TimeoutExpired:
        print(f"Error: FFmpeg command '-version' timed out using path '{FFMPEG_PATH}'. FFmpeg might be unresponsive.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while checking FFmpeg with path '{FFMPEG_PATH}': {e}")
        return False

def get_media_files(source_folder_root):
    """Scans the source folder and its subdirectories for files matching MEDIA_EXTENSIONS."""
    found_files_list = []
    print(f"\nScanning for files with extensions: {', '.join(MEDIA_EXTENSIONS)} in '{source_folder_root}' and its subdirectories...")
    
    debug_print_limit = 50 
    files_checked_count = 0

    for root, _, files in os.walk(source_folder_root):
        for f_name in files:
            files_checked_count += 1
            file_ext_processed = os.path.splitext(f_name)[1].lower().strip()
            
            # Print debug info for the first few files
            if files_checked_count <= debug_print_limit:
                print(f"    DEBUG: Checking: {os.path.join(root, f_name)} (Processed Ext: '{file_ext_processed}')")
            
            if file_ext_processed in MEDIA_EXTENSIONS:
                full_path = os.path.join(root, f_name)
                found_files_list.append(full_path)
    
    if files_checked_count > debug_print_limit:
        print(f"    DEBUG: ... (file listing truncated after checking {files_checked_count} files, debug_print_limit was {debug_print_limit})")

    if found_files_list:
        print(f"Found {len(found_files_list)} media files to process after filtering.")
    else:
        print(f"No files matching the specified extensions ({', '.join(MEDIA_EXTENSIONS)}) were found.")
    return found_files_list

def run_ffmpeg_conversion(source_file, output_file_full_path, ffmpeg_preset='medium'):
    """Executes FFmpeg to convert a single media file to MP4."""
    try:
        os.makedirs(os.path.dirname(output_file_full_path), exist_ok=True)
        
        command = [
            FFMPEG_PATH, '-hide_banner', '-loglevel', 'error', '-y',
            '-i', source_file,
            '-c:v', 'libx264', '-preset', ffmpeg_preset,
            '-c:a', 'aac',
            output_file_full_path
        ]
        
        print(f"    Converting: {os.path.basename(source_file)} -> {os.path.relpath(output_file_full_path, os.path.dirname(os.path.dirname(output_file_full_path)))}")
        
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        if process.returncode == 0:
            if os.path.exists(output_file_full_path) and os.path.getsize(output_file_full_path) > 0:
                print("    Conversion SUCCESSFUL.")
                return True
            else:
                print("    Conversion FAILED (FFmpeg reported success but output file is missing or empty).")
                print(f"    FFmpeg stderr: {process.stderr.strip()}")
                if os.path.exists(output_file_full_path): os.remove(output_file_full_path)
                return False
        else:
            print(f"    Conversion FAILED (FFmpeg return code: {process.returncode}).")
            print(f"    FFmpeg stderr: {process.stderr.strip()}")
            if os.path.exists(output_file_full_path): os.remove(output_file_full_path)
            return False
    except Exception as e:
        print(f"    An unexpected error occurred during FFmpeg conversion setup or execution: {e}")
        if os.path.exists(output_file_full_path): os.remove(output_file_full_path)
        return False

def move_file_to_folder(source_path, dest_folder_path):
    """Moves a file to a destination folder, handling potential name conflicts by adding a UUID."""
    try:
        os.makedirs(dest_folder_path, exist_ok=True)
        dest_file_path = os.path.join(dest_folder_path, os.path.basename(source_path))
        
        if os.path.exists(dest_file_path):
            base, ext = os.path.splitext(os.path.basename(source_path))
            unique_id = str(uuid.uuid4())[:8]
            dest_file_path = os.path.join(dest_folder_path, f"{base}_{unique_id}{ext}")
            
        shutil.move(source_path, dest_file_path)
        print(f"    Moved to errors: {os.path.basename(source_path)}")
        return dest_file_path
    except Exception as e:
        print(f"    Error moving {source_path} to {dest_folder_path}: {e}")
        return None

def cleanup_empty_dirs(root_dir, initial_scan_dirs):
    """Removes empty directories that were part of the initial scan."""
    print(f"\n--- Cleaning up empty directories in {root_dir} ---")
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Only consider directories that were part of the initial scan's structure
        # or were created for converted files. Avoid deleting the root itself.
        if not dirnames and not filenames and dirpath != root_dir and dirpath not in initial_scan_dirs:
            try:
                os.rmdir(dirpath)
                print(f"    Removed empty directory: {dirpath}")
            except OSError as e:
                print(f"    Error removing directory {dirpath}: {e}")


def process_single_file_for_parallel(file_data):
    """
    Helper function to process a single file, designed to be run by a multiprocessing Pool.
    It encapsulates the conversion and error handling for one file.
    """
    original_full_path, source_folder_abs, converted_folder_root, error_folder_root, ffmpeg_preset = file_data

    operation_log_entry = {
        'id': str(uuid.uuid4()),
        'original_path': original_full_path,
        'timestamp': time.time()
    }

    if not os.path.exists(original_full_path):
        operation_log_entry.update({'status': 'skipped', 'reason': 'file_not_found'})
        return operation_log_entry

    relative_path_from_source = os.path.relpath(original_full_path, source_folder_abs)
    base_name_original, _ = os.path.splitext(relative_path_from_source)
    converted_file_relative_path = f"{base_name_original}{CONVERTED_EXTENSION}"
    converted_file_full_path = os.path.join(converted_folder_root, converted_file_relative_path)

    conversion_success = run_ffmpeg_conversion(original_full_path, converted_file_full_path, ffmpeg_preset) # Pass preset

    if conversion_success:
        try:
            # Move to Recycle Bin (or delete if send2trash not installed)
            send2trash(original_full_path)
            print(f"    Original moved to Recycle Bin: {os.path.basename(original_full_path)}")
            operation_log_entry.update({
                'status': 'converted_and_recycled', # Updated status
                'converted_file_path': converted_file_full_path,
            })
        except Exception as e:
            # If moving to Recycle Bin fails, move original to error folder
            print(f"    Error moving {original_full_path} to Recycle Bin: {e}. Moving original to error folder.")
            moved_to_err_path = move_file_to_folder(original_full_path, error_folder_root)
            operation_log_entry.update({
                'status': 'error',
                'error_type': 'recycling_failed',
                'moved_to_error_path': moved_to_err_path or original_full_path
            })
            # Clean up successfully converted file if original couldn't be handled
            if os.path.exists(converted_file_full_path):
                try: os.remove(converted_file_full_path); print(f"    Cleaned up (deleted) converted file: {converted_file_full_path}")
                except Exception as e_del: print(f"    Error cleaning up converted file {converted_file_full_path}: {e_del}")
    else: # Conversion failed
        moved_to_err_path = move_file_to_folder(original_full_path, error_folder_root)
        operation_log_entry.update({
            'status': 'error',
            'error_type': 'conversion_failed',
            'moved_to_error_path': moved_to_err_path or original_full_path
        })
    
    return operation_log_entry

# NEW: Custom File System Event Handler
class MediaConversionEventHandler(FileSystemEventHandler):
    def __init__(self, source_folder, converted_folder, error_folder, ffmpeg_preset, executor, initial_dirs):
        super().__init__()
        self.source_folder = source_folder
        self.converted_folder = converted_folder
        self.error_folder = error_folder
        self.ffmpeg_preset = ffmpeg_preset
        self.executor = executor # The ProcessPoolExecutor
        self.initial_dirs = initial_dirs
        print(f"Watcher initialized for: {self.source_folder}")

    def process_file_event(self, event_path):
        """Processes a file when it's created or modified."""
        file_ext = os.path.splitext(event_path)[1].lower().strip()
        if file_ext in MEDIA_EXTENSIONS:
            print(f"\n[WATCHER] Detected new/modified media file: {os.path.basename(event_path)}")
            # Submit the conversion task to the processing pool
            # Use a lambda or functools.partial if you need to bind more args
            future = self.executor.submit(
                process_single_file_for_parallel,
                (event_path, self.source_folder, self.converted_folder, self.error_folder, self.ffmpeg_preset)
            )
            # You can add a callback to the future if you want to log results as they complete
            # future.add_done_callback(lambda f: print(f"[WATCHER] Conversion done for {event_path}: {f.result()}"))
            # For simplicity, we just submit it here.
        elif os.path.isdir(event_path):
            # NEW: Re-scan if a directory is created, to potentially find new files within it
            print(f"[WATCHER] Detected new directory: {event_path}. Re-scanning for files.")
            new_files = get_media_files(event_path) # Scan just the new directory
            for file_path in new_files:
                if file_path not in self.initial_dirs: # Avoid re-processing files from initial scan
                    print(f"[WATCHER] Adding newly found file: {os.path.basename(file_path)} to processing queue.")
                    self.executor.submit(
                        process_single_file_for_parallel,
                        (file_path, self.source_folder, self.converted_folder, self.error_folder, self.ffmpeg_preset)
                    )

    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory:
            # Add a small delay to ensure the file is fully written before processing
            time.sleep(1) # Give the file a moment to finish being written
            self.process_file_event(event.src_path)
        else:
            # If a directory is created, also process it (to find files within it)
            time.sleep(1) # Give directory creation a moment
            self.process_file_event(event.src_path)

    def on_moved(self, event):
        """Called when a file or directory is moved/renamed."""
        # Treat moved files as new creations in the target location
        if not event.is_directory:
            self.process_file_event(event.dest_path)

    # You might want to implement on_modified for cases where files are edited in place
    # def on_modified(self, event):
    #     if not event.is_directory:
    #         self.process_file_event(event.src_path)


# --- Main Script ---
def main():
    print("Video Conversion and Recycle Script")
    print("=" * 70)

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Convert media files with FFmpeg, move originals to Recycle Bin upon success.")
    parser.add_argument("--auto-continue", action="store_true",
                        help="Process all files without pausing for user input.")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, 
                        help=f"Number of files to process per batch when --auto-continue is OFF. Default: {BATCH_SIZE}")
    parser.add_argument("--parallel", action="store_true",
                        help="Enable parallel processing of files using multiple CPU cores. Disables batch prompts.")
    parser.add_argument("--ffmpeg-preset", type=str, default="medium",
                        choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
                        help="FFmpeg encoding preset. Trades speed for compression efficiency/quality. Default: medium")
    parser.add_argument("--all-cores", action="store_true",
                        help="Use all available CPU cores for parallel processing (vs. cores-1).")
    # NEW: Add argument for watch mode
    parser.add_argument("--watch", action="store_true",
                        help="Enable continuous folder watching mode. Processes initial files then watches for new ones.")
    
    args = parser.parse_args()

    # Prompt for the source folder interactively
    source_folder_input = sanitize_path(input("Enter the source folder path containing raw media files: "))

    auto_continue_mode = args.auto_continue
    parallel_mode = args.parallel
    ffmpeg_preset = args.ffmpeg_preset
    watch_mode = args.watch # NEW: Get watch mode setting
    
    # If parallel mode is enabled, automatically force auto-continue
    if parallel_mode or watch_mode: # MODIFIED: Watch mode also implies auto-continue
        auto_continue_mode = True
        print("\n--- Parallel processing or Watch mode enabled. Forcing AUTOMATIC mode (no pauses). ---")

    # Initial checks before proceeding
    if not check_ffmpeg():
        print("\nPlease resolve FFmpeg issue before proceeding.")
        if send2trash == os.remove and sys.platform == 'win32':
             print("Note: 'send2trash' is not installed. Files will be permanently deleted on success.")
        return

    if not os.path.isdir(source_folder_input):
        print(f"Error: Source folder '{source_folder_input}' not found.")
        return

    # Define output folder paths based on the source folder
    source_folder_abs = os.path.abspath(source_folder_input)
    parent_dir_of_source = os.path.dirname(source_folder_abs)
    source_base_name = os.path.basename(source_folder_abs)

    converted_folder_root = os.path.join(parent_dir_of_source, f"{source_base_name}_converted")
    error_folder_root = os.path.join(parent_dir_of_source, f"{source_base_name}_errors")

    # Globalize paths and preset for the watcher
    global source_folder_global, converted_folder_global, error_folder_global, ffmpeg_preset_global, initial_scan_dirs_global
    source_folder_global = source_folder_abs
    converted_folder_global = converted_folder_root
    error_folder_global = error_folder_root
    ffmpeg_preset_global = ffmpeg_preset

    # Get the list of media files to process initially
    all_raw_media_files = get_media_files(source_folder_abs)
    
    # Store initial subdirectories to prevent deleting them if they become empty
    # MODIFIED: Store this globally for cleanup_empty_dirs and watcher
    initial_scan_dirs_global = {os.path.abspath(dirpath) for dirpath, dirnames, filenames in os.walk(source_folder_abs)}


    print(f"\nOutput Structure:")
    print(f"    Converted files retaining subfolder structure in: {converted_folder_root}")
    print(f"    Originals of successful conversions will be MOVED TO RECYCLE BIN.")
    print(f"    Originals of failed conversions moved to: {error_folder_root} (originals only, flat structure for errors)")

    # Inform the user about the operating mode
    if watch_mode: # NEW: Watch mode message
        print("\n--- Running in WATCH mode. Initial scan will be processed, then new files will be processed automatically. ---")
    elif auto_continue_mode and not parallel_mode:
        print("\n--- Running in AUTOMATIC mode. No pauses for user input. ---")
    elif not auto_continue_mode:
        print(f"\n--- Running in INTERACTIVE mode. Pausing every {args.batch_size} files. ---")

    # Initialize session tracking variables
    session_operations_log = []
    current_batch_id_counter = 1 
    total_processed_in_session = 0
    files_to_process_main_list = list(all_raw_media_files)

    try:
        # NEW: Initialize the ProcessPoolExecutor before starting operations
        MAX_WORKERS = multiprocessing.cpu_count() if args.all_cores else max(1, multiprocessing.cpu_count() - 1)
        print(f"Using up to {MAX_WORKERS} parallel processes for conversions (FFmpeg preset: '{ffmpeg_preset}').")
        
        global processing_executor # Use the global executor
        with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            processing_executor = executor # Assign the executor for the handler to use

            # --- Initial Scan Processing (run once at startup) ---
            if files_to_process_main_list:
                print("\n--- Starting initial processing of existing files ---")
                files_for_processing = [(f, source_folder_abs, converted_folder_root, error_folder_root, ffmpeg_preset) 
                                        for f in files_to_process_main_list]

                results_iterator = executor.map(process_single_file_for_parallel, files_for_processing, chunksize=10)
                
                for i, result_log_entry in enumerate(results_iterator):
                    session_operations_log.append(result_log_entry)
                    total_processed_in_session += 1
                    sys.stdout.write(f"\rProgress (Initial Scan): Completed {total_processed_in_session}/{len(files_to_process_main_list)} files.")
                    sys.stdout.flush()
                print("\n--- Initial processing complete. ---")
            else:
                print("\n--- No existing media files found for initial processing. ---")


            # NEW: Start the Watcher if --watch argument is provided
            if watch_mode:
                event_handler = MediaConversionEventHandler(
                    source_folder_abs, 
                    converted_folder_root, 
                    error_folder_root, 
                    ffmpeg_preset, 
                    executor, # Pass the shared executor
                    initial_scan_dirs_global # Pass initial dirs to avoid re-processing
                )
                observer = Observer()
                observer.schedule(event_handler, source_folder_abs, recursive=True)
                observer.start()
                print(f"\n--- WATCHING '{source_folder_abs}' for new media files. Press Ctrl+C to stop. ---")
                try:
                    while True:
                        time.sleep(WATCH_INTERVAL_SECONDS) # Keep the main thread alive
                except KeyboardInterrupt:
                    observer.stop()
                    print("\nWatcher stopped by user.")
                observer.join() # Wait until the observer thread terminates
                
            elif not parallel_mode: # Keep sequential processing logic if neither parallel nor watch is enabled
                print(f"Running in sequential mode (FFmpeg preset: '{ffmpeg_preset}').")
                files_processed_in_current_batch_prompt = 0
                operations_for_current_batch_prompt = []

                for file_index, original_full_path in enumerate(files_to_process_main_list):
                    print(f"\nProcessing file {file_index + 1}/{len(files_to_process_main_list)}: {original_full_path}")
                    if not os.path.exists(original_full_path):
                        print(f"    Skipped: File {original_full_path} no longer exists (possibly moved).")
                        continue

                    # The logic for sequential processing is here, identical to your original code
                    # It's now inside the `with concurrent.futures.ProcessPoolExecutor` block
                    # so that `process_single_file_for_parallel` can be used directly or via submit if desired
                    # For sequential, you'd directly call the conversion logic.
                    # To keep things consistent and avoid duplicating the long block of conversion/recycling logic,
                    # we can still use process_single_file_for_parallel here.

                    file_data_for_sequential = (original_full_path, source_folder_abs, converted_folder_root, error_folder_root, ffmpeg_preset)
                    result_log_entry = process_single_file_for_parallel(file_data_for_sequential)

                    session_operations_log.append(result_log_entry)
                    operations_for_current_batch_prompt.append(result_log_entry)
                    files_processed_in_current_batch_prompt += 1
                    total_processed_in_session +=1

                    if not auto_continue_mode and \
                       (files_processed_in_current_batch_prompt >= args.batch_size or (file_index + 1) == len(files_to_process_main_list)):
                        
                        print(f"\n--- Batch {current_batch_id_counter} complete ({files_processed_in_current_batch_prompt} files in this batch segment). ---")
                        print(f"Total processed in this session: {total_processed_in_session}")
                        
                        user_choice_valid = False
                        while not user_choice_valid:
                            prompt_text = "Choose action: [C]ontinue, [S]top (finalize), [E]xit immediately: "
                            choice = input(prompt_text).lower()
                            if choice in ['c', 's', 'e']: user_choice_valid = True
                            else: print("Invalid choice.")

                        if choice == 's': print("Stopping script."); return
                        if choice == 'e': print("Exiting immediately."); return
                        
                        current_batch_id_counter += 1 
                        files_processed_in_current_batch_prompt = 0
                        operations_for_current_batch_prompt = []
                    
                if operations_for_current_batch_prompt and not auto_continue_mode:
                    print(f"\n--- Final batch segment complete ({files_processed_in_current_batch_prompt} files). ---")

    except KeyboardInterrupt:
        print("\n--- User interrupted. ---")
    except Exception as e_main:
        print(f"\nAn CRITICAL UNEXPECTED error occurred in the main script: {e_main}")
        import traceback
        traceback.print_exc()
        if session_operations_log: 
            log_file_path_on_error = os.path.join(parent_dir_of_source, f"{source_base_name}_session_log_on_CRITICAL_error.txt")
            try:
                with open(log_file_path_on_error, "w") as log_f_err:
                    for op in session_operations_log: log_f_err.write(str(op) + "\n")
                print(f"Session log attempting to save to {log_file_path_on_error}")
            except Exception as e_log: print(f"Could not save session log: {e_log}")
    finally:
        print("\n--- Script processing finished. ---")
        if total_processed_in_session > 0:
            print(f"Total files processed in this session: {total_processed_in_session}")
            print(f"Converted files output to subdirectories within: {converted_folder_root}")
            print(f"Originals of successful conversions were MOVED TO RECYCLE BIN (or deleted if send2trash was not installed).")
            print(f"Originals of failed conversions (if any) moved to: {error_folder_root}")
            
            # Optional: Clean up empty subdirectories in the source folder
            # MODIFIED: Pass the global initial_scan_dirs_global
            cleanup_empty_dirs(source_folder_abs, initial_scan_dirs_global)

        elif not all_raw_media_files:
            pass
        else: 
            print("No files were fully processed in this session.")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()