import json
import os
import sys

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from checker.excel_exporter import build_excel_response
from checker.models import ChecklistSection
from checker.orchestrator import MODEL, analyze_with_llm
from checker.pdf_extractor import extract_text_from_bytes

# When packaged as an .exe, files are inside sys._MEIPASS instead of the script folder
BASE_DIR = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    checklist: str = Form(...),  # checklist sent as a JSON string together with the PDF
    model: str = Form(default=""),
    api_key: str = Form(default=""),
):
    # Keep the PDF in memory only — never save it to disk
    pdf_bytes = await file.read()
    document_text = extract_text_from_bytes(pdf_bytes)

    try:
        raw = json.loads(checklist)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"checklist JSON ไม่ถูกต้อง: {e}")

    # Check that the checklist data has the right shape before sending to the AI
    try:
        sections = [ChecklistSection.model_validate(s) for s in raw]
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    checklist_data = [{"title": s.title, "items": [{"name": i.name, "score": i.score} for i in s.items]} for s in sections]

    selected_model = model or MODEL

    try:
        llm_result = await analyze_with_llm(document_text, checklist_data, model=selected_model, api_key=api_key)
    except httpx.ConnectError:
        # Ollama is not running — ask the user to start it first
        raise HTTPException(
            status_code=502,
            detail="ไม่สามารถเชื่อมต่อ Ollama ได้ — โปรดตรวจสอบว่า Ollama กำลังรันอยู่ที่ localhost:11434",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Ollama ตอบกลับด้วย error: {e.response.status_code}")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"แปลงผลลัพธ์จาก LLM ไม่ได้: {e}")

    results = llm_result.get("results", [])

    # Count how many items passed and add up their scores
    total = 0
    passed = 0
    total_score = 0.0
    passed_score = 0.0
    for section in results:
        for item in section.get("items", []):
            total += 1
            item_score = float(item.get("score", 0.0))
            total_score += item_score
            if item.get("status") == "pass":
                passed += 1
                passed_score += item_score

    score = round(passed / total * 100) if total > 0 else 0

    return {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "total_score": total_score,
            "passed_score": passed_score,
        },
        "similarity_score": score,
        "results": results,
    }


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
