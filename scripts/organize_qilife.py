import os
import shutil
from pathlib import Path

# Set base path (edit if needed)
BASE_DIR = Path("C:/Users/codyr/Documents/Github/EmpowerQNow713/qilife-one")

# Target clean structure
TARGETS = {
    "app": ["main", "renderer", "modules", "shared"],
    "docs": [],
    "samples": [],
    "dist": [],
    "scripts": []
}

# 1. Create target folders
for folder, subs in TARGETS.items():
    path = BASE_DIR / folder
    path.mkdir(exist_ok=True)
    for sub in subs:
        (path / sub).mkdir(exist_ok=True)

# 2. Move renderer source to app/renderer
renderer_src = BASE_DIR / "renderer" / "src"
if renderer_src.exists():
    shutil.move(str(renderer_src), BASE_DIR / "app" / "renderer")

# 3. Move qi_one modules to app/modules
qi_modules = BASE_DIR / "app" / "renderer" / "qi_one" / "modules"
if qi_modules.exists():
    dest = BASE_DIR / "app" / "modules"
    for item in qi_modules.iterdir():
        shutil.move(str(item), dest)

# 4. Clean duplicate dist folders (archive old copies)
nested_dist = list(BASE_DIR.glob("**/dist/qilife-one-win32-x64"))
archive_dir = BASE_DIR / "dist" / "archive"
archive_dir.mkdir(parents=True, exist_ok=True)

for folder in nested_dist:
    # Skip if folder is already in BASE_DIR/dist (final destination)
    if folder.parent.parent == BASE_DIR:
        continue

    dest = BASE_DIR / "dist" / folder.name

    # Archive existing target if present
    if dest.exists():
        archived = archive_dir / f"{folder.name}_old"
        counter = 1
        while archived.exists():
            archived = archive_dir / f"{folder.name}_old_{counter}"
            counter += 1
        shutil.move(str(dest), archived)

    # Move this duplicate into final dist
    shutil.move(str(folder), BASE_DIR / "dist")

    # Cleanup parent tree if empty
    try:
        parent = folder.parent
        while parent != BASE_DIR and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent
    except Exception:
        pass

# 5. Move QiDocs
qidocs = BASE_DIR / "renderer" / "src" / "qidocs"
if qidocs.exists():
    shutil.move(str(qidocs), BASE_DIR / "docs")

# 6. Remove build artifacts from repo root
ARTIFACT_EXTENSIONS = [".dll", ".pak", ".bin", ".exe", ".dat"]
for ext in ARTIFACT_EXTENSIONS:
    for file in BASE_DIR.glob(f"**/*{ext}"):
        try:
            os.remove(file)
        except:
            pass

print("Reorganization complete. Check app/, docs/, dist/, and scripts/ for results.")
