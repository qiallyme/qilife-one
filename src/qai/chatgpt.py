# src/ai/chatgpt.py

from openai import OpenAI
from src.config.env import get_config

client = OpenAI(api_key=get_config().get("OPENAI_API_KEY"))

def ask_gpt(prompt: str, model="gpt-4", temp=0.3) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
    )
    return response.choices[0].message.content
