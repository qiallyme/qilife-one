# src/config/env.py

import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

# Always resolve to the project root (2 levels up from /config/)
env_path = Path(__file__).resolve().parents[2] / ".env"

# Load .env file if it exists
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    print(f"⚠️ Warning: .env file not found at {env_path}")

def get_env() -> dict:
    """
    Returns all major environment credentials as a dictionary.
    Extend this list as needed.
    """
    return {
        "OPENAI_API_KEY_MAIN":     os.getenv("OPENAI_API_KEY_MAIN"),
        "GEMINI_API_KEY":          os.getenv("GEMINI_API_KEY"),
        "NOTION_API_KEY":          os.getenv("NOTION_API_KEY"),
        "NOTION_LIFE_FEED_DB_ID":  os.getenv("NOTION_LIFE_FEED_DB_ID"),
        "NOTION_QINOTE_DB_ID":     os.getenv("NOTION_QINOTE_DB_ID"),
        "TWILIO_ACCOUNT_SID":      os.getenv("TWILIO_ACCOUNT_SID"),
        "TWILIO_AUTH_TOKEN":       os.getenv("TWILIO_AUTH_TOKEN"),
        "TWILIO_ACCOUNT_ID":       os.getenv("TWILIO_ACCOUNT_ID"),
        "CLOUDINARY_API_KEY":      os.getenv("CLOUDINARY_API_KEY"),
        "CLOUDINARY_API_SECRET":   os.getenv("CLOUDINARY_API_SECRET"),
        "CLOUDINARY_CLOUD_NAME":   os.getenv("CLOUDINARY_CLOUD_NAME"),
        "CLOUDINARY_URL":          os.getenv("CLOUDINARY_URL"),
    }
def get_value(key: str, fallback: Optional[str] = None) -> str:
    """
    Retrieve a single environment variable by key with optional fallback.
    Always returns a string.
    """
    value = os.getenv(key, fallback)
    return value if value is not None else (fallback if fallback is not None else "")

def update_env(key: str, value: str, verbose: bool = True):
    """
    Safely updates or appends a key=value to the root .env file.
    """
    lines = []
    if env_path.exists():
        lines = [
            line for line in env_path.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
    else:
        env_path.touch()

    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            break
    else:
        lines.append(f"{key}={value}")

    env_path.write_text("\n".join(lines))
    load_dotenv(dotenv_path=env_path, override=True)
    
    if verbose:
        print(f"✅ Updated {key} in .env → {value}")

def get_module_key(module: str) -> str:
    """
    Gets the API key for a specific module, falling back to MAIN if missing,
    empty, or set to "missing" (as a string literal).
    """
    key_name = f"OPENAI_API_KEY_{module.upper()}"
    key_value = os.getenv(key_name)

    if not key_value or key_value.strip().lower() == "missing":
        return os.getenv("OPENAI_API_KEY_MAIN", "")

    return key_value
