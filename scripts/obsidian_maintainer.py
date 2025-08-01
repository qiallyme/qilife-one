#!/usr/bin/env python3
import os, re, json, yaml, datetime

# ====== CONFIG ======
VAULT_PATH = r"C:\Path\To\Your\Vault"     # <-- set your vault path
MEDIA_PATH = r"C:\Path\To\MediaArchive"   # <-- external media folder
REPORT_FOLDER = "_VaultHealth"            # folder inside vault for reports
# ====================

def safe_yaml(content):
    try:
        yaml.safe_load(content)
        return True
    except:
        return False

def scan_vault(vault_path):
    report = {
        "invalid_filenames": [],
        "duplicate_filenames": [],
        "broken_links": [],
        "yaml_errors": [],
        "empty_files": [],
        "plugin_errors": [],
        "largest_files": []
    }

    all_files = []
    filename_map = {}

    # 1. Walk vault
    for root, _, files in os.walk(vault_path):
        for file in files:
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, vault_path)
            all_files.append(rel_path)

            # Check invalid characters
            if re.search(r'[<>:"/\\|?*]', file):
                report["invalid_filenames"].append(rel_path)

            # Track duplicates
            name_no_ext = os.path.splitext(file)[0].lower()
            filename_map.setdefault(name_no_ext, []).append(rel_path)

            # Check empty files
            if os.path.getsize(path) == 0:
                report["empty_files"].append(rel_path)

            # Check YAML/frontmatter errors
            if file.endswith(".md"):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if content.startswith('---'):
                        yaml_block = content.split('---')[1]
                        if not safe_yaml(yaml_block):
                            report["yaml_errors"].append(rel_path)

    # 2. Duplicates
    report["duplicate_filenames"] = [
        v for k,v in filename_map.items() if len(v) > 1
    ]

    # 3. Broken links
    md_files = [f for f in all_files if f.endswith('.md')]
    link_pattern = re.compile(r'\[\[([^\]]+)\]\]')
    md_set = {os.path.splitext(f)[0].lower() for f in md_files}
    for md in md_files:
        path = os.path.join(vault_path, md)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for match in link_pattern.findall(content):
                if match.lower() not in md_set:
                    report["broken_links"].append(f"{md} → [[{match}]]")

    # 4. Plugin folder issues
    plugin_dir = os.path.join(vault_path, ".obsidian", "plugins")
    if os.path.exists(plugin_dir):
        for plugin in os.listdir(plugin_dir):
            manifest = os.path.join(plugin_dir, plugin, "manifest.json")
            if os.path.exists(manifest):
                try:
                    json.load(open(manifest))
                except Exception:
                    report["plugin_errors"].append(plugin)
    
    # 5. Largest files
    largest = sorted(
        [(f, os.path.getsize(os.path.join(vault_path, f))) for f in all_files],
        key=lambda x: x[1], reverse=True
    )[:10]
    report["largest_files"] = [f"{f} - {s/1024:.1f} KB" for f,s in largest]

    return report

def generate_media_index(media_path, vault_path):
    lines = ["# Media Index\n"]
    for root, _, files in os.walk(media_path):
        for file in files:
            rel_dir = os.path.relpath(root, media_path)
            rel_path = os.path.join(rel_dir, file).replace("\\", "/")
            abs_path = os.path.join(root, file)
            size = os.path.getsize(abs_path) / (1024*1024)
            lines.append(f"- **{file}** ({size:.1f} MB) – [{rel_path}]({abs_path})")
    return "\n".join(lines)

def save_report(vault_path, report, media_index):
    # Ensure report folder exists
    report_path = os.path.join(vault_path, REPORT_FOLDER)
    os.makedirs(report_path, exist_ok=True)

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(report_path, f"Report-{date}.md")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# Vault Health Report – {date}\n\n")

        for key, items in report.items():
            f.write(f"## {key.replace('_',' ').title()}\n")
            if not items:
                f.write("- None found.\n\n")
            else:
                for item in items:
                    f.write(f"- {item}\n")
                f.write("\n")

        f.write("\n---\n\n")
        f.write(media_index)

    print(f"Report saved to {file_path}")

if __name__ == "__main__":
    vault_report = scan_vault(VAULT_PATH)
    media_index = generate_media_index(MEDIA_PATH, VAULT_PATH)
    save_report(VAULT_PATH, vault_report, media_index)
