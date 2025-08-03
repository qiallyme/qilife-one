import os
import shutil

# Root folder where all qilife-* repos live
ROOT_DIR = r"C:\Users\codyr\Documents\Github\EmpowerQNow713"

# Destination modules folder inside qilife-one
DEST_MODULES = os.path.join(ROOT_DIR, "qilife-one", "src", "qi_one", "modules")

def normalize_name(name):
    """
    Convert qi_module_name -> module_name (drop 'qi_' prefix).
    """
    if name.startswith("qi_"):
        return name[3:]
    return name

def copy_modules():
    if not os.path.exists(DEST_MODULES):
        os.makedirs(DEST_MODULES)

    for folder in os.listdir(ROOT_DIR):
        # Skip non-module repos and skip qilife-one itself
        if not folder.startswith("qilife-") or folder == "qilife-one":
            continue

        repo_path = os.path.join(ROOT_DIR, folder)
        src_path = os.path.join(repo_path, "src")

        # Find qi_* folder inside src
        if not os.path.exists(src_path):
            continue

        # Look for folders starting with qi_
        for item in os.listdir(src_path):
            if item.startswith("qi_"):
                module_path = os.path.join(src_path, item)
                if os.path.isdir(module_path):
                    # Normalize name and set destination path
                    module_name = normalize_name(item)
                    dest_path = os.path.join(DEST_MODULES, module_name)

                    # Copy
                    print(f"Moving module: {module_path} -> {dest_path}")
                    if os.path.exists(dest_path):
                        print(f" - Skipping (already exists)")
                    else:
                        shutil.copytree(module_path, dest_path)

def main():
    print(f"Moving modules into: {DEST_MODULES}")
    copy_modules()
    print("Done!")

if __name__ == "__main__":
    main()
