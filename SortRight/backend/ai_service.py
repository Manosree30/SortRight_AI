import os
import io
import json
import base64
import logging
from typing import Dict, Any, Optional, Tuple
from PIL import Image
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger("SortRight.AI")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b")
GROQ_BACKUP_VISION_MODEL = os.getenv("GROQ_BACKUP_VISION_MODEL", "")
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")

# Material list hint to help model return consistent keys matching rules.json
MATERIAL_HINTS = [
    "pet_plastic", "cardboard", "organic_waste", "battery", "tea_leaves",
    "aluminum", "ldpe", "glass", "coated_paper", "eggshell", "e_waste",
    "styrofoam", "sanitary_waste", "newspaper", "single_use_plastic",
    "blister_pack", "coconut_shell", "light_bulb", "cooked_food",
    "textile", "plastic_bag", "aerosol_can", "wood", "mlp"
]

SYSTEM_PROMPT_VISION = f"""You are an expert waste classification perception model.
Your ONLY task is to identify WHAT the object in the image is, its primary material, its visible condition, and your confidence level.
You DO NOT provide disposal or recycling instructions.

Materials should closely match one of these keys when applicable: {', '.join(MATERIAL_HINTS)}.
Condition MUST be one of: "clean", "dirty", "greasy", "unknown".
Confidence MUST be a float between 0.0 and 1.0. If the image is blurry, blank, unclear, ambiguous, or lacks a discernible waste item, set confidence to 0.3 or lower and item to "Unclear Object".

You MUST respond ONLY with valid JSON in this exact structure:
{{
  "item": "<short item name, e.g. PET Plastic Bottle, Pizza Box, Banana Peel>",
  "material": "<material key or best descriptive material>",
  "condition": "<clean | dirty | greasy | unknown>",
  "confidence": <float 0.0 to 1.0>
}}"""

SYSTEM_PROMPT_TEXT = f"""You are an expert waste perception assistant.
Your ONLY task is to identify WHAT the item described in text is, its primary material, condition, and confidence level.
You DO NOT provide disposal or recycling instructions.

Materials should closely match one of these keys when applicable: {', '.join(MATERIAL_HINTS)}.
Unless the user explicitly specifies a condition (e.g. 'greasy pizza box', 'clean bottle', 'dirty plate'), condition MUST default to "unknown".
Confidence MUST be a float between 0.0 and 1.0. If the text is nonsense, gibberish, or completely unrecognizable waste, set confidence to 0.2 and material to "unknown".

You MUST respond ONLY with valid JSON in this exact structure:
{{
  "item": "<standardized item name>",
  "material": "<material key or unknown>",
  "condition": "<unknown | clean | dirty | greasy>",
  "confidence": <float 0.0 to 1.0>
}}"""


class AIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def _ensure_client(self):
        if not self.client:
            self.api_key = os.getenv("GROQ_API_KEY", "")
            if self.api_key:
                self.client = Groq(api_key=self.api_key)
            else:
                raise ValueError("GROQ_API_KEY is not configured in .env file.")

    def compress_image(self, image_bytes: bytes, max_size: int = 1024, quality: int = 80) -> Tuple[str, str]:
        """
        Resizes and compresses image in memory to avoid payload size limits. Never saves to disk.
        """
        img = Image.open(io.BytesIO(image_bytes))
        
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        width, height = img.size
        if max(width, height) > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=quality, optimize=True)
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{img_b64}"
        return data_url, img_b64

    def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Sends compressed image to Groq Vision model with graceful fallback and structured JSON output.
        """
        self._ensure_client()
        data_url, _ = self.compress_image(image_bytes)

        models_to_try = [GROQ_VISION_MODEL]
        if GROQ_BACKUP_VISION_MODEL and GROQ_BACKUP_VISION_MODEL != GROQ_VISION_MODEL and GROQ_BACKUP_VISION_MODEL.strip():
            models_to_try.append(GROQ_BACKUP_VISION_MODEL.strip())

        last_error = None
        for model_name in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_VISION},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analyze this waste item and output structured JSON only."},
                                {"type": "image_url", "image_url": {"url": data_url}}
                            ]
                        }
                    ],
                    model=model_name,
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                raw_content = response.choices[0].message.content.strip()
                data = json.loads(raw_content)
                return {
                    "success": True,
                    "item": data.get("item", "Unidentified Item"),
                    "material": data.get("material", "unknown"),
                    "condition": data.get("condition", "unknown"),
                    "confidence": float(data.get("confidence", 0.7)),
                    "model_used": model_name
                }
            except Exception as e:
                logger.warning(f"Vision model {model_name} failed: {e}")
                last_error = str(e)

        return {
            "success": False,
            "error_type": "VISION_API_UNAVAILABLE",
            "message": f"Vision analysis is currently unavailable ({last_error}). Please type the item name below.",
            "item": "Unknown",
            "material": "unknown",
            "condition": "unknown",
            "confidence": 0.0
        }

    def analyze_text(self, text_input: str) -> Dict[str, Any]:
        """
        Extracts item, material, condition (defaulting to unknown unless stated), and confidence from user text.
        """
        self._ensure_client()
        query = (text_input or "").strip()
        if not query:
            return {
                "success": False,
                "message": "Please enter an item name.",
                "confidence": 0.0
            }

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_TEXT},
                    {"role": "user", "content": f"Extract waste item details for: \"{query}\""}
                ],
                model=GROQ_TEXT_MODEL,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            raw_content = response.choices[0].message.content.strip()
            data = json.loads(raw_content)
            return {
                "success": True,
                "item": data.get("item", query),
                "material": data.get("material", "unknown"),
                "condition": data.get("condition", "unknown"),
                "confidence": float(data.get("confidence", 0.95)),
                "model_used": GROQ_TEXT_MODEL
            }
        except Exception as e:
            logger.warning(f"Text model {GROQ_TEXT_MODEL} failed: {e}")
            return {
                "success": True,
                "item": query,
                "material": query.lower().replace(" ", "_"),
                "condition": "unknown",
                "confidence": 0.7,
                "model_used": "heuristic_fallback"
            }

    def translate_result(self, card_data: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """
        Translates ONLY display text into Tamil or Hindi.
        Uses accurate, commonly used technical terms (e.g. 'lead' -> ஈயம், 'groundwater' -> நிலத்தடி நீர்).
        Category, special handling, potential, and rules logic remain 100% deterministic and unchanged.
        """
        if not target_language or target_language.lower() in ("en", "english"):
            merged = dict(card_data)
            merged["translation_note"] = None
            merged["language"] = "en"
            return merged

        lang_name = "Tamil" if target_language.lower() in ("ta", "tamil") else "Hindi"
        
        self._ensure_client()
        try:
            prompt = f"""You are a professional translator for municipal waste management in {lang_name}.
Translate ONLY the display texts in this JSON waste classification card to natural, commonly spoken {lang_name}.
Use standard, commonly used words for technical terms (e.g. in Tamil, 'lead' is 'ஈயம்', 'groundwater' is 'நிலத்தடி நீர்', 'mercury' is 'பாதரசம்', 'compost' is 'மக்கும் உரம்', 'cadmium' is 'காட்மியம்'). Keep chemical and material names accurate.

Keep category, special, and recycling_potential UNCHANGED. Translate only 'item_name', 'reason', and 'steps' (prepare, separate, route).

Input JSON:
{json.dumps({
    "item_name": card_data.get("item_name"),
    "reason": card_data.get("reason"),
    "steps": card_data.get("steps"),
    "clarifying_question": card_data.get("clarifying_question")
}, ensure_ascii=False)}

Respond ONLY with valid JSON matching the exact structure."""

            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are an expert waste management translator for {lang_name}."},
                    {"role": "user", "content": prompt}
                ],
                model=GROQ_TEXT_MODEL,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            translated_dict = json.loads(response.choices[0].message.content.strip())
            
            merged = dict(card_data)
            if "item_name" in translated_dict:
                merged["item_name"] = translated_dict["item_name"]
            if "reason" in translated_dict:
                merged["reason"] = translated_dict["reason"]
            if "steps" in translated_dict:
                merged["steps"] = translated_dict["steps"]
            if "clarifying_question" in translated_dict:
                merged["clarifying_question"] = translated_dict["clarifying_question"]
            
            # Add translation note in the selected language and English
            if target_language.lower() in ("ta", "tamil"):
                merged["translation_note"] = "இயந்திரத்தால் மொழிபெயர்க்கப்பட்டது. உள்ளூர் வழிகாட்டுதலுடன் சரிபார்க்கவும். / Machine-translated. Please verify with local guidance."
            else:
                merged["translation_note"] = "मशीन द्वारा अनुवादित। कृपया स्थानीय मार्गदर्शन से सत्यापित करें। / Machine-translated. Please verify with local guidance."

            merged["language"] = target_language
            return merged
        except Exception as e:
            logger.warning(f"Translation to {target_language} failed: {e}")
            merged = dict(card_data)
            merged["translation_note"] = "Machine-translated. Please verify with local guidance."
            return merged


# Global singleton
ai_service = AIService()
