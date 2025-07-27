import os
from fileflow.analyzer import analyze_file
from fileflow.renamer import generate_new_name
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

def ask_for_folder():
    folder = input("📂 Enter the full path of the folder to scan and rename files:\n> ").strip()
    while not os.path.isdir(folder):
        print("❌ That folder does not exist. Try again.")
        folder = input("> ").strip()
    return os.path.abspath(folder)

def main():
    source_root = ask_for_folder()

    log_path = "inplace_rename_log.csv"
    logfile = open(log_path, "w", encoding="utf-8")
    logfile.write("original_path,new_name,new_full_path\n")

    print(f"\n🔍 Scanning for files in: {source_root}\n")

    for root, _, files in os.walk(source_root):
        for file in tqdm(files, desc=f"📂 {os.path.relpath(root, source_root)}"):
            path = os.path.join(root, file)

            try:
                # Skip system junk
                if file.lower() in ['.ds_store', 'thumbs.db']:
                    continue

                meta = analyze_file(path)
                new_name = generate_new_name(path, meta)

                if new_name == file:
                    continue  # No change

                new_path = os.path.join(root, new_name)

                os.rename(path, new_path)
                logfile.write(f"{path},{new_name},{new_path}\n")

            except Exception as e:
                print(f"❌ Error on {path}: {e}")

    logfile.close()
    print(f"\n✅ Done. Renamed files are logged in: {log_path}")

if __name__ == "__main__":
    main()
