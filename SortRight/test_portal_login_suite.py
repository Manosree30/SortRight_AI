import os
import io
import sys
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from backend.app import app
import backend.auth as auth_mod

sys.stdout.reconfigure(encoding='utf-8')
client = TestClient(app)

print("=" * 70)
print("STAFF LOGIN & REGRESSION TEST SUITE")
print("=" * 70)

# Test 1: DEMO_MODE=false -> endpoint returns 404
os.environ["DEMO_MODE"] = "false"
res_demo_off = client.get("/api/auth/demo-credentials")
print(f"1. DEMO_MODE=false test:")
print(f"   Status Code: {res_demo_off.status_code} (Expected: 404)")
print(f"   Response Detail: {res_demo_off.json().get('detail')}")
assert res_demo_off.status_code == 404, "DEMO_MODE=false should return 404"

# Test 2: DEMO_MODE=true -> endpoint returns demo accounts
os.environ["DEMO_MODE"] = "true"
res_demo_on = client.get("/api/auth/demo-credentials")
print(f"\n2. DEMO_MODE=true test:")
print(f"   Status Code: {res_demo_on.status_code} (Expected: 200)")
data_demo = res_demo_on.json()
print(f"   Demo Accounts Returned: {len(data_demo.get('accounts', []))} accounts")
for acc in data_demo.get("accounts", []):
    print(f"     - Role: {acc['role_label']}, Email: {acc['email']}")
assert res_demo_on.status_code == 200, "DEMO_MODE=true should return 200"
assert len(data_demo.get("accounts", [])) == 2

# Reset DEMO_MODE back to false
os.environ["DEMO_MODE"] = "false"

# Test 3: Login as Municipality Officer
res_muni = client.post("/api/portal/login", json={
    "email": "officer@coimbatore.gov.in",
    "password": "Admin@Coimbatore2026"
})
print(f"\n3. Municipality Login:")
print(f"   Status: {res_muni.status_code}, User: {res_muni.json().get('user')}")
assert res_muni.status_code == 200
cookie_muni = res_muni.cookies.get("sortright_session")

# Test 4: Access protected /api/portal/me with cookie
res_me = client.get("/api/portal/me", cookies={"sortright_session": cookie_muni})
print(f"\n4. Access protected /api/portal/me:")
print(f"   Status: {res_me.status_code}, Role: {res_me.json().get('user', {}).get('role')}")
assert res_me.status_code == 200
assert res_me.json()["user"]["role"] == "municipality"

# Test 5: Login as Recycler Partner
res_recy = client.post("/api/portal/login", json={
    "email": "manager@cleanreclaim.in",
    "password": "Recycle@2026"
})
print(f"\n5. Recycler Login:")
print(f"   Status: {res_recy.status_code}, User: {res_recy.json().get('user')}")
assert res_recy.status_code == 200

# Test 6: Wrong Password -> Generic "Invalid credentials." message
res_wrong = client.post("/api/portal/login", json={
    "email": "officer@coimbatore.gov.in",
    "password": "WrongPassword123"
})
print(f"\n6. Wrong Password:")
print(f"   Status: {res_wrong.status_code}, Detail: {res_wrong.json().get('detail')}")
assert res_wrong.status_code == 401
assert res_wrong.json().get("detail") == "Invalid credentials."

# Test 7: Non-existent user -> Generic "Invalid credentials." message
res_nonexist = client.post("/api/portal/login", json={
    "email": "fake_user@random.com",
    "password": "SomePassword"
})
print(f"\n7. Non-existent User:")
print(f"   Status: {res_nonexist.status_code}, Detail: {res_nonexist.json().get('detail')}")
assert res_nonexist.status_code == 401
assert res_nonexist.json().get("detail") == "Invalid credentials."

# Test 8: Logout
res_logout = client.post("/api/portal/logout", cookies={"sortright_session": cookie_muni})
print(f"\n8. Logout:")
print(f"   Status: {res_logout.status_code}, Message: {res_logout.json().get('message')}")
assert res_logout.status_code == 200

# Test 9: Access protected endpoint after logout -> 401
res_me_after = client.get("/api/portal/me", cookies={"sortright_session": cookie_muni})
print(f"\n9. Access /api/portal/me after logout:")
print(f"   Status: {res_me_after.status_code} (Expected: 401), Detail: {res_me_after.json().get('detail')}")
assert res_me_after.status_code == 401

# Test 10: Public Classifier Integrity Check
print("\n" + "=" * 70)
print("PUBLIC CLASSIFIER FLOW VERIFICATION")
print("=" * 70)

# 10a. Text rice
r_rice = client.post("/api/classify-text", json={"text": "rice", "language": "en"})
print(f"10a. Text 'rice':")
print(f"     Item: {r_rice.json().get('item_name')}, Category: {r_rice.json().get('category')}, Special: {r_rice.json().get('special')}")
assert r_rice.json().get("category") == "organic"

# 10b. Text used battery
r_bat = client.post("/api/classify-text", json={"text": "used battery", "language": "en"})
print(f"\n10b. Text 'used battery':")
print(f"     Item: {r_bat.json().get('item_name')}, Category: {r_bat.json().get('category')}, Special: {r_bat.json().get('special')}")
assert r_bat.json().get("special") is True

# 10c. Image upload: plastic bottle
bottle_img = Image.new("RGB", (150, 200), color=(255, 255, 255))
d = ImageDraw.Draw(bottle_img)
d.rectangle([50, 40, 100, 180], fill=(64, 164, 223))
d.rectangle([65, 20, 85, 40], fill=(20, 90, 160))
buf_bottle = io.BytesIO()
bottle_img.save(buf_bottle, format="JPEG")
buf_bottle.seek(0)
r_img = client.post("/api/classify-image", files={"file": ("bottle.jpg", buf_bottle, "image/jpeg")}, data={"language": "en"})
print(f"\n10c. Image Upload (Plastic Bottle):")
print(f"     Detected: {r_img.json().get('item_name')}, Category: {r_img.json().get('category')}")
assert r_img.json().get("category") == "recyclable"

print("\n" + "=" * 70)
print("ALL TESTS PASSED SUCCESSFULLY!")
print("=" * 70)
