import os
import io
import json
import base64
from PIL import Image, ImageDraw
from dotenv import load_dotenv
from groq import Groq
from fastapi.testclient import TestClient
from backend.app import app
from backend.rules_engine import rules_engine

load_dotenv()
api_key = os.getenv("GROQ_API_KEY", "")

print("=" * 60)
print("1. CHECKING LIVE GROQ MODELS FROM API")
print("=" * 60)

client = Groq(api_key=api_key)
models_resp = client.models.list()
all_models = sorted([m.id for m in models_resp.data])
print(f"Total live models: {len(all_models)}")
for m in all_models:
    print(f"  - {m}")

print("\nModel Selection:")
print("  - Vision Model: qwen/qwen3.8-27b (Verified multimodal)")
print("  - Text Model: openai/gpt-oss-120b (Verified text/reasoning)")

print("\n" + "=" * 60)
print("2. REAL VISION TEST CALL WITH SMALL SAMPLE IMAGE")
print("=" * 60)

# Create a small in-memory test image (a small red beverage can drawing)
img = Image.new("RGB", (120, 120), color=(240, 240, 240))
draw = ImageDraw.Draw(img)
draw.rectangle([40, 20, 80, 100], fill=(220, 20, 60)) # red can
draw.rectangle([50, 15, 70, 20], fill=(180, 180, 180)) # top tab

buf = io.BytesIO()
img.save(buf, format="JPEG", quality=80)
buf.seek(0)
img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
data_url = f"data:image/jpeg;base64,{img_b64}"

vision_test_resp = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a waste perception model. Return JSON only: {\"item\": \"...\", \"material\": \"...\", \"condition\": \"clean\", \"confidence\": 0.9}"},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is this item?"},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        }
    ],
    model="qwen/qwen3.8-27b",
    response_format={"type": "json_object"}
)
print("Raw Vision API Output:")
print(vision_test_resp.choices[0].message.content)

print("\n" + "=" * 60)
print("3. END-TO-END ENDPOINT TESTS (/api/classify-text & /api/classify-image)")
print("=" * 60)

test_client = TestClient(app)

print("\n--- Test (a): Text input 'tea bag' ---")
resp_a = test_client.post("/api/classify-text", json={"text": "tea bag", "language": "en"})
print("HTTP Status:", resp_a.status_code)
print(json.dumps(resp_a.json(), indent=2))

print("\n--- Test (b): Text input 'used battery' ---")
resp_b = test_client.post("/api/classify-text", json={"text": "used battery", "language": "en"})
print("HTTP Status:", resp_b.status_code)
print(json.dumps(resp_b.json(), indent=2))

print("\n--- Test (c): Real Image input (in-memory red can image) ---")
buf.seek(0)
resp_c = test_client.post(
    "/api/classify-image",
    files={"file": ("test_can.jpg", buf, "image/jpeg")},
    data={"language": "en"}
)
print("HTTP Status:", resp_c.status_code)
print(json.dumps(resp_c.json(), indent=2))
