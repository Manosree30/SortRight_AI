import os
import re
from fastapi.testclient import TestClient
from backend.app import app
from backend.auth import is_demo_mode

client = TestClient(app)

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

def set_env_demo_mode(val_str: str):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    if re.search(r"^DEMO_MODE=.*$", content, re.MULTILINE):
        new_content = re.sub(r"^DEMO_MODE=.*$", f"DEMO_MODE={val_str}", content, flags=re.MULTILINE)
    else:
        new_content = content + f"\nDEMO_MODE={val_str}\n"
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

print("=" * 60)
print("TESTING DEMO_MODE IN .ENV (FILE CHANGE TEST)")
print("=" * 60)

# 1. Set DEMO_MODE=true in .env
set_env_demo_mode("true")
is_true = is_demo_mode()
res_true = client.get("/api/auth/demo-credentials")
print(f"1. With DEMO_MODE=true in .env:")
print(f"   Server reads is_demo_mode(): {is_true}")
print(f"   Endpoint status code: {res_true.status_code} (Expected: 200)")
print(f"   Accounts returned: {len(res_true.json().get('accounts', []))} accounts")
assert is_true is True
assert res_true.status_code == 200
assert len(res_true.json().get("accounts", [])) == 2

# 2. Set DEMO_MODE=false in .env
set_env_demo_mode("false")
is_false = is_demo_mode()
res_false = client.get("/api/auth/demo-credentials")
print(f"\n2. With DEMO_MODE=false in .env:")
print(f"   Server reads is_demo_mode(): {is_false}")
print(f"   Endpoint status code: {res_false.status_code} (Expected: 404)")
print(f"   Endpoint response detail: {res_false.json().get('detail')}")
assert is_false is False
assert res_false.status_code == 404

print("\n" + "=" * 60)
print("BOTH MODES (TRUE & FALSE) VERIFIED SUCCESSFULLY!")
print("=" * 60)
