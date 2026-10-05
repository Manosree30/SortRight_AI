import os
import io
import json
import base64
from PIL import Image, ImageDraw, ImageFilter
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from backend.app import app

load_dotenv()
test_client = TestClient(app)

print("=" * 65)
print("EXTRA TEST 1: PIZZA BOX CLARIFYING FLOW")
print("=" * 65)

# (1a) Initial classify
r_pizza = test_client.post("/api/classify-text", json={"text": "pizza box", "language": "en"})
data_pizza = r_pizza.json()
print("Initial /api/classify-text ('pizza box'):")
print(f"  needs_clarification: {data_pizza.get('needs_clarification')}")
print(f"  clarifying_question: {data_pizza.get('clarifying_question')}")
print(f"  condition_detected: {data_pizza.get('ai_perception', {}).get('condition_detected')}")

# (1b) Follow up with greasy=True
r_greasy = test_client.post("/api/clarify", json={
    "item": "Cardboard Pizza Box / Takeout Box",
    "material": "cardboard",
    "is_greasy_or_food_soiled": True,
    "language": "en"
})
data_greasy = r_greasy.json()
print("\nFollow-up /api/clarify (is_greasy=True):")
print(f"  Category: {data_greasy.get('category')} (Expected: organic)")
print(f"  Potential: {data_greasy.get('recycling_potential')} ({data_greasy.get('potential_label')})")
print(f"  Reason: {data_greasy.get('reason')}")
print(f"  Route Step: {data_greasy.get('steps', {}).get('route')}")

# (1c) Follow up with greasy=False
r_clean = test_client.post("/api/clarify", json={
    "item": "Cardboard Pizza Box / Takeout Box",
    "material": "cardboard",
    "is_greasy_or_food_soiled": False,
    "language": "en"
})
data_clean = r_clean.json()
print("\nFollow-up /api/clarify (is_greasy=False):")
print(f"  Category: {data_clean.get('category')} (Expected: recyclable)")
print(f"  Potential: {data_clean.get('recycling_potential')} ({data_clean.get('potential_label')})")
print(f"  Reason: {data_clean.get('reason')}")
print(f"  Route Step: {data_clean.get('steps', {}).get('route')}")

print("\n" + "=" * 65)
print("EXTRA TEST 2: BLURRY / PLAIN IMAGE TEST")
print("=" * 65)
# Create a solid grey blurry image
plain_img = Image.new("RGB", (100, 100), color=(128, 128, 128))
buf_blur = io.BytesIO()
plain_img.save(buf_blur, format="JPEG")
buf_blur.seek(0)

r_blur = test_client.post("/api/classify-image", files={"file": ("blurry.jpg", buf_blur, "image/jpeg")}, data={"language": "en"})
data_blur = r_blur.json()
print("Blurry Image Result:")
print(f"  Confidence: {data_blur.get('ai_perception', {}).get('confidence')}")
print(f"  Confidence Status: {data_blur.get('ai_perception', {}).get('confidence_status')}")
print(f"  Message: {data_blur.get('ai_perception', {}).get('confidence_message')}")
print(f"  Reason: {data_blur.get('reason')}")

print("\n" + "=" * 65)
print("EXTRA TEST 3: NONSENSE TEXT 'xyz random thing'")
print("=" * 65)
r_xyz = test_client.post("/api/classify-text", json={"text": "xyz random thing", "language": "en"})
data_xyz = r_xyz.json()
print("Nonsense Text Result:")
print(f"  Confidence Status: {data_xyz.get('ai_perception', {}).get('confidence_status')}")
print(f"  Message: {data_xyz.get('ai_perception', {}).get('confidence_message')}")
print(f"  Reason: {data_xyz.get('reason')}")

print("\n" + "=" * 65)
print("EXTRA TEST 4: TEXT 'tea bag' CONDITION DEFAULT")
print("=" * 65)
r_tea = test_client.post("/api/classify-text", json={"text": "tea bag", "language": "en"})
data_tea = r_tea.json()
print(f"  Item: {data_tea.get('item_name')}")
print(f"  Condition Detected: {data_tea.get('ai_perception', {}).get('condition_detected')} (Expected: unknown)")
print(f"  Category: {data_tea.get('category')} (Expected: organic)")
print(f"  Label: {data_tea.get('potential_label')} (Expected: Composting potential)")

print("\n" + "=" * 65)
print("EXTRA TEST 5: REAL IMAGES (PLASTIC BOTTLE & BANANA PEEL)")
print("=" * 65)

# Plastic bottle drawing
bottle_img = Image.new("RGB", (150, 200), color=(255, 255, 255))
d = ImageDraw.Draw(bottle_img)
d.rectangle([50, 40, 100, 180], fill=(64, 164, 223)) # Blue bottle body
d.rectangle([65, 20, 85, 40], fill=(20, 90, 160)) # Cap
buf_bottle = io.BytesIO()
bottle_img.save(buf_bottle, format="JPEG")
buf_bottle.seek(0)

r_bot = test_client.post("/api/classify-image", files={"file": ("bottle.jpg", buf_bottle, "image/jpeg")}, data={"language": "en"})
data_bot = r_bot.json()
print("Synthetic Plastic Bottle Image Result:")
print(f"  Item Detected: {data_bot.get('ai_perception', {}).get('item_detected')}")
print(f"  Material: {data_bot.get('ai_perception', {}).get('material_detected')}")
print(f"  Category: {data_bot.get('category')} (Expected: recyclable)")
print(f"  Special: {data_bot.get('special')}")

# Banana peel drawing
banana_img = Image.new("RGB", (150, 150), color=(255, 255, 255))
d2 = ImageDraw.Draw(banana_img)
d2.arc([30, 30, 120, 120], 30, 180, fill=(255, 215, 0), width=18) # Yellow curved peel
buf_banana = io.BytesIO()
banana_img.save(buf_banana, format="JPEG")
buf_banana.seek(0)

r_ban = test_client.post("/api/classify-image", files={"file": ("banana.jpg", buf_banana, "image/jpeg")}, data={"language": "en"})
data_ban = r_ban.json()
print("\nSynthetic Banana Peel Image Result:")
print(f"  Item Detected: {data_ban.get('ai_perception', {}).get('item_detected')}")
print(f"  Material: {data_ban.get('ai_perception', {}).get('material_detected')}")
print(f"  Category: {data_ban.get('category')}")
print(f"  Special: {data_ban.get('special')}")

print("\n" + "=" * 65)
print("SECURITY VERIFICATION")
print("=" * 65)
with open(".gitignore") as f:
    git_content = f.read()
print("Is .env in .gitignore?:", ".env" in git_content.splitlines())
