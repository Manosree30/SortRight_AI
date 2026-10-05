import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()

for m in ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b", "allam-2-7b"]:
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": "Extract item info for 'tea bag'. Return JSON: {\"item\": \"tea bag\", \"material\": \"tea_leaves\", \"condition\": \"clean\", \"confidence\": 0.95}"}],
            model=m,
            response_format={"type": "json_object"}
        )
        print(f"Model {m}: SUCCESS ->", resp.choices[0].message.content.strip())
    except Exception as e:
        print(f"Model {m}: FAILED ->", e)
