import json
import re

import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:26b"
OLLAMA_TIMEOUT = httpx.Timeout(connect=30.0, read=1200.0, write=60.0, pool=10.0)
OLLAMA_OPTIONS = {"num_ctx": 32768, "num_predict": 512, "temperature": 0}

CHUNK_SIZE = 24_000      # characters per chunk sent to LLM
CHUNK_OVERLAP = 2_000   # overlap between consecutive chunks to avoid missing content at boundaries

_JSON_FORMAT_EXAMPLE = """{
  "status": "pass หรือ fail",
  "reasoning_in_thai": "1-2 ประโยคสั้นๆ เป็นภาษาไทยเท่านั้น",
  "evidence": "ข้อความที่คัดลอกจากเอกสาร ไม่เกิน 80 ตัวอักษร หรือ null ถ้าไม่พบ",
  "found_in_document": true
}"""


def _build_single_prompt(document_text: str, section_title: str, requirement: str) -> str:
    return f"""คุณคือระบบตรวจสอบเอกสาร หน้าที่ของคุณคือตรวจสอบว่าเอกสารมีเนื้อหาครอบคลุมข้อกำหนดที่ระบุหรือไม่

หัวข้อ: {section_title}
ข้อกำหนด: {requirement}

เกณฑ์การตัดสิน:
- "pass" = เอกสารมีเนื้อหาที่เกี่ยวข้องกับข้อกำหนดนี้ ไม่ว่าจะใช้คำพูดเดียวกันหรือความหมายใกล้เคียงก็ได้ ใช้การดูข้อมูลจากทั้งเอกสาร ไม่ใช่แค่การเปรียบเทียบคำ ต้องระบุ evidence เป็นข้อความจากเอกสาร
- "fail" = เอกสารไม่มีเนื้อหาที่เกี่ยวข้องกับข้อกำหนดนี้เลย หรือเนื้อหาไม่เกี่ยวข้องกับการไฟฟ้าฝ่ายผลิตแห่งประเทศไทย evidence ต้องเป็น null

หลักการ:
1. ยอมรับการใช้คำที่มีความหมายเดียวกันหรือใกล้เคียง เช่น "ความเสี่ยง" กับ "risk", "แผนรับมือ" กับ "มาตรการ"
2. evidence ต้องเป็นข้อความที่คัดลอกมาจากเอกสารโดยตรง ห้ามแต่งขึ้นเอง
3. ตอบ "fail" เฉพาะเมื่อเอกสารไม่มีเนื้อหาที่เกี่ยวข้องกับข้อกำหนดนี้จริงๆ ไม่ใช่เพราะใช้คำต่างกัน
4. found_in_document = true เมื่อพบเนื้อหาที่เกี่ยวข้อง แม้จะใช้ภาษาต่างกัน
5. ห้ามใช้ภาษาอังกฤษในการอธิบาย (reasoning_in_thai) ต้องตอบเป็นภาษาไทยเท่านั้น
6. reasoning_in_thai ต้องสั้น 1-2 ประโยคเท่านั้น ห้ามอธิบายยาว
7. evidence ต้องสั้น ไม่เกิน 80 ตัวอักษร

ตอบเป็น JSON เท่านั้น ตามรูปแบบนี้:
{_JSON_FORMAT_EXAMPLE}

DOCUMENT:
{document_text}"""


def _split_chunks(text: str) -> list[str]:
    """Split document text into overlapping chunks of CHUNK_SIZE characters."""
    if len(text) <= CHUNK_SIZE:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def _extract_json(text: str) -> dict:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fenced:
        text = fenced.group(1)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Truncated JSON fallback: extract fields individually via regex
    status_m = re.search(r'"status"\s*:\s*"(pass|fail)"', text)
    reasoning_m = re.search(r'"reasoning_in_thai"\s*:\s*"([^"]*)', text)
    evidence_m = re.search(r'"evidence"\s*:\s*"([^"]*)', text)
    found_m = re.search(r'"found_in_document"\s*:\s*(true|false)', text)

    return {
        "status": status_m.group(1) if status_m else "fail",
        "reasoning_in_thai": reasoning_m.group(1) if reasoning_m else "",
        "evidence": evidence_m.group(1) if evidence_m else None,
        "found_in_document": found_m.group(1) == "true" if found_m else (status_m is not None and status_m.group(1) == "pass"),
    }


