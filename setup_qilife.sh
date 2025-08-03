#!/bin/bash

# This script performs a one‑time cleanup and setup for the qi_one Electron/Python
# project.  Run it from the root of the repository.  It removes unnecessary
# folders, updates the .gitignore, creates environment files, implements
# configuration loading for Python, and patches cross‑platform paths in
# main.js and core.py.

set -e

echo "[1/8] Removing unwanted folders..."
# Remove node_modules and qilife-hybrid-dashboard if they exist
rm -rf node_modules
rm -rf qilife-hybrid-dashboard

echo "[2/8] Updating .gitignore..."
# Append ignore patterns if not already present
add_ignore() {
  local pattern="$1"
  if ! grep -qxF "$pattern" .gitignore; then
    echo "$pattern" >> .gitignore
  fi
}
add_ignore "node_modules/"
add_ignore ".venv/"
add_ignore "dist/"
add_ignore "settings.json"

echo "[3/8] Creating .env.example file..."
# Create .env.example only if it does not exist
if [ ! -f .env.example ]; then
  cat > .env.example <<'EOF_ENV'
# Path to watch for new files (absolute path)
SOURCE_FOLDER=/absolute/path/to/watch

# Path where processed files will be moved
PROCESSED_FOLDER=/absolute/path/to/processed

# Number of files to process at a time
BATCH_SIZE=10

# OpenAI API key for file renaming
OPENAI_API_KEY=sk-your-openai-key-here

# Other API keys (optional)
GEMINI_API_KEY=
TWILIO_API_KEY=
EOF_ENV
fi

echo "[4/8] Creating Python config loader..."
# Ensure config directory exists and create env loader
mkdir -p src/qi_one/modules/config
cat > src/qi_one/modules/config/env.py <<'EOF_PY'
import os
from dotenv import load_dotenv


def load_env():
    """Load environment variables from a .env file at the project root.

    Returns a dictionary with SOURCE_FOLDER, PROCESSED_FOLDER and BATCH_SIZE.
    Defaults are empty strings or 10 for BATCH_SIZE if not provided.
    """
    # Determine the project root relative to this file's location
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
    )
    dotenv_path = os.path.join(base_dir, '.env')
    load_dotenv(dotenv_path)

    return {
        'SOURCE_FOLDER': os.getenv('SOURCE_FOLDER', ''),
        'PROCESSED_FOLDER': os.getenv('PROCESSED_FOLDER', ''),
        'BATCH_SIZE': int(os.getenv('BATCH_SIZE', '10')),
    }
EOF_PY

echo "[5/8] Patching Python import in core.py..."
# Patch import path in core.py if present
CORE_FILE="src/qi_one/modules/fileflow/core.py"
if [ -f "$CORE_FILE" ]; then
  if grep -q "from config.env import load_env" "$CORE_FILE"; then
    sed -i.bak "s/from config.env import load_env/from modules.config.env import load_env/" "$CORE_FILE"
  fi
fi

echo "[6/8] Patching main.js for cross‑platform support..."
MAIN_JS="src/qi_one/main.js"
if [ -f "$MAIN_JS" ]; then
  # Replace pythonPath declaration with cross‑platform logic
  sed -i.bak \
    "/const pythonPath/c\\
const pythonPath = process.platform === 'win32' ?\\n  path.join(venvDir, 'Scripts', 'python.exe') :\\n  path.join(venvDir, 'bin', 'python');" "$MAIN_JS"

  # Replace vaultLogPath with user data directory
  sed -i.bak "s|const vaultLogPath = .*|const vaultLogPath = path.join(app.getPath('userData'), 'vault-logs');|" "$MAIN_JS"

  # Replace index.html loading with explicit path
  sed -i.bak "s|win.loadFile('index.html')|win.loadFile(path.join(__dirname, 'index.html'))|" "$MAIN_JS"

  # Optionally disable automatic venv setup to avoid OS-specific issues
  sed -i.bak "s/ensureVenvAndDeps();//" "$MAIN_JS"
fi

echo "[7/8] Staging updated files (optional)..."
git add .gitignore src/qi_one/modules/config/env.py "$CORE_FILE" "$MAIN_JS" .env.example 2>/dev/null || true

echo "[8/8] Setup complete. Review the changes with 'git diff' and commit them if correct."
