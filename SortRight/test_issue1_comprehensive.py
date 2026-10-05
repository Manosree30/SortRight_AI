import sys
import io
import json
from PIL import Image, ImageDraw
from backend.rules_engine import rules_engine
from backend.app import app, format_classification_response, ai_service
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')
client = TestClient(app)

print("=" * 75)
print("COMPREHENSIVE TEST: ALL RULES & FALLBACKS WITH TYPED NAMES")
print("=" * 75)

test_cases = [
    # (Input Name, Expected Rule ID, Expected Category, Expected Special)
    ("rice", "food_waste_cooked", "organic", False),
    ("leftover rice", "food_waste_cooked", "organic", False),
    ("curry", "food_waste_cooked", "organic", False),
    ("apple core", "banana_peel", "organic", False),
    ("banana peel", "banana_peel", "organic", False),
    ("banana peels", "banana_peel", "organic", False),
    ("tea bag", "tea_bag", "organic", False),
    ("used tea bags", "tea_bag", "organic", False),
    ("eggshell", "egg_shells", "organic", False),
    ("egg shells", "egg_shells", "organic", False),
    ("coconut shell", "coconut_shell", "organic", False),
    ("nariyal chilka", "coconut_shell", "organic", False),
    ("wooden chopstick", "wooden_stick", "organic", False),
    ("ice cream stick", "wooden_stick", "organic", False),
    ("coke can", "aluminum_can", "recyclable", False),
    ("aluminum can", "aluminum_can", "recyclable", False),
    ("plastic water bottle", "pet_bottle", "recyclable", False),
    ("mineral water bottle", "pet_bottle", "recyclable", False),
    ("curd packet", "milk_pouch", "recyclable", False),
    ("milk pouch", "milk_pouch", "recyclable", False),
    ("pickle jar", "glass_bottle", "recyclable", False),
    ("glass bottle", "glass_bottle", "recyclable", False),
    ("shipping box", "cardboard_box", "recyclable", False),
    ("amazon box", "cardboard_box", "recyclable", False),
    ("newspaper", "newspaper", "recyclable", False),
    ("notebook", "newspaper", "recyclable", False),
    ("old shirt", "clothes_textile", "recyclable", False),
    ("fabric scrap", "clothes_textile", "recyclable", False),
    ("coffee cup", "paper_cup", "other", False),
    ("paper cup", "paper_cup", "other", False),
    ("thermocol", "styrofoam_packaging", "other", False),
    ("styrofoam cup", "styrofoam_packaging", "other", False),
    ("chips packet", "snack_wrapper", "other", False),
    ("biscuit packet", "snack_wrapper", "other", False),
    ("plastic straw", "plastic_straw", "other", False),
    ("single-use straw", "plastic_straw", "other", False),
    ("polythene bag", "plastic_carry_bag", "other", False),
    ("plastic carry bag", "plastic_carry_bag", "other", False),
    ("medicine strip", "medicine_strip", "other", False),
    ("blister pack", "medicine_strip", "other", False),
    ("aa battery", "battery", "other", True),
    ("lithium battery", "battery", "other", True),
    ("laptop", "e_waste_device", "other", True),
    ("charging cable", "e_waste_device", "other", True),
    ("CFL bulb", "light_bulb", "other", True),
    ("tube light", "light_bulb", "other", True),
    ("deodorant can", "spray_can", "other", True),
    ("spray can", "spray_can", "other", True),
    ("sanitary pad", "sanitary_waste", "other", True),
    ("diaper", "sanitary_waste", "other", True),
    ("kitchen waste", "generic_organic", "organic", False),
    ("cardboard scrap", "generic_paper", "recyclable", False),
    ("rigid plastic", "generic_plastic", "recyclable", False),
    ("scrap metal", "generic_metal", "recyclable", False),
    ("broken electronics", "generic_ewaste", "other", True),
]

print(f"{'Input Name':<24} | {'Rule ID':<20} | {'Card Title':<32} | {'Category':<10} | {'Special':<7} | {'Correct?'}")
print("-" * 115)

all_passed = True
for name, exp_id, exp_cat, exp_special in test_cases:
    res = rules_engine.evaluate(item=name, material="unknown")
    actual_id = res.get("rule_id")
    actual_title = res.get("item_name")
    actual_cat = res.get("category")
    actual_special = res.get("special")
    
    is_correct = (actual_id == exp_id and actual_cat == exp_cat and actual_special == exp_special)
    if not is_correct:
        all_passed = False
    
    status_str = "YES" if is_correct else "NO (FAIL)"
    print(f"{name:<24} | {actual_id:<20} | {actual_title[:32]:<32} | {actual_cat:<10} | {str(actual_special):<7} | {status_str}")

print("\n" + "=" * 75)
print("NEGATIVE TESTS (Must NOT match unintended keywords)")
print("=" * 75)

neg_cases = [
    ("price", "rice"),            # 'price' should NOT match 'rice'
    ("scan", "can"),              # 'scan' should NOT match 'can'
    ("egg roll", "egg_shells"),   # 'egg roll' should NOT match 'egg_shells'
    ("xyz random thing", "any")   # Should return is_not_sure
]

for name, avoid_target in neg_cases:
    res = rules_engine.evaluate(item=name, material="unknown")
    rule_id = res.get("rule_id")
    is_not_sure = res.get("is_not_sure", False)
    
    if name == "xyz random thing":
        passed = is_not_sure
        result_desc = "Correctly flagged is_not_sure" if passed else f"Incorrectly matched {rule_id}"
    elif name == "egg roll":
        passed = (rule_id != "egg_shells")
        result_desc = f"Correctly avoided egg_shells (matched {rule_id})" if passed else "FAILED: Matched egg_shells"
    else:
        passed = (avoid_target not in rule_id)
        result_desc = f"Correctly avoided {avoid_target} (got {rule_id})" if passed else f"FAILED: Matched {rule_id}"
    
    status = "YES" if passed else "NO (FAIL)"
    print(f"Negative test '{name}': {result_desc} -> Correct: {status}")

print("\n" + "=" * 75)
print("RE-RUN REGRESSION TESTS")
print("=" * 75)

# 1. Pizza box greasy & clean
r_greasy = client.post("/api/clarify", json={"item": "Pizza box", "material": "cardboard", "is_greasy_or_food_soiled": True})
print("Pizza box (greasy):", r_greasy.json().get("category"), "(Expected: organic)")

r_clean = client.post("/api/clarify", json={"item": "Pizza box", "material": "cardboard", "is_greasy_or_food_soiled": False})
print("Pizza box (clean):", r_clean.json().get("category"), "(Expected: recyclable)")

# 2. Blurry image fallback
plain_img = Image.new("RGB", (100, 100), color=(128, 128, 128))
buf_blur = io.BytesIO()
plain_img.save(buf_blur, format="JPEG")
buf_blur.seek(0)
r_blur = client.post("/api/classify-image", files={"file": ("blur.jpg", buf_blur, "image/jpeg")})
print("Blurry image fallback message:", r_blur.json().get("reason"))

# 3. Used battery
r_bat = client.post("/api/classify-text", json={"text": "used battery", "language": "en"})
print("Battery category & special:", r_bat.json().get("category"), "Special:", r_bat.json().get("special"))
