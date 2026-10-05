"""
SortRight - Deployment Verification Test Suite
Tests:
1. Dashboard data endpoints return 401 without login
2. Dashboard data endpoints return data after login
3. /api/auth/demo-credentials returns 404 when DEMO_MODE=false
4. Startup fails clearly when SESSION_SECRET is missing
5. Login is rate-limited after repeated wrong passwords
"""
import os
import sys
import bcrypt
from fastapi.testclient import TestClient
import backend.auth as auth_mod
from backend.app import app

client = TestClient(app)

print("=" * 70)
print("1. TEST: Dashboard data endpoints return 401 without login")
print("=" * 70)
r_muni_unauth = client.get("/api/portal/municipality-data")
r_recy_unauth = client.get("/api/portal/recycler-data")
print(f"GET /api/portal/municipality-data (unauthenticated): Status {r_muni_unauth.status_code}")
print(f"  Response: {r_muni_unauth.json()}")
print(f"GET /api/portal/recycler-data (unauthenticated): Status {r_recy_unauth.status_code}")
print(f"  Response: {r_recy_unauth.json()}")
assert r_muni_unauth.status_code == 401, "Expected 401 for unauthenticated municipality-data"
assert r_recy_unauth.status_code == 401, "Expected 401 for unauthenticated recycler-data"

print("\n" + "=" * 70)
print("2. TEST: Dashboard data endpoints return data after login")
print("=" * 70)
demo_pw = "DemoPassword2026!"
os.environ["MUNICIPALITY_EMAIL"] = "municipality@demo.example"
os.environ["MUNICIPALITY_NAME"] = "Demo Municipality User"
os.environ["MUNICIPALITY_PASSWORD_HASH"] = bcrypt.hashpw(demo_pw.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
os.environ["SESSION_SECRET"] = "verified_session_secret_2026"

r_login = client.post("/api/portal/login", json={
    "email": "municipality@demo.example",
    "password": demo_pw
})
print(f"POST /api/portal/login: Status {r_login.status_code}")
print(f"  User profile: {r_login.json().get('user')}")
assert r_login.status_code == 200, "Login should succeed"
session_cookie = r_login.cookies.get("sortright_session")
assert session_cookie, "Session cookie must be set"

r_muni_auth = client.get("/api/portal/municipality-data", cookies={"sortright_session": session_cookie})
r_recy_auth = client.get("/api/portal/recycler-data", cookies={"sortright_session": session_cookie})
print(f"GET /api/portal/municipality-data (authenticated): Status {r_muni_auth.status_code}")
print(f"  Total scans: {r_muni_auth.json().get('kpi', {}).get('total_scans')}")
print(f"  Ward table rows: {len(r_muni_auth.json().get('ward_table', []))}")
print(f"GET /api/portal/recycler-data (authenticated): Status {r_recy_auth.status_code}")
print(f"  Materials listed: {len(r_recy_auth.json().get('materials', []))}")
assert r_muni_auth.status_code == 200
assert r_recy_auth.status_code == 200

print("\n" + "=" * 70)
print("3. TEST: /api/auth/demo-credentials returns 404 when DEMO_MODE=false")
print("=" * 70)
os.environ["DEMO_MODE"] = "false"
r_demo_404 = client.get("/api/auth/demo-credentials")
print(f"GET /api/auth/demo-credentials: Status {r_demo_404.status_code}")
print(f"  Response: {r_demo_404.json()}")
assert r_demo_404.status_code == 404, "DEMO_MODE=false must return 404"

print("\n" + "=" * 70)
print("4. TEST: Startup validation fails clearly when SESSION_SECRET is missing")
print("=" * 70)
os.environ.pop("SESSION_SECRET", None)
try:
    auth_mod.get_session_secret()
    print("ERROR: Startup validation did not raise error!")
    sys.exit(1)
except RuntimeError as e:
    print(f"Startup validation raised expected RuntimeError:")
    print(f"  \"{str(e)}\"")

# Restore session secret
os.environ["SESSION_SECRET"] = "verified_session_secret_2026"

print("\n" + "=" * 70)
print("5. TEST: Login is rate-limited after repeated wrong passwords")
print("=" * 70)
auth_mod.LOGIN_ATTEMPTS.clear()
test_client = TestClient(app, base_url="http://testserver")

for attempt in range(1, 6):
    r_bad = test_client.post("/api/portal/login", json={
        "email": "municipality@demo.example",
        "password": "incorrect_password"
    })
    print(f"  Attempt {attempt}: Status {r_bad.status_code} ({r_bad.json().get('detail')})")

r_rate_limited = test_client.post("/api/portal/login", json={
    "email": "municipality@demo.example",
    "password": "incorrect_password"
})
print(f"  Attempt 6 (Rate Limited): Status {r_rate_limited.status_code}")
print(f"  Response detail: \"{r_rate_limited.json().get('detail')}\"")
assert r_rate_limited.status_code == 429, "Attempt 6 must return 429 Too Many Requests"

print("\n" + "=" * 70)
print("ALL 5 VERIFICATION SUITES PASSED SUCCESSFULLY!")
print("=" * 70)