def _is_thai(text: str) -> bool:
    """Return True if text contains a meaningful amount of Thai characters."""
    if not text:
        return True  # empty is fine, no retry needed
    thai_chars = sum(1 for c in text if "\u0e00" <= c <= "\u0e7f")
    return thai_chars / len(text) >= 0.15  # at least 15% Thai script


async def _check_chunk(
    client: httpx.AsyncClient,
    chunk: str,
    section_title: str,
    requirement: str,
) -> dict:
    prompt = _build_single_prompt(chunk, section_title, requirement)
    response = await client.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "system": "คุณตอบเป็นภาษาไทยเท่านั้น ห้ามใช้ภาษาอังกฤษในคำอธิบาย",
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": OLLAMA_OPTIONS,
        },
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    raw = response.json()
    llm_text = raw.get("response", "")
    print(f"[DEBUG] done_reason={raw.get('done_reason')} ctx_used={raw.get('prompt_eval_count')} gen_tokens={raw.get('eval_count')} raw_response={repr(llm_text[:120])}")
    result = _extract_json(llm_text)
    if "reasoning_in_thai" in result:
        result["reasoning"] = result.pop("reasoning_in_thai")
    elif "reasoning" not in result:
        result["reasoning"] = ""

    # If reasoning came back in English, retry once with a stronger instruction
    if not _is_thai(result.get("reasoning", "")):
        print(f"[WARN] Reasoning not in Thai, retrying with stronger instruction...")
        retry_prompt = (
            "!!!สำคัญมาก: ตอบเป็นภาษาไทยเท่านั้น ห้ามใช้ภาษาอังกฤษโดยเด็ดขาด!!!\n\n"
            + prompt
        )
        retry_response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "system": "ห้ามตอบเป็นภาษาอังกฤษ ตอบเป็นภาษาไทยเท่านั้น",
                "prompt": retry_prompt,
                "stream": False,
                "format": "json",
                "options": OLLAMA_OPTIONS,
            },
            timeout=OLLAMA_TIMEOUT,
        )
        retry_response.raise_for_status()
        retry_text = retry_response.json().get("response", "")
        retry_result = _extract_json(retry_text)
        if "reasoning_in_thai" in retry_result:
            retry_result["reasoning"] = retry_result.pop("reasoning_in_thai")
        elif "reasoning" not in retry_result:
            retry_result["reasoning"] = ""
        if _is_thai(retry_result.get("reasoning", "")):
            result = retry_result

    return result


async def _check_single_item(
    client: httpx.AsyncClient,
    document_text: str,
    section_title: str,
    requirement: str,
) -> dict:
    chunks = _split_chunks(document_text)
    best = {"status": "fail", "reasoning": "", "evidence": None}
    try:
        for i, chunk in enumerate(chunks):
            result = await _check_chunk(client, chunk, section_title, requirement)
            status = result.get("status", "fail")
            print(f"[DEBUG] '{requirement[:40]}' chunk {i+1}/{len(chunks)} → {status}")
            if status == "pass":
                return result
        return best
    except Exception as e:
        print(f"[ERROR] Failed checking '{requirement[:40]}': {type(e).__name__}: {e}")
        return {"status": "fail", "reasoning": f"เกิดข้อผิดพลาด: {e}", "evidence": None}


async def analyze_with_llm(document_text: str, checklist: list[dict]) -> dict:
    """Check each sub-item individually against the document."""
    print(f"[DEBUG] Checklist received: {json.dumps(checklist, ensure_ascii=False)}")

    results = []
    async with httpx.AsyncClient() as client:
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
