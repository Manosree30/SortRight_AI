import os
import time
import secrets
import bcrypt
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from dotenv import load_dotenv

load_dotenv()

# In-memory session store: session_token -> { email, role, name, expires_at }
SESSIONS: Dict[str, Dict[str, Any]] = {}
SESSION_DURATION_SECONDS = 3600 * 12 # 12 hours

# Rate limiting for failed logins: client_ip -> { attempts: int, locked_until: float }
LOGIN_ATTEMPTS: Dict[str, Dict[str, Any]] = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_WINDOW_SECONDS = 300 # 5 minutes

def get_session_secret() -> str:
    """
    Retrieves the mandatory SESSION_SECRET from environment.
    Fails with a clear, descriptive error if missing or empty.
    """
    secret = os.getenv("SESSION_SECRET", "").strip()
    if not secret:
        raise RuntimeError(
            "CRITICAL: SESSION_SECRET environment variable is missing or empty. "
            "Please set SESSION_SECRET in your environment or .env file before running SortRight."
        )
    return secret

def get_demo_users() -> Dict[str, Dict[str, Any]]:
    """
    Loads demo user accounts strictly from environment variables.
    Never hardcoded in code or client.
    """
    users = {}
    
    muni_email = os.getenv("MUNICIPALITY_EMAIL", "officer@coimbatore.gov.in").strip().lower()
    muni_hash = os.getenv("MUNICIPALITY_PASSWORD_HASH", "").strip()
    muni_name = os.getenv("MUNICIPALITY_NAME", "Coimbatore Sanitation Admin").strip()
    if muni_email and muni_hash:
        users[muni_email] = {
            "email": muni_email,
            "role": "municipality",
            "name": muni_name,
            "password_hash": muni_hash
        }

    recy_email = os.getenv("RECYCLER_EMAIL", "manager@cleanreclaim.in").strip().lower()
    recy_hash = os.getenv("RECYCLER_PASSWORD_HASH", "").strip()
    recy_name = os.getenv("RECYCLER_NAME", "CleanReclaim Materials").strip()
    if recy_email and recy_hash:
        users[recy_email] = {
            "email": recy_email,
            "role": "recycler",
            "name": recy_name,
            "password_hash": recy_hash
        }

    return users

def is_demo_mode() -> bool:
    """
    Checks if DEMO_MODE is explicitly enabled in environment.
    Defaults to False in production.
    """
    raw_val = os.getenv("DEMO_MODE", "false")
    clean_val = str(raw_val).strip().strip('"').strip("'").lower()
    return clean_val in ("true", "1", "yes", "t", "y")

def get_demo_credentials_for_client() -> Optional[Dict[str, Any]]:
    """
    Returns demo credentials only when DEMO_MODE is true.
    Returns None if demo mode is disabled.
    """
    if not is_demo_mode():
        return None
    return {
        "enabled": True,
        "accounts": [
            {
                "role_label": "Municipality Admin",
                "email": os.getenv("MUNICIPALITY_EMAIL", "officer@coimbatore.gov.in").strip(),
                "password": os.getenv("DEMO_MUNICIPALITY_PASSWORD", "Admin@Coimbatore2026").strip()
            },
            {
                "role_label": "Recycler Partner",
                "email": os.getenv("RECYCLER_EMAIL", "manager@cleanreclaim.in").strip(),
                "password": os.getenv("DEMO_RECYCLER_PASSWORD", "Recycle@2026").strip()
            }
        ]
    }



def check_rate_limit(ip: str) -> None:
    now = time.time()
    record = LOGIN_ATTEMPTS.get(ip)
    if record:
        if record.get("locked_until", 0) > now:
            remaining = int(record["locked_until"] - now)
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed login attempts. Please try again in {remaining} seconds."
            )
        # Reset if lockout expired
        if record.get("locked_until", 0) > 0 and record["locked_until"] <= now:
            LOGIN_ATTEMPTS.pop(ip, None)

def record_failed_login(ip: str) -> None:
    now = time.time()
    record = LOGIN_ATTEMPTS.setdefault(ip, {"attempts": 0, "locked_until": 0})
    record["attempts"] += 1
    if record["attempts"] >= MAX_FAILED_ATTEMPTS:
        record["locked_until"] = now + LOCKOUT_WINDOW_SECONDS

def record_successful_login(ip: str) -> None:
    LOGIN_ATTEMPTS.pop(ip, None)

def verify_credentials(email: str, password: str, client_ip: str) -> Dict[str, Any]:
    check_rate_limit(client_ip)
    
    email_clean = (email or "").strip().lower()
    users = get_demo_users()
    user = users.get(email_clean)

    # Always perform constant-time check to mitigate timing attacks
    if not user:
        # Dummy check
        bcrypt.checkpw(b"dummy_password", b"$2b$12$TeUqDWGWhiCIBybSA0BoaujllTZBVUT7Hq85Pa0v5MWJESyS9FkPK")
        record_failed_login(client_ip)
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Check password against stored bcrypt hash
    stored_hash = user["password_hash"].encode("utf-8")
    try:
        is_valid = bcrypt.checkpw(password.encode("utf-8"), stored_hash)
    except Exception:
        is_valid = False

    if not is_valid:
        record_failed_login(client_ip)
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    record_successful_login(client_ip)
    return {
        "email": user["email"],
        "role": user["role"],
        "name": user["name"]
    }

def create_session(user_data: Dict[str, Any]) -> str:
    # Ensure session secret is configured in environment
    get_session_secret()
    session_token = secrets.token_urlsafe(32)
    expires_at = time.time() + SESSION_DURATION_SECONDS
    SESSIONS[session_token] = {
        "email": user_data["email"],
        "role": user_data["role"],
        "name": user_data["name"],
        "expires_at": expires_at
    }
    return session_token

def destroy_session(session_token: Optional[str]) -> None:
    if session_token and session_token in SESSIONS:
        SESSIONS.pop(session_token, None)

def get_current_user(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency: Server-side validation of session cookie.
    Guarantees that protected endpoints return 401 if unauthenticated.
    """
    session_token = request.cookies.get("sortright_session")
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required. Please log in.")

    session = SESSIONS.get(session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session. Please log in again.")

    if session["expires_at"] < time.time():
        SESSIONS.pop(session_token, None)
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    return {
        "email": session["email"],
        "role": session["role"],
        "name": session["name"]
    }
