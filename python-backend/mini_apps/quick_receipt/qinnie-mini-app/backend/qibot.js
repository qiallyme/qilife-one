import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_response(prompt, context=""):
    try:
        full_prompt = f"User said: {prompt}\nContext:\n{context}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Qinnie, the user's AI sidekick and assistant."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.6
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error: {str(e)}"
