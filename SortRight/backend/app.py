import os
import csv
import io
import json
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Response, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, Response
from pydantic import BaseModel

from .rules_engine import rules_engine
from .ai_service import ai_service
from .auth import (
    verify_credentials, create_session, destroy_session,
    get_current_user, SESSIONS, get_demo_credentials_for_client
)
from .simulated_data import get_municipality_analytics, get_recycler_analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SortRight.API")

app = FastAPI(
    title="SortRight AI Waste Classification API",
    description="Deterministic Rules Engine + Groq AI Perception + Portal Auth",
    version="2.0.0"
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Pydantic Schemas
class TextClassificationRequest(BaseModel):
    text: str
    language: Optional[str] = "en"

class ClarificationRequest(BaseModel):
    item: str
    material: str
    condition: Optional[str] = "unknown"
    is_greasy_or_food_soiled: bool
    language: Optional[str] = "en"

class TranslationRequest(BaseModel):
    card: Dict[str, Any]
    target_language: str

class LoginRequest(BaseModel):
    email: str
    password: str


# =========================================================
# PUBLIC CLASSIFICATION PIPELINE (Preserved & Untouched)
# =========================================================

def format_classification_response(
    ai_output: Dict[str, Any],
    user_clarification: Optional[bool] = None,
    language: str = "en"
) -> Dict[str, Any]:
    confidence = float(ai_output.get("confidence", 0.0))
    item = ai_output.get("item", "Unidentified Item")
    material = ai_output.get("material", "unknown")
    condition = ai_output.get("condition", "clean")

    rule_eval = rules_engine.evaluate(
        item=item,
        material=material,
        condition=condition,
        user_clarification_response=user_clarification
    )

    if confidence < 0.5 or rule_eval.get("is_not_sure", False):
        confidence_status = "fallback"
        confidence_message = "I'm not sure. Please retake the photo or describe the item."
        reason_text = "I'm not sure. Please retake the photo or describe the item."
        steps_dict = {
            "prepare": "Check lighting and item clarity.",
            "separate": "Verify with local municipal waste guidelines.",
            "route": "Please retake the photo or enter the item name in the text box."
        }
    elif confidence < 0.8:
        confidence_status = "verify"
        confidence_message = "Please verify: item was detected with moderate confidence."
        reason_text = rule_eval.get("reason")
        steps_dict = rule_eval.get("steps")
    else:
        confidence_status = "high"
        confidence_message = "High confidence identification."
        reason_text = rule_eval.get("reason")
        steps_dict = rule_eval.get("steps")

    response_card = {
        "success": True,
        "ai_perception": {
            "item_detected": item,
            "material_detected": material,
            "condition_detected": condition,
            "confidence": round(confidence, 2),
            "confidence_status": confidence_status,
            "confidence_message": confidence_message,
            "model_used": ai_output.get("model_used", "groq")
        },
        "rule_id": rule_eval.get("rule_id"),
        "item_name": rule_eval.get("item_name"),
        "category": rule_eval.get("category"),
        "special": rule_eval.get("special", False),
        "recycling_potential": rule_eval.get("recycling_potential"),
        "potential_label": rule_eval.get("potential_label", "Recycling potential"),
        "reason": reason_text,
        "steps": steps_dict,
        "needs_clarification": rule_eval.get("needs_clarification", False),
        "clarifying_question": rule_eval.get("clarifying_question"),
        "city": rule_eval.get("city"),
        "disclaimer": rule_eval.get("disclaimer"),
        "source": rule_eval.get("source"),
        "last_updated": rule_eval.get("last_updated"),
        "language": language
    }

    if language and language.lower() not in ("en", "english"):
        response_card = ai_service.translate_result(response_card, language)

    return response_card


@app.post("/api/classify-image")
async def classify_image(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en")
):
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image uploaded.")

        ai_res = ai_service.analyze_image(image_bytes)

        if not ai_res.get("success", False):
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "error_type": ai_res.get("error_type", "VISION_ERROR"),
                    "message": ai_res.get("message", "Could not process image. Please try text input instead."),
                    "fallback_to_text": True
                }
            )

        card = format_classification_response(ai_res, language=language)
        return card

    except Exception as e:
        logger.exception("Error processing image classification")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_type": "SERVER_ERROR",
                "message": f"An error occurred while analyzing the image ({str(e)}). Please try text input.",
                "fallback_to_text": True
            }
        )


@app.post("/api/classify-text")
async def classify_text(req: TextClassificationRequest):
    try:
        ai_res = ai_service.analyze_text(req.text)
        card = format_classification_response(ai_res, language=req.language or "en")
        return card
    except Exception as e:
        logger.exception("Error processing text classification")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Server error: {str(e)}"
            }
        )


