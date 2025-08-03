# src/config/settings.py
from .env    import get_env, update_env
from .rules  import load_rules, watch_rules

# Single import point for your app:
ENV     = get_env()
RULES   = load_rules()

# Example usage:
#   from src.config.settings import ENV, RULES
#   print(ENV["OPENAI_API_KEY"])
#   print(RULES["drives"]["F"]["subfolders"].keys())

# If you want live-reload in your app startup:
# observer = watch_rules(lambda new: globals().update(RULES=new))
