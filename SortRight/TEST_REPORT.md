# 📊 SortRight - Prototype Test Report

> **Disclosure**: Automated preliminary tests conducted during development used synthetic vector drawings and programmatic scripts. The table below is left intentionally empty for manual verification with **real physical photos** taken on real devices.

---

## 📋 Real-Photo Test Verification Table (To Be Filled By User)

| # | Item Description | Input Method (Camera / Upload / Text) | Condition (Clean / Dirty / Greasy / Unknown) | Expected Category (Recyclable / Organic / Other / Special) | Actual System Output | Correct? (Yes / No) | Notes / Behavior Observed |
|---|------------------|---------------------------------------|----------------------------------------------|-----------------------------------------------------------|----------------------|---------------------|---------------------------|
| 1 | Clean PET Bottle |                                       | Clean                                        | Recyclable (Dry bin)                                      |                      |                     |                           |
| 2 | Banana Peel      |                                       | Clean                                        | Organic (Wet bin)                                         |                      |                     |                           |
| 3 | Used AA Battery  |                                       | Unknown                                      | Special (Hazardous / E-Waste)                             |                      |                     |                           |
| 4 | Pizza Box        |                                       | Greasy / Food-soiled                         | Organic (Wet bin / Compost)                               |                      |                     | Should trigger Yes/No Q   |
| 5 | Blurry Image     |                                       | Unclear                                      | Fallback ("I'm not sure")                                 |                      |                     | Confidence < 0.5          |
| 6 | Text: "tea bag"  | Text                                  | Unknown                                      | Organic (Wet bin)                                         |                      |                     | Composting potential      |
| 7 |                  |                                       |                                              |                                                           |                      |                     |                           |
| 8 |                  |                                       |                                              |                                                           |                      |                     |                           |

---

## 🔍 Core Deterministic Invariants Checked
- [x] Separation of AI Perception from Deterministic Rules (`rules.json`).
- [x] Special Handling Flag (`special === true`) is the single source of truth for red badge styling.
- [x] Organic items display "Composting potential" instead of "Recycling potential".
- [x] Confidence < 0.5 or unclassified item returns "I'm not sure. Please retake the photo or describe the item."
- [x] Clarifying Question handles food-soiled vs. clean conditions deterministically.
- [x] Multilingual display translation preserves all underlying category and rules values.
- [x] Browser `localStorage` history stores text metadata only (zero image data).
