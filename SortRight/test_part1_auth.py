import json
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

print("=" * 65)
print("PART 1 VERIFICATION: AUTHENTICATION & ROUTING SPLIT")
print("=" * 65)

# 1. Unauthenticated Request Test
print("\n1. Testing Unauthenticated Request to Protected Endpoints:")
r_unauth_me = client.get("/api/portal/me")
print(f"  GET /api/portal/me: Status {r_unauth_me.status_code} (Expected: 401)")
print(f"  Response: {r_unauth_me.json()}")

r_unauth_data = client.get("/api/portal/municipality-data")
print(f"  GET /api/portal/municipality-data: Status {r_unauth_data.status_code} (Expected: 401)")
print(f"  Response: {r_unauth_data.json()}")

# 2. Wrong Password Test
print("\n2. Testing Wrong Password Login:")
r_wrong = client.post("/api/portal/login", json={
    "email": "officer@coimbatore.gov.in",
    "password": "WrongPassword123"
})
print(f"  POST /api/portal/login (wrong password): Status {r_wrong.status_code} (Expected: 401)")
print(f"  Response: {r_wrong.json()}")

# 3. Municipality Officer Login Test
print("\n3. Testing Valid Municipality Officer Login:")
client_muni = TestClient(app)
r_login_muni = client_muni.post("/api/portal/login", json={
    "email": "officer@coimbatore.gov.in",
    "password": "Admin@Coimbatore2026"
})
print(f"  POST /api/portal/login (muni): Status {r_login_muni.status_code}")
print(f"  Cookies set: {list(client_muni.cookies.keys())}")
print(f"  Login response: {r_login_muni.json()}")

r_me_muni = client_muni.get("/api/portal/me")
print(f"  GET /api/portal/me: Status {r_me_muni.status_code}")
print(f"  User profile: {r_me_muni.json()}")

r_data_muni = client_muni.get("/api/portal/municipality-data?days=30")
print(f"  GET /api/portal/municipality-data: Status {r_data_muni.status_code}")
print(f"  Simulated total scans: {r_data_muni.json()['kpi']['total_scans']}")
print(f"  First ward in table: {r_data_muni.json()['ward_table'][0]['ward_name']}")

# 4. Recycler Partner Login Test
print("\n4. Testing Valid Recycler Partner Login:")
client_recy = TestClient(app)
r_login_recy = client_recy.post("/api/portal/login", json={
    "email": "manager@cleanreclaim.in",
    "password": "Recycle@2026"
})
print(f"  POST /api/portal/login (recycler): Status {r_login_recy.status_code}")
print(f"  Cookies set: {list(client_recy.cookies.keys())}")
print(f"  Login response: {r_login_recy.json()}")

r_me_recy = client_recy.get("/api/portal/me")
print(f"  GET /api/portal/me: Status {r_me_recy.status_code}")
print(f"  User profile: {r_me_recy.json()}")

r_data_recy = client_recy.get("/api/portal/recycler-data?days=30")
print(f"  GET /api/portal/recycler-data: Status {r_data_recy.status_code}")
print(f"  First material available: {r_data_recy.json()['material_availability'][0]['material_type']} ({r_data_recy.json()['material_availability'][0]['estimated_metric_tons']} Tons)")

# 5. Logout Test
print("\n5. Testing Logout:")
r_logout = client_muni.post("/api/portal/logout")
print(f"  POST /api/portal/logout: Status {r_logout.status_code}")
print(f"  Response: {r_logout.json()}")

r_after_logout = client_muni.get("/api/portal/me")
print(f"  GET /api/portal/me after logout: Status {r_after_logout.status_code} (Expected: 401)")

# 6. Public Classifier Unaffected Test
print("\n6. Testing Public Classifier (Zero Auth Required):")
r_public = client.post("/api/classify-text", json={"text": "tea bag", "language": "en"})
print(f"  POST /api/classify-text: Status {r_public.status_code} (Expected: 200)")
print(f"  Item: {r_public.json().get('item_name')}, Category: {r_public.json().get('category')}")
