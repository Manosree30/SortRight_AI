import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from backend.app import app
from backend.auth import is_demo_mode, get_demo_credentials_for_client

client = TestClient(app)

print("--- 1. Testing with current .env ---")
load_dotenv(override=True)
current_raw = os.getenv("DEMO_MODE")
print(f"Server reads DEMO_MODE raw from .env as: {current_raw}")
print(f"is_demo_mode() returns: {is_demo_mode()}")

res = client.get("/api/auth/demo-credentials")
print(f"Endpoint GET /api/auth/demo-credentials status: {res.status_code}")

print("\n--- 2. Testing with DEMO_MODE=true in environment ---")
os.environ["DEMO_MODE"] = "true"
print(f"is_demo_mode() returns: {is_demo_mode()}")
res_true = client.get("/api/auth/demo-credentials")
print(f"Endpoint status when DEMO_MODE=true: {res_true.status_code}")
data = res_true.json()
print(f"Returns accounts list: {bool(data.get('accounts'))}, count: {len(data.get('accounts', []))}")

print("\n--- 3. Testing with DEMO_MODE=false in environment ---")
os.environ["DEMO_MODE"] = "false"
print(f"is_demo_mode() returns: {is_demo_mode()}")
res_false = client.get("/api/auth/demo-credentials")
print(f"Endpoint status when DEMO_MODE=false: {res_false.status_code}")
print(f"Endpoint response detail: {res_false.json().get('detail')}")
