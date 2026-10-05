import os
import json
import base64
import io
from PIL import Image, ImageDraw
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

print(f"Testing Groq API with Key: {api_key[:10]}...")

client = Groq(api_key=api_key)

try:
    models_resp = client.models.list()
    model_ids = sorted([m.id for m in models_resp.data])
    print(f"\n=== Total Models in Live Groq Account: {len(model_ids)} ===")
    for m in model_ids:
        print(f" - {m}")
except Exception as e:
    print(f"Error fetching model list: {e}")
    exit(1)

# Look for vision models
vision_candidates = [m for m in model_ids if "vision" in m or "qwen" in m or "vl" in m or "llama-3.2" in m]
print(f"\nVision-related candidates found: {vision_candidates}")

# Create a small synthetic test image (a green bottle drawing) in base64
img = Image.new("RGB", (100, 100), color=(240, 240, 240))
draw = ImageDraw.Draw(img)
draw.rectangle([35, 20, 65, 90], fill=(34, 139, 34)) # green bottle shape
draw.rectangle([45, 10, 55, 20], fill=(200, 200, 200)) # cap

buffered = io.BytesIO()
img.save(buffered, format="JPEG", quality=85)
img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
image_data_url = f"data:image/jpeg;base64,{img_b64}"

print("\n=== Testing Live Model Calls ===")

# Test text model
text_model_to_test = "llama-3.3-70b-versatile" if "llama-3.3-70b-versatile" in model_ids else model_ids[0]
print(f"\n1. Testing Text Model: {text_model_to_test}...")
try:
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "Respond with JSON only: {\"status\": \"ok\", \"item\": \"test\"}"}],
        model=text_model_to_test,
        response_format={"type": "json_object"}
    )
    print(" Text model response:", chat_completion.choices[0].message.content)
except Exception as e:
    print(f" Text model failed: {e}")

# Test vision models in order of candidate preference
selected_vision_model = None
backup_vision_model = None

for candidate in vision_candidates:
    print(f"\n2. Testing Vision Candidate: {candidate}...")
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image? Respond strictly in JSON: {\"item\": \"...\", \"material\": \"...\", \"condition\": \"clean\", \"confidence\": 0.9}"},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                }
            ],
            model=candidate,
            response_format={"type": "json_object"}
        )
        print(f" SUCCESS with {candidate}!")
        print(" Vision response:", chat_completion.choices[0].message.content)
        if not selected_vision_model:
            selected_vision_model = candidate
        elif not backup_vision_model:
            backup_vision_model = candidate
    except Exception as e:
        print(f" Vision candidate {candidate} failed: {e}")

print("\n=== SUMMARY OF LIVE VERIFICATION ===")
print(f"Selected Primary Vision Model: {selected_vision_model}")
print(f"Selected Backup Vision Model: {backup_vision_model}")
print(f"Selected Text Model: {text_model_to_test}")
