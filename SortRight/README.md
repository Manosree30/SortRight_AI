# ♻️ SortRight - AI Waste Classification Assistant

A hackathon MVP for intelligent waste segregation that **decouples AI perception from deterministic municipal rules**.

---

## 💡 Core Design Principle
Generative AI models should **never hallucinate disposal or recycling rules**. 
- **AI Perception Layer (Groq)**: Analyzes the image or text to extract *item name*, *material*, *condition*, and *confidence*.
- **Deterministic Rules Engine (`rules.json`)**: Strictly maps the item and condition to the correct bin, special-handling flags, recycling/composting potential, and step-by-step actions (Prepare / Separate / Route).

---

## 🚀 Features Built
1. **Three Input Methods**:
   - 📸 **Camera (Two Modes)**:
     - **Native Mobile Camera** (`<input capture="environment">`): Works directly on mobile browsers over both HTTP and HTTPS.
     - **Live WebRTC Viewfinder**: Available when served on `localhost` or via HTTPS tunnel.
   - 📁 **File Upload**: Drag-and-drop or file selector with automatic in-memory compression.
   - ✍️ **Text Input**: Direct item query with fast attribute extraction.
2. **Deterministic Rules Engine**:
   - 25+ common materials & items calibrated for Indian municipal segregation practice (Coimbatore sample).
   - Condition branches (e.g., greasy pizza box $\to$ organic/wet stream, clean pizza box $\to$ dry recyclables).
3. **Color-Coded Result Card**:
   - 🚨 **Red**: Special Handling / Hazardous / E-Waste (evaluated via `special: true` as single source of truth).
   - ♻️ **Green**: Recyclable (Dry stream).
   - 🌱 **Brown**: Organic / Wet stream (shows "Composting potential").
   - 🗑️ **Grey**: Reject / Other non-recyclable stream.
4. **Confidence Fallback**:
   - Confidence < 0.5 or unclassified item $\to$ `"I'm not sure. Please retake the photo or describe the item."` (no false guessing).
   - Confidence 0.5 to 0.8 $\to$ Yellow `"Please verify"` note.
5. **Clarifying Question Modal**:
   - Triggers for ambiguous items (e.g., pizza boxes) asking *"Is the cardboard greasy or food-soiled?"* with Yes/No buttons that deterministically re-evaluate the card.
6. **Multilingual Support**:
   - English / Tamil (தமிழ்) / Hindi (हिन्दी) dropdown translating display text without altering rule logic.
7. **Local Scan History**:
   - Persisted in browser `localStorage` (stores text metadata only, zero images).
8. **Simulated Municipality Dashboard**:
   - Visual charts (Waste Mix, Contamination Hotspots, E-Waste Trends) using Chart.js, clearly marked with *"Simulated demo data. Not real scan data."*

---

## 🛠️ Tech Stack
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pillow (in-memory image processing), python-dotenv
- **AI Model / Vision**: Groq API (`qwen/qwen3.8-27b` for multimodal vision, `openai/gpt-oss-120b` for text)
- **Frontend**: Vanilla HTML5, CSS3 (modern glassmorphic design system), JavaScript (ES6+), Chart.js

---

## 📦 Quickstart & Running Locally

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment
Verify `.env` has your `GROQ_API_KEY`:
```ini
GROQ_API_KEY=your_groq_api_key_here
GROQ_VISION_MODEL=qwen/qwen3.8-27b
GROQ_TEXT_MODEL=openai/gpt-oss-120b
PORT=8000
HOST=0.0.0.0
```

### 3. Start the Server
```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📱 How to Test on Your Mobile Phone

### Option A: Standard Direct Access (Native Camera)
Modern mobile browsers (Chrome / Safari / iOS) restrict WebRTC `getUserMedia` live camera streaming to secure HTTPS origins or `localhost`. SortRight includes a **native camera capture fallback** that works immediately over HTTP:
1. Connect your phone and computer to the **same Wi-Fi**.
2. Find your computer's local IP address (in PowerShell, run `ipconfig` and find `IPv4 Address`, e.g., `192.168.1.45`).
3. On your phone's browser, open:
   ```
   http://<YOUR_COMPUTER_IP>:8000
   ```
4. Tap **📱 Take Photo** to open your mobile camera app directly!

### Option B: HTTPS Tunnel for Live WebRTC Viewfinder
If you want to test the live continuous WebRTC camera viewfinder on your phone, create a quick HTTPS tunnel:
```bash
# Using Cloudflare Tunnel (recommended, no account needed):
npx cloudflared tunnel --url http://localhost:8000

# Or using ngrok:
ngrok http 8000
```
Open the generated `https://...` URL on your phone to get full access to the live WebRTC viewfinder.

---

## 🔐 Staff Portal Authentication & Demo Mode

The application includes an authenticated Staff Portal (`/portal`) with role-based simulated dashboards for **Municipality Planning** and **Recycler Materials Aggregation**.

### Demo Mode (`DEMO_MODE` flag)
- Set `DEMO_MODE=true` in `.env` only when conducting live demonstrations or testing. This exposes a helper on `/portal/login` to pre-fill demo role credentials.
- **Important**: Turn `DEMO_MODE=false` off after the demo or in production. When `DEMO_MODE=false`, the demo credentials endpoint returns `404 Not Found` and no credentials or buttons appear on the login page.

---

## 🛡️ Privacy
- **Zero Image Storage**: Uploaded and captured images are processed strictly in RAM (`io.BytesIO`) and converted to base64. They are never saved to disk or external storage.
- **Text-Only Scan History**: `localStorage` records only `{ item_name, category, special, time }`. No image blobs or thumbnails are stored.

---

## 🧪 Test Suite
Run the automated verification suite:
```bash
python run_live_verification.py
python test_extra_cases.py
python test_issue2_regression.py
```

