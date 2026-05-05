import json
import os
import sys

import httpx
import pymupdf
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from checker.excel_exporter import build_excel_response
from checker.models import ChecklistSection
from checker.orchestrator import MODEL, analyze_with_llm_stream
from checker.pdf_extractor import extract_text_from_bytes

# When packaged as an .exe, files are inside sys._MEIPASS instead of the script folder
BASE_DIR = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


_LOCAL_MODELS = [
    {"value": "gemma4:26b", "label": "Gemma 4 26B (Local)"},
]


@app.get("/")
async def index(request: Request):
    installed: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://localhost:11434/api/tags")
            if r.status_code == 200:
                installed = [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    local_models = [m for m in _LOCAL_MODELS if m["value"] in installed]
    return templates.TemplateResponse(request, "index.html", {"local_models": local_models})


@app.post("/analyze/stream")
async def analyze_stream(
    file: UploadFile = File(...),
    checklist: str = Form(...),
    model: str = Form(default=""),
    api_key: str = Form(default=""),
):
    # Validate inputs up-front so errors come back as proper HTTP responses, not as SSE error events
    pdf_bytes = await file.read()
    try:
        document_text = extract_text_from_bytes(pdf_bytes)
    except pymupdf.FileDataError:
        raise HTTPException(status_code=422, detail="ไฟล์ที่อัปโหลดไม่ใช่ PDF ที่ถูกต้อง หรือไฟล์เสียหาย")

    try:
        raw = json.loads(checklist)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"checklist JSON ไม่ถูกต้อง: {e}")

    try:
        sections = [ChecklistSection.model_validate(s) for s in raw]
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=jsonable_encoder(e.errors()))

    checklist_data = [{"title": s.title, "items": [{"name": i.name, "score": i.score} for i in s.items]} for s in sections]
    selected_model = model or MODEL

    async def event_stream():
        try:
            async for event in analyze_with_llm_stream(document_text, checklist_data, model=selected_model, api_key=api_key):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except httpx.ConnectError:
            err = {"type": "error", "detail": "ไม่สามารถเชื่อมต่อ Ollama ได้ โปรดตรวจสอบว่า Ollama กำลังรันอยู่ที่ localhost:11434"}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
        except httpx.HTTPStatusError as e:
            code = e.response.status_code
            if code == 400:
                detail = "คำขอไม่ถูกต้อง โปรดตรวจสอบชื่อโมเดลและรูปแบบคำขอ (400 Bad Request)"
            elif code == 401:
                detail = "API Key ไม่ถูกต้องหรือหมดอายุ โปรดตรวจสอบ API Key อีกครั้ง (401 Unauthorized)"
            elif code == 403:
                detail = "API Key ไม่มีสิทธิ์เข้าถึงโมเดลนี้ โปรดตรวจสอบสิทธิ์การใช้งาน (403 Forbidden)"
            elif code == 404:
                detail = "ไม่พบโมเดลที่เลือก โปรดตรวจสอบชื่อโมเดลให้ถูกต้อง (404 Not Found)"
            elif code == 429:
                detail = "เกินขีดจำกัดการใช้งาน API โปรดรอสักครู่แล้วลองใหม่อีกครั้ง (429 Too Many Requests)"
            else:
                detail = f"เกิดข้อผิดพลาดจาก AI provider (HTTP {code})"
            yield f"data: {json.dumps({'type': 'error', 'detail': detail}, ensure_ascii=False)}\n\n"
        except Exception as e:
            err = {"type": "error", "detail": f"เกิดข้อผิดพลาด: {e}"}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/export/excel")
async def export_excel(payload: dict):
    # Build the Excel file and send it back to the browser
    return build_excel_response(
        filename=payload.get("filename", "document"),
        results_data=payload.get("results", []),
        summary=payload.get("summary", {}),
        score=payload.get("similarity_score", 0),
    )


@app.get("/health")
async def health():
    # Ask Ollama if it is running; a 200 reply means it is ready
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("http://localhost:11434/api/tags")
            ollama_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "status": "ok",
        "ollama": "reachable" if ollama_ok else "unreachable",
        "model": MODEL,
    }