@app.post("/api/clarify")
async def clarify_question(req: ClarificationRequest):
    ai_output = {
        "item": req.item,
        "material": req.material,
        "condition": "greasy" if req.is_greasy_or_food_soiled else "clean",
        "confidence": 0.95,
        "model_used": "rules_engine_direct"
    }
    card = format_classification_response(
        ai_output=ai_output,
        user_clarification=req.is_greasy_or_food_soiled,
        language=req.language or "en"
    )
    return card


@app.post("/api/translate")
async def translate_card(req: TranslationRequest):
    translated = ai_service.translate_result(req.card, req.target_language)
    return translated


@app.get("/api/rules")
async def get_rules():
    return rules_engine.rules_data


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "city": "Coimbatore (Sample City)",
        "vision_model": os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b"),
        "text_model": os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b"),
        "groq_api_key_configured": bool(os.getenv("GROQ_API_KEY"))
    }


# =========================================================
# STAFF PORTAL AUTHENTICATION & PROTECTED DATA ENDPOINTS
# =========================================================

@app.get("/api/auth/demo-credentials")
async def get_demo_credentials_endpoint():
    """
    Returns demo credentials only if DEMO_MODE is true in .env.
    Returns 404 if DEMO_MODE is disabled/false.
    """
    creds = get_demo_credentials_for_client()
    if not creds:
        raise HTTPException(status_code=404, detail="Demo mode is disabled.")
    return creds


@app.post("/api/portal/login")
async def portal_login(req: LoginRequest, request: Request, response: Response):
    """
    Validates demo credentials against bcrypt hash in environment,
    creates server-side session, and sets secure httpOnly cookie.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_data = verify_credentials(req.email, req.password, client_ip)
    
    session_token = create_session(user_data)
    
    response.set_cookie(
        key="sortright_session",
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=False, # True in HTTPS production
        max_age=3600 * 12
    )

    return {
        "success": True,
        "message": "Login successful.",
        "user": {
            "email": user_data["email"],
            "role": user_data["role"],
            "name": user_data["name"]
        }
    }


@app.post("/api/portal/logout")
async def portal_logout(request: Request, response: Response):
    """
    Destroys active session on server and clears cookie.
    """
    session_token = request.cookies.get("sortright_session")
    destroy_session(session_token)
    response.delete_cookie(key="sortright_session")
    return {"success": True, "message": "Logged out successfully."}


@app.get("/api/portal/me")
async def portal_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Protected endpoint: returns authenticated user profile or 401 Unauthorized.
    """
    return {
        "authenticated": True,
        "user": current_user
    }


@app.get("/api/portal/municipality-data")
async def api_municipality_data(
    days: int = Query(30, ge=7, le=90),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Protected Endpoint: Returns simulated municipality planning data.
    Requires valid server-side session.
    """
    return get_municipality_analytics(days=days)


@app.get("/api/portal/recycler-data")
async def api_recycler_data(
    days: int = Query(30, ge=7, le=90),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Protected Endpoint: Returns simulated material availability for recyclers.
    Requires valid server-side session.
    """
    return get_recycler_analytics(days=days)


@app.get("/api/portal/export-csv")
async def export_ward_csv(
    days: int = Query(30, ge=7, le=90),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Protected Endpoint: Generates and streams downloadable CSV of simulated ward data.
    """
    data = get_municipality_analytics(days=days)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Ward ID", "Ward Name", "Scans Count", "Recyclable %", "Organic %", "Contamination %", "E-Waste (kg)", "Status"])
    
    for row in data.get("ward_table", []):
        writer.writerow([
            row["ward_id"],
            row["ward_name"],
            row["scans"],
            row["recyclable_pct"],
            row["organic_pct"],
            row["contamination_pct"],
            row["ewaste_kg"],
            row["status"]
        ])

    csv_bytes = output.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=sortright_ward_data_{days}d.csv"}
    )


# =========================================================
# PAGE ROUTES & STATIC FILES
# =========================================================

@app.get("/portal/login")
async def serve_portal_login():
    login_html = os.path.join(FRONTEND_DIR, "portal_login.html")
    if os.path.exists(login_html):
        return FileResponse(login_html)
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/portal")
async def serve_portal():
    portal_html = os.path.join(FRONTEND_DIR, "portal.html")
    if os.path.exists(portal_html):
        return FileResponse(portal_html)
    return FileResponse(os.path.join(FRONTEND_DIR, "portal_login.html"))

if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
