import json
import os
import re
from typing import Dict, Any, Optional, List, Tuple

RULES_PATH = os.path.join(os.path.dirname(__file__), "rules.json")

class RulesEngine:
    def __init__(self, rules_file: str = RULES_PATH):
        self.rules_file = rules_file
        self.rules_data = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        with open(self.rules_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate(
        self,
        item: str,
        material: str,
        condition: str = "clean",
        user_clarification_response: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Deterministically evaluates item, material, and condition against the rules database.
        
        MATCH ORDER:
        1. Whole-word keyword matching on item text against rule keywords (longest match wins).
        2. Specific material key match on AI's material attribute.
        3. Generic fallback rules (e.g. generic_organic, generic_plastic) if material is generic.
        4. If nothing matches, returns is_not_sure fallback.
        """
        item_text = (item or "").strip().lower()
        material_key = (material or "").strip().lower().replace(" ", "_")
        condition_lower = (condition or "clean").strip().lower()

        matched_rule = None
        rules_list = self.rules_data.get("rules", [])

        # ---------------------------------------------------------
        # STEP 1: Whole-word keyword match (Longest match wins)
        # ---------------------------------------------------------
        if item_text:
            candidate_matches: List[Tuple[int, bool, Dict[str, Any]]] = []
            for rule in rules_list:
                for kw in rule.get("keywords", []):
                    kw_clean = kw.lower().strip()
                    # Whole-word regex match: prevents "price" matching "rice", "scan" matching "can"
                    pattern = r'\b' + re.escape(kw_clean) + r'\b'
                    if re.search(pattern, item_text):
                        is_exact = (kw_clean == item_text)
                        candidate_matches.append((len(kw_clean), is_exact, rule))

            if candidate_matches:
                # Sort: (1) Exact full match first, (2) Longest matched keyword length
                candidate_matches.sort(key=lambda x: (x[1], x[0]), reverse=True)
                matched_rule = candidate_matches[0][2]

        # ---------------------------------------------------------
        # STEP 2: Specific Material Key lookup (if no keyword matched)
        # ---------------------------------------------------------
        if not matched_rule and material_key and material_key != "unknown":
            # First check non-generic rules
            for rule in rules_list:
                if not rule.get("id", "").startswith("generic_"):
                    if material_key in [k.lower() for k in rule.get("material_keys", [])]:
                        matched_rule = rule
                        break
                    if rule.get("id", "").lower() == material_key:
                        matched_rule = rule
                        break

        # ---------------------------------------------------------
        # STEP 3: Generic Material Fallback lookup (e.g. generic_organic)
        # ---------------------------------------------------------
        if not matched_rule and material_key and material_key != "unknown":
            for rule in rules_list:
                if rule.get("id", "").startswith("generic_"):
                    if material_key in [k.lower() for k in rule.get("material_keys", [])]:
                        matched_rule = rule
                        break

        # ---------------------------------------------------------
        # STEP 4: If no rule matches, return is_not_sure fallback
        # ---------------------------------------------------------
        if not matched_rule:
            fallback = self.rules_data.get("default_fallback", {})
            return {
                "matched": False,
                "is_not_sure": True,
                "rule_id": "not_sure_fallback",
                "item_name": item or "Unknown Item",
                "category": "other",
                "special": False,
                "recycling_potential": "None",
                "potential_label": "Recycling potential",
                "reason": "I'm not sure. Please retake the photo or describe the item.",
                "steps": {
                    "prepare": "Check lighting and item clarity.",
                    "separate": "Verify with local municipal waste guidelines.",
                    "route": "Please retake the photo or type the item name in the text box."
                },
                "needs_clarification": False,
                "clarifying_question": None,
                "city": self.rules_data.get("city", "Coimbatore (Sample City)"),
                "disclaimer": self.rules_data.get("disclaimer", "Sample rules. Verify with local municipality."),
                "source": self.rules_data.get("source", "Prototype sample rules"),
                "last_updated": self.rules_data.get("last_updated", "2026-10-05")
            }

        # Handle condition branches & clarifying questions
        needs_clarification = False
        clarifying_q = matched_rule.get("clarifying_question")
        
        if user_clarification_response is not None:
            effective_condition = "greasy" if user_clarification_response else "clean"
        else:
            effective_condition = condition_lower

        category = matched_rule.get("category", "other")
        special = matched_rule.get("special", False)
        recycling_potential = matched_rule.get("recycling_potential", "Medium")
        reason = matched_rule.get("reason", "")
        steps = matched_rule.get("steps", {})

        if "condition_branches" in matched_rule:
            branches = matched_rule["condition_branches"]
            if user_clarification_response is not None:
                branch = branches.get(effective_condition, branches.get("clean", {}))
                category = branch.get("category", category)
                special = branch.get("special", special)
                recycling_potential = branch.get("recycling_potential", recycling_potential)
                reason = branch.get("reason", reason)
                steps = branch.get("steps", steps)
                needs_clarification = False
            elif condition_lower in branches:
                branch = branches[condition_lower]
                category = branch.get("category", category)
                special = branch.get("special", special)
                recycling_potential = branch.get("recycling_potential", recycling_potential)
                reason = branch.get("reason", reason)
                steps = branch.get("steps", steps)
                if condition_lower in ["dirty", "unknown"]:
                    needs_clarification = True
            elif clarifying_q:
                needs_clarification = True

        elif "condition_overrides" in matched_rule:
            overrides = matched_rule["condition_overrides"]
            if effective_condition in overrides:
                override = overrides[effective_condition]
                if "steps" in override:
                    steps = override["steps"]
                if "reason" in override:
                    reason = override["reason"]

        if category not in ("recyclable", "organic", "other"):
            category = "other"

        potential_label = "Composting potential" if category == "organic" else "Recycling potential"

        return {
            "matched": True,
            "is_not_sure": False,
            "rule_id": matched_rule.get("id"),
            "item_name": matched_rule.get("name"),
            "category": category,
            "special": special,
            "recycling_potential": recycling_potential,
            "potential_label": potential_label,
            "reason": reason,
            "steps": steps,
            "needs_clarification": needs_clarification,
            "clarifying_question": clarifying_q if needs_clarification else None,
            "city": self.rules_data.get("city", "Coimbatore (Sample City)"),
            "disclaimer": self.rules_data.get("disclaimer", "Sample rules. Verify with local municipality."),
            "source": self.rules_data.get("source", "Prototype sample rules"),
            "last_updated": self.rules_data.get("last_updated", "2026-10-05")
        }

# Global singleton
rules_engine = RulesEngine()
