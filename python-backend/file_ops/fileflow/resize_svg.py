import os
import re
from pathlib import Path

def scale_svg_dimensions(svg_content, scale=0.5):
    # Scale width and height attributes
    svg_content = re.sub(
        r'(width|height)="([\d.]+)([^"]*)"',
        lambda m: f'{m.group(1)}="{float(m.group(2)) * scale:.2f}{m.group(3)}"',
        svg_content,
    )
    # Scale viewBox
    def scale_viewbox(m):
        nums = list(map(float, m.group(1).split()))
        scaled = [f"{n * scale:.2f}" for n in nums]
        return f'viewBox="{" ".join(scaled)}"'
    svg_content = re.sub(r'viewBox="([^"]+)"', scale_viewbox, svg_content)

    return svg_content

def resize_svgs(folder_path: str, scale=0.5):
    folder = Path(folder_path).resolve()
    if not folder.exists():
        print("❌ Folder not found.")
        return

    for file in folder.glob("*.svg"):
        content = file.read_text(encoding="utf-8")
        resized = scale_svg_dimensions(content, scale=scale)
        file.write_text(resized, encoding="utf-8")
        print(f"✅ Resized {file.name}")

if __name__ == "__main__":
    folder = input("📁 Path to folder with SVGs to resize: ").strip()
    resize_svgs(folder)
