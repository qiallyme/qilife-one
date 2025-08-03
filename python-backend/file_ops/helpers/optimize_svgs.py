import os
import subprocess
from pathlib import Path

def optimize_all_svgs(source_dir: str):
    """
    Optimizes all .svg files in a directory using svgo CLI and overwrites originals.
    """
    src = Path(source_dir).resolve()

    if not src.exists() or not src.is_dir():
        raise FileNotFoundError(f"❌ Directory not found: {src}")

    svg_files = list(src.glob("*.svg"))
    if not svg_files:
        print("⚠️ No .svg files found in:", src)
        return

    svgo_path = r"C:\Users\codyr\AppData\Roaming\npm\svgo.cmd"

    print(f"⚙️ Optimizing {len(svg_files)} SVG(s) in {src} (will overwrite originals)")
    for svg in svg_files:
        cmd = [svgo_path, str(svg), "-o", str(svg)]  # overwrite original
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Optimized: {svg.name}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to optimize: {svg.name}")
            print(e)


if __name__ == "__main__":
    try:
        folder_input = input("📁 Enter the path to the folder containing SVG files: ").strip()
        if not folder_input:
            raise ValueError("No path provided.")
        optimize_all_svgs(folder_input)
    except Exception as e:
        print("❌ Error:", str(e))
