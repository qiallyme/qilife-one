import os
from dotenv import load_dotenv
load_dotenv()
print("🔐 OPENAI KEY FOUND:", os.getenv("OPENAI_API_KEY")[:8], "...")

import openai
from fileflow.rules import get_naming_prompt

# Load API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_new_name(filepath, metadata):
    base = metadata["timestamp"]
    ext = os.path.splitext(filepath)[1]
    rules_prompt = get_naming_prompt()

    prompt = f"""
You are an AI file naming assistant. Based on the following file metadata and rules, suggest a clean, descriptive filename.

Metadata:
- Original filename: {metadata.get("original_filename")}
- Extracted text: {metadata.get("text", "")[:500]}
- Parent folder (if any): {metadata.get("parent_folder", "")}

Rules:
{rules_prompt}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates descriptive filenames."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        suggestion = response.choices[0].message.content.strip()
        print("🧠 GPT INPUT PROMPT:\n", prompt)
        print("🧠 GPT RESPONSE:\n", suggestion)
        return f"{suggestion}{ext}"  # ✅ GPT controls the full filename
    except Exception as e:
        print(f"⚠️ GPT fallback due to error: {e}")
        text = metadata.get("text", "").strip().replace("\n", " ").replace("  ", " ")
        snippet = "_".join(text.split()[:5]) or "untitled"
        return f"{suggestion}{ext}"  # ✅ GPT controls the full filename

