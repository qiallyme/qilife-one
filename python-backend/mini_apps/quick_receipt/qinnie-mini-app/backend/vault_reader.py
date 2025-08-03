import os

VAULT_PATH = os.path.expanduser("~/QinnieVault")  # Replace this with your actual path

def search_vault(query):
    results = []
    for root, dirs, files in os.walk(VAULT_PATH):
        for filename in files:
            if filename.endswith(".md"):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        results.append(f"# {filename}\n{content[:500]}...\n\n")
                        if len(results) >= 3:
                            break
    return "\n".join(results)
