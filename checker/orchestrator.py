import json
import re

import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:e4b"

MAX_DOC_CHARS = 24_000

_SINGLE_ITEM_SCHEMA = {
    "type": "object",
    "required": ["status", "reasoning_in_thai", "evidence"],
    "properties": {
        "status": {"type": "string", "enum": ["pass", "partial", "fail"]},
        "reasoning_in_thai": {"type": "string", "description": "อธิบายเหตุผลเป็นภาษาไทยเท่านั้น"},
        "evidence": {"type": ["string", "null"]},
    },
}


def _build_single_prompt(document_text: str, section_title: str, requirement: str) -> str:
    if len(document_text) > MAX_DOC_CHARS:
        document_text = (
            document_text[:MAX_DOC_CHARS]
            + "\n\n[เอกสารถูกตัดทอนเนื่องจากความยาวเกินกำหนด]"
        )

    return f"""คุณคือระบบตรวจสอบเอกสาร กรุณาตรวจสอบว่าเอกสารด้านล่างมีเนื้อหาตรงกับข้อกำหนดที่ระบุหรือไม่

หัวข้อ: {section_title}
ข้อกำหนด: {requirement}

ตอบเป็นภาษาไทยเท่านั้น โดยใช้รูปแบบ JSON ดังนี้:
{{
  "status": "pass" | "partial" | "fail",
  "reasoning_in_thai": "<อธิบายเหตุผล 1-2 ประโยค เป็นภาษาไทยเท่านั้น ห้ามใช้ภาษาอังกฤษ>",
  "evidence": "<ข้อความอ้างอิงจากเอกสารไม่เกิน 100 ตัวอักษร หรือ null>"
}}

กฎ:
- "pass"    = พบเนื้อหาที่ตรงกับข้อกำหนดอย่างชัดเจน
- "partial" = พบเนื้อหาที่เกี่ยวข้องบางส่วน
- "fail"    = ไม่พบเนื้อหาที่ตรงกับข้อกำหนด
- "evidence" ต้องเป็น null เมื่อ status เป็น "fail"
- ห้ามใช้ภาษาอังกฤษในการอธิบาย (reasoning_in_thai) เด็ดขาด ต้องตอบเป็นภาษาไทย

DOCUMENT:
{document_text}"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fenced:
        text = fenced.group(1)
    return json.loads(text)


async def _check_single_item(
    client: httpx.AsyncClient,
    document_text: str,
    section_title: str,
    requirement: str,
) -> dict:
    prompt = _build_single_prompt(document_text, section_title, requirement)
    try:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "system": "คุณตอบเป็นภาษาไทยเท่านั้น ห้ามใช้ภาษาอังกฤษในคำอธิบาย",
                "prompt": prompt,
                "stream": False,
                "format": _SINGLE_ITEM_SCHEMA,
            },
        )
        response.raise_for_status()
        llm_text = response.json().get("response", "")
        result = _extract_json(llm_text)
        
        if "reasoning_in_thai" in result:
            result["reasoning"] = result.pop("reasoning_in_thai")
        elif "reasoning" not in result:
            result["reasoning"] = ""
            
        print(f"[DEBUG] '{requirement[:40]}' → {result.get('status')}")
        return result
    except Exception as e:
        print(f"[ERROR] Failed checking '{requirement[:40]}': {e}")
        return {"status": "fail", "reasoning": f"เกิดข้อผิดพลาด: {e}", "evidence": None}


async def analyze_with_llm(document_text: str, checklist: list[dict]) -> dict:
    """Check each sub-item individually against the document."""
    print(f"[DEBUG] Checklist received: {json.dumps(checklist, ensure_ascii=False)}")

    results = []
    async with httpx.AsyncClient(timeout=120) as client:
        for section in checklist:
            section_title = section.get("title", "")
            items_out = []
            for requirement in section.get("items", []):
                check = await _check_single_item(client, document_text, section_title, requirement)
                items_out.append({
                    "requirement": requirement,
                    "status": check.get("status", "fail"),
                    "reasoning": check.get("reasoning", ""),
                    "evidence": check.get("evidence"),
                })
            results.append({"section": section_title, "items": items_out})

    total = sum(len(s["items"]) for s in results)
    passed = sum(1 for s in results for it in s["items"] if it["status"] == "pass")
    return {
        "summary": {"total": total, "passed": passed, "failed": total - passed},
        "results": results,
    }
