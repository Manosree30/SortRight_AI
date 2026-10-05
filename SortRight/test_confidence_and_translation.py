import sys
import json
from backend.app import format_classification_response, ai_service

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 65)
print("1. CONTROLLED TEST: CONFIDENCE THRESHOLDS")
print("=" * 65)

# Case A: Low confidence (< 0.5, e.g. 0.35)
ai_low = {
    "item": "Possible plastic scrap",
    "material": "pet_plastic",
    "condition": "unknown",
    "confidence": 0.35,
    "model_used": "controlled_test"
}
res_low = format_classification_response(ai_low)
print("\n--- Low Confidence (0.35 < 0.5) Output ---")
print(f"Confidence Status: {res_low['ai_perception']['confidence_status']}")
print(f"Confidence Message: {res_low['ai_perception']['confidence_message']}")
print(f"Reason: {res_low['reason']}")
print(f"Route Step: {res_low['steps']['route']}")

# Case B: Moderate confidence (0.5 to 0.8, e.g. 0.65)
ai_med = {
    "item": "PET Plastic Bottle",
    "material": "pet_plastic",
    "condition": "clean",
    "confidence": 0.65,
    "model_used": "controlled_test"
}
res_med = format_classification_response(ai_med)
print("\n--- Moderate Confidence (0.65 in [0.5, 0.8)) Output ---")
print(f"Confidence Status: {res_med['ai_perception']['confidence_status']}")
print(f"Confidence Message: {res_med['ai_perception']['confidence_message']}")
print(f"Category: {res_med['category']}")
print(f"Reason: {res_med['reason']}")

# Case C: High confidence (>= 0.8, e.g. 0.95)
ai_high = {
    "item": "PET Plastic Bottle",
    "material": "pet_plastic",
    "condition": "clean",
    "confidence": 0.95,
    "model_used": "controlled_test"
}
res_high = format_classification_response(ai_high)
print("\n--- High Confidence (0.95 >= 0.8) Output ---")
print(f"Confidence Status: {res_high['ai_perception']['confidence_status']}")
print(f"Confidence Message: {res_high['ai_perception']['confidence_message']}")

print("\n" + "=" * 65)
print("2. MULTILINGUAL TRANSLATION TEST (TAMIL & HINDI)")
print("=" * 65)

# Test 1: Battery Translation
battery_base = format_classification_response({
    "item": "AA battery",
    "material": "battery",
    "condition": "clean",
    "confidence": 0.95
})

print("\n--- Base Card: Used Battery (English) ---")
print(f"Item: {battery_base['item_name']}")
print(f"Category: {battery_base['category']}, Special: {battery_base['special']}")
print(f"Reason: {battery_base['reason']}")
print(f"Steps.Route: {battery_base['steps']['route']}")

# Translate Battery to Tamil
bat_tamil = ai_service.translate_result(battery_base, "ta")
print("\n--- Battery Translated to Tamil ---")
print(f"Item: {bat_tamil['item_name']}")
print(f"Category: {bat_tamil['category']} (Unchanged: {bat_tamil['category'] == battery_base['category']})")
print(f"Special: {bat_tamil['special']} (Unchanged: {bat_tamil['special'] == battery_base['special']})")
print(f"Reason: {bat_tamil['reason']}")
print(f"Steps.Route: {bat_tamil['steps']['route']}")

# Test 2: Banana Peel Translation
banana_base = format_classification_response({
    "item": "Banana peel",
    "material": "organic_waste",
    "condition": "clean",
    "confidence": 0.95
})

# Translate Banana Peel to Hindi
ban_hindi = ai_service.translate_result(banana_base, "hi")
print("\n--- Banana Peel Translated to Hindi ---")
print(f"Item: {ban_hindi['item_name']}")
print(f"Category: {ban_hindi['category']} (Unchanged: {ban_hindi['category'] == banana_base['category']})")
print(f"Potential: {ban_hindi['recycling_potential']} (Unchanged: {ban_hindi['recycling_potential'] == banana_base['recycling_potential']})")
print(f"Reason: {ban_hindi['reason']}")
print(f"Steps.Route: {ban_hindi['steps']['route']}")
