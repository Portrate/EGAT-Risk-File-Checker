import json
import re

import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:26b"
OLLAMA_TIMEOUT = httpx.Timeout(connect=30.0, read=1200.0, write=60.0, pool=10.0)
OLLAMA_OPTIONS = {"num_ctx": 32768, "num_predict": 256, "temperature": 0, "repeat_penalty": 1.3, "repeat_last_n": 64}

CHUNK_SIZE = 24_000      # characters per chunk sent to LLM
CHUNK_OVERLAP = 2_000   # overlap between consecutive chunks to avoid missing content at boundaries

_JSON_FORMAT_EXAMPLE = """{
  "status": "pass หรือ fail",
  "reasoning_in_thai": "1-2 ประโยคสั้นๆ เป็นภาษาไทยเท่านั้น",
  "evidence": "ข้อความจากเอกสาร ไม่เกิน 80 ตัวอักษร หรือ null ถ้าไม่พบ",
  "found_in_document": true
}"""


def _build_single_prompt(document_text: str, section_title: str, requirement: str) -> str:
    return f"""คุณคือระบบตรวจสอบเอกสารที่เข้มงวด หน้าที่ของคุณคือตรวจสอบว่าเอกสารมีเนื้อหาครอบคลุมข้อกำหนดที่ระบุอย่างชัดเจนหรือไม่

หัวข้อ: {section_title}
ข้อกำหนด: {requirement}

เกณฑ์การตัดสิน (เข้มงวด):
- "pass" = เอกสารมีเนื้อหาที่ระบุถึงข้อกำหนดนี้อย่างชัดเจนและเฉพาะเจาะจง ต้องระบุ evidence เป็นข้อความจากเอกสารที่อ้างอิงได้
- "fail" = เอกสารไม่มีเนื้อหาที่กล่าวถึงข้อกำหนดนี้อย่างชัดเจน หรือมีเพียงการกล่าวถึงแบบผ่านๆ โดยไม่มีสาระสำคัญ หรือเนื้อหาไม่ตรงกับข้อกำหนดที่ถามอย่างแท้จริง evidence ต้องเป็น null

หลักการ (ต้องปฏิบัติตามอย่างเคร่งครัด):
1. เอกสารต้องกล่าวถึงประเด็นในข้อกำหนดอย่างชัดเจนและตรงประเด็น ไม่ใช่แค่กล่าวถึงหัวข้อทั่วไปที่เกี่ยวข้อง
2. หากเอกสารกล่าวถึงหัวข้อกว้างๆ แต่ไม่ได้ระบุรายละเอียดที่ข้อกำหนดต้องการ ให้ตอบ "fail"
3. หากไม่มีข้อความจากเอกสารที่พิสูจน์ว่าครอบคลุมข้อกำหนดได้โดยตรง ให้ตอบ "fail"
4. เมื่อสงสัย ให้เลือก "fail" เสมอ
5. evidence ต้องเป็นข้อความจากเอกสารโดยตรง ห้ามแต่งขึ้นเอง ต้องอ้างอิงได้จริง
6. found_in_document = true เฉพาะเมื่อพบหลักฐานชัดเจนในเอกสาร
7. ห้ามใช้ภาษาอังกฤษในการอธิบาย ต้องตอบเป็นภาษาไทยเท่านั้น
8. reasoning_in_thai ต้องสั้น 1-2 ประโยคเท่านั้น ห้ามอธิบายยาว
9. evidence ต้องสั้น ไม่เกิน 80 ตัวอักษร

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


def _sanitize_reasoning(text: str) -> str:
    """Truncate at the first sign of repetition or artifact — char-level or word-level."""
    if not text:
        return text

    # 1. Character-level exact loop (e.g. /Dok/Dok/Dok or _en_en_en)
    m = re.search(r"(.{3,20})\1{3,}", text)
    if m:
        return text[: m.start()].rstrip(" /_.,-")

    # 2. English artifact words appearing inside Thai text (PDF redaction markers etc.)
    artifact = re.search(r"\b(Erased|Redacted|Dok)\b", text)
    if artifact:
        return text[: artifact.start()].rstrip()

    # 3. Word-level phrase repetition: any Thai word (4+ chars) appearing 3+ times,
    #    or any bigram (8+ chars) appearing 2+ times — truncate before the 2nd/3rd hit.
    words = text.split()
    word_positions: dict[str, list[int]] = {}
    pos = 0
    for w in words:
        if len(w) >= 4:
            word_positions.setdefault(w, []).append(pos)
        pos += len(w) + 1  # +1 for the space

    cutoff = len(text)
    for w, positions in word_positions.items():
        if len(positions) >= 3:
            cutoff = min(cutoff, positions[2])  # start of 3rd occurrence
        elif len(positions) >= 2 and len(w) >= 8:
            cutoff = min(cutoff, positions[1])  # start of 2nd occurrence of long phrase

    if cutoff < len(text):
        return text[:cutoff].rstrip()

    return text


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
        result["reasoning"] = _sanitize_reasoning(result.pop("reasoning_in_thai"))
    elif "reasoning" not in result:
        result["reasoning"] = ""
    else:
        result["reasoning"] = _sanitize_reasoning(result["reasoning"])

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
            retry_result["reasoning"] = _sanitize_reasoning(retry_result.pop("reasoning_in_thai"))
        elif "reasoning" not in retry_result:
            retry_result["reasoning"] = ""
        else:
            retry_result["reasoning"] = _sanitize_reasoning(retry_result["reasoning"])
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
            for req_item in section.get("items", []):
                requirement = req_item.get("name", "")
                score = req_item.get("score", 0.0)
                check = await _check_single_item(client, document_text, section_title, requirement)
                items_out.append({
                    "requirement": requirement,
                    "score": score,
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
