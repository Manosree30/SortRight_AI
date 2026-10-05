from fastapi.testclient import TestClient
from backend.app import app
import io
from PIL import Image, ImageDraw

client = TestClient(app)

print("1. Testing /api/health...")
r = client.get("/api/health")
print("Health:", r.status_code, r.json())

print("\n2. Testing /api/classify-text with 'tea bag'...")
r = client.post("/api/classify-text", json={"text": "tea bag", "language": "en"})
data = r.json()
print("Text classify:", r.status_code, "Item:", data.get("item_name"), "Category:", data.get("category"), "Steps:", data.get("steps"))

print("\n3. Testing /api/clarify with pizza box greasy=True...")
r = client.post("/api/clarify", json={"item": "Pizza box", "material": "cardboard", "is_greasy_or_food_soiled": True})
print("Greasy pizza box category:", r.json().get("category"), "Potential:", r.json().get("recycling_potential"))

print("\n4. Testing /api/clarify with pizza box greasy=False...")
r = client.post("/api/clarify", json={"item": "Pizza box", "material": "cardboard", "is_greasy_or_food_soiled": False})
print("Clean pizza box category:", r.json().get("category"), "Potential:", r.json().get("recycling_potential"))

print("\n5. Testing /api/classify-image with synthetic image...")
img = Image.new("RGB", (120, 120), color=(250, 250, 250))
draw = ImageDraw.Draw(img)
draw.rectangle([30, 20, 90, 100], fill=(220, 20, 60)) # red item
buf = io.BytesIO()
img.save(buf, format="JPEG")
buf.seek(0)

r = client.post("/api/classify-image", files={"file": ("test.jpg", buf, "image/jpeg")}, data={"language": "en"})
print("Image classify status:", r.status_code, "Output:", r.json().get("item_name", r.json().get("message")))
