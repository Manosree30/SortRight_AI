# 🚀 SortRight Cloud Deployment Guide (Render)

This guide provides step-by-step instructions for deploying SortRight as a Python Web Service on [Render](https://render.com).

---

## 📋 Overview
- **Service Type**: Web Service
- **Runtime**: Python 3
- **Framework**: FastAPI + Uvicorn
- **Host Binding**: `0.0.0.0`
- **Port**: Dynamically assigned by Render via the `$PORT` environment variable

---

## 🛠️ Step 1: Connect Repository to Render

1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** in the top navigation bar and select **Web Service**.
3. Under **Connect a repository**, find and select your `SortRight_AI` repository.
4. Click **Connect**.

---

## ⚙️ Step 2: Configure Service Settings

In the Render Web Service configuration page, fill in the following fields:

| Setting | Value |
| :--- | :--- |
| **Name** | `sortright-ai` *(or your preferred service name)* |
| **Region** | Select region closest to your users (e.g., `Singapore`, `Frankfurt`, `Ohio`) |
| **Branch** | `main` |
| **Root Directory** | `SortRight` *(Recommended)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `uvicorn backend.app:app --host 0.0.0.0 --port $PORT` |
| **Plan Type** | Free or Starter |

> [!NOTE]
> If you leave **Root Directory** empty (repository root `.`), use:
> - **Build Command**: `pip install -r requirements.txt`
> - **Start Command**: `cd SortRight && uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

---

## 🔐 Step 3: Configure Environment Variables

In the **Environment Variables** section of your Render Web Service dashboard, add the following variable names. Enter your own values directly in the Render dashboard:

### 1. Mandatory Core Variables
- `GROQ_API_KEY`
  - *Purpose*: Your Groq Cloud API key for AI vision perception and text attribute extraction.
- `SESSION_SECRET`
  - *Purpose*: Long random cryptographic string used for server-side session integrity (e.g., generated with `openssl rand -hex 32` or `python -c "import secrets; print(secrets.token_hex(32))"`). The service will fail fast with a clear error if this is missing.

### 2. AI Model Selection (Optional - defaults are built-in)
- `GROQ_VISION_MODEL`
  - *Default*: `qwen/qwen3.8-27b`
- `GROQ_BACKUP_VISION_MODEL`
  - *Optional fallback model*
- `GROQ_TEXT_MODEL`
  - *Default*: `openai/gpt-oss-120b`

### 3. Production Security & Demo Mode
- `DEMO_MODE`
  - *Value*: `false`
  - *Purpose*: Disables the public demo credentials endpoint (`/api/auth/demo-credentials` returns 404).

### 4. Staff Portal Accounts (Bcrypt Password Hashes)
- `MUNICIPALITY_EMAIL`
  - *Default*: `officer@coimbatore.gov.in`
- `MUNICIPALITY_NAME`
  - *Default*: `Coimbatore Sanitation Admin`
- `MUNICIPALITY_PASSWORD_HASH`
  - *Purpose*: Bcrypt hash of the municipality officer password (e.g., generated using bcrypt).
- `RECYCLER_EMAIL`
  - *Default*: `manager@cleanreclaim.in`
- `RECYCLER_NAME`
  - *Default*: `CleanReclaim Materials`
- `RECYCLER_PASSWORD_HASH`
  - *Purpose*: Bcrypt hash of the recycler partner password.

> [!IMPORTANT]
> Never hardcode or commit actual passwords, API keys, or secret keys into Git. Enter them exclusively through the Render Dashboard.

---

## 🚀 Step 4: Deploy & Verify

1. Click **Create Web Service** (or **Deploy latest commit**).
2. Render will trigger the build pipeline:
   - Clones repository
   - Installs dependencies from `requirements.txt`
   - Executes start command binding to `0.0.0.0:$PORT`
3. Once the deployment status turns green (**Live**), verify the following endpoints:

| Endpoint / Action | Expected Result |
| :--- | :--- |
| `https://<your-render-url>/` | Public Waste Classifier UI loads |
| `https://<your-render-url>/api/health` | Returns JSON status `{"status": "healthy", ...}` |
| `https://<your-render-url>/api/auth/demo-credentials` | Returns `404 Not Found` (confirming `DEMO_MODE=false`) |
| `https://<your-render-url>/portal/login` | Staff portal login page loads |
| Staff Login (`/api/portal/login`) | Sets cookie with `HttpOnly` and `Secure` attributes over HTTPS |

---

## 💻 Local Development Reference

To continue running and testing locally:
```bash
# Navigate to SortRight directory
cd SortRight

# Install dependencies in your virtual environment
pip install -r backend/requirements.txt

# Start local server with hot-reload
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```
Local application URL: `http://localhost:8000`
