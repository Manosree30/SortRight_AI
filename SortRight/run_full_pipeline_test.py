import sys
import io
import json
from PIL import Image, ImageDraw
from backend.app import app, format_classification_response, ai_service
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')
client = TestClient(app)

print("=" * 85)
print("FULL END-TO-END PIPELINE TEST (/api/classify-text WITH REAL AI INFERENCE)")
print("=" * 85)

test_inputs = [
    "rice",
    "apple core",
    "curry",
    "tea bag",
    "plastic bottle",
    "coke can",
    "laptop",
    "used battery",
    "price",
    "scan",
    "xyz random thing"
]

print(f"{'Input':<18} | {'AI Item':<22} | {'AI Material':<16} | {'Rule ID':<18} | {'Card Title':<28} | {'Category':<10} | {'Special'}")
print("-" * 125)

for inp in test_inputs:
    r = client.post("/api/classify-text", json={"text": inp, "language": "en"})
    data = r.json()
    
    ai_item = data.get("ai_perception", {}).get("item_detected", "-")
    ai_mat = data.get("ai_perception", {}).get("material_detected", "-")
    rule_id = data.get("rule_id", "-")
    card_title = data.get("item_name", "-")
    cat = data.get("category", "-")
    special = str(data.get("special", False))
    
    print(f"{inp:<18} | {ai_item[:22]:<22} | {ai_mat[:16]:<16} | {rule_id:<18} | {card_title[:28]:<28} | {cat:<10} | {special}")

print("\n" + "=" * 85)
print("REAL IMAGE TEST: PLASTIC BOTTLE")
print("=" * 85)
bottle_img = Image.new("RGB", (150, 200), color=(255, 255, 255))
d = ImageDraw.Draw(bottle_img)
d.rectangle([50, 40, 100, 180], fill=(64, 164, 223))
d.rectangle([65, 20, 85, 40], fill=(20, 90, 160))
buf_bottle = io.BytesIO()
bottle_img.save(buf_bottle, format="JPEG")
buf_bottle.seek(0)

r_bot = client.post("/api/classify-image", files={"file": ("bottle.jpg", buf_bottle, "image/jpeg")}, data={"language": "en"})
data_bot = r_bot.json()
print("Plastic Bottle Image Result:")
print("  Detected Item:", data_bot.get("ai_perception", {}).get("item_detected"))
print("  Detected Material:", data_bot.get("ai_perception", {}).get("material_detected"))
print("  Rule ID:", data_bot.get("rule_id"))
print("  Card Title:", data_bot.get("item_name"))
print("  Category:", data_bot.get("category"))
print("  Special:", data_bot.get("special"))

print("\n" + "=" * 85)
print("TAMIL & HINDI TRANSLATIONS VERIFICATION")
print("=" * 85)

# Battery in Tamil
base_battery = format_classification_response({
    "item": "used battery",
    "material": "battery_cell",
    "condition": "unknown",
    "confidence": 0.95
})
bat_tamil = ai_service.translate_result(base_battery, "ta")
print("\n1. Battery in Tamil (தமிழ்):")
print("  Item Name:", bat_tamil["item_name"])
print("  Category:", bat_tamil["category"], "(Unchanged)")
print("  Special Flag:", bat_tamil["special"], "(Unchanged)")
print("  Reason:", bat_tamil["reason"])
print("  Route:", bat_tamil["steps"]["route"])
print("  Translation Note:", bat_tamil.get("translation_note"))

# Fruit & Veg scraps in Hindi
base_banana = format_classification_response({
    "item": "banana peel",
    "material": "fruit_peel",
    "condition": "unknown",
    "confidence": 0.95
})
ban_hindi = ai_service.translate_result(base_banana, "hi")
print("\n2. Fruit Scraps (Banana Peel) in Hindi (हिन्दी):")
print("  Item Name:", ban_hindi["item_name"])
print("  Category:", ban_hindi["category"], "(Unchanged)")
print("  Special Flag:", ban_hindi["special"], "(Unchanged)")
print("  Reason:", ban_hindi["reason"])
print("  Route:", ban_hindi["steps"]["route"])
print("  Translation Note:", ban_hindi.get("translation_note"))
