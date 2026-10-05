import sys
import io
import json
from PIL import Image, ImageDraw
from backend.app import app
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')
client = TestClient(app)

print("=" * 65)
print("ISSUE 2 REGRESSION TESTS: FULL CLASSIFIER FLOW")
print("=" * 65)

# 1. Text: rice
r_rice = client.post("/api/classify-text", json={"text": "rice", "language": "en"})
d_rice = r_rice.json()
print("1. Text 'rice':")
print(f"  Item: {d_rice.get('item_name')}, Category: {d_rice.get('category')}, Special: {d_rice.get('special')}")

# 2. Text: used battery
r_bat = client.post("/api/classify-text", json={"text": "used battery", "language": "en"})
d_bat = r_bat.json()
print("\n2. Text 'used battery':")
print(f"  Item: {d_bat.get('item_name')}, Category: {d_bat.get('category')}, Special: {d_bat.get('special')}")

# 3. Pizza box greasy & clean
r_greasy = client.post("/api/clarify", json={"item": "Pizza box", "material": "cardboard", "is_greasy_or_food_soiled": True})
print("\n3. Pizza box (greasy follow-up):")
print(f"  Category: {r_greasy.json().get('category')}, Potential: {r_greasy.json().get('recycling_potential')}")

r_clean = client.post("/api/clarify", json={"item": "Pizza box", "material": "cardboard", "is_greasy_or_food_soiled": False})
print("   Pizza box (clean follow-up):")
print(f"  Category: {r_clean.json().get('category')}, Potential: {r_clean.json().get('recycling_potential')}")

# 4. Image upload: synthetic plastic bottle
bottle_img = Image.new("RGB", (150, 200), color=(255, 255, 255))
d = ImageDraw.Draw(bottle_img)
d.rectangle([50, 40, 100, 180], fill=(64, 164, 223))
d.rectangle([65, 20, 85, 40], fill=(20, 90, 160))
buf_bottle = io.BytesIO()
bottle_img.save(buf_bottle, format="JPEG")
buf_bottle.seek(0)
r_img = client.post("/api/classify-image", files={"file": ("bottle.jpg", buf_bottle, "image/jpeg")}, data={"language": "en"})
print("\n4. Image Upload (Plastic Bottle):")
print(f"  Detected: {r_img.json().get('item_name')}, Category: {r_img.json().get('category')}")

# 5. Blurry image fallback
plain_img = Image.new("RGB", (100, 100), color=(128, 128, 128))
buf_blur = io.BytesIO()
plain_img.save(buf_blur, format="JPEG")
buf_blur.seek(0)
r_blur = client.post("/api/classify-image", files={"file": ("blur.jpg", buf_blur, "image/jpeg")})
print("\n5. Blurry image fallback:")
print(f"  Reason: {r_blur.json().get('reason')}")
