import json
import re

import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:e4b"

# Truncate document to this many characters to stay within the model context window.
# Gemma 4 has a 128k context, but large prompts slow inference significantly.
MAX_DOC_CHARS = 24_000


def build_prompt(document_text: str, checklist: list[dict]) -> str:
    if len(document_text) > MAX_DOC_CHARS:
        document_text = (
            document_text[:MAX_DOC_CHARS]
            + "\n\n[เอกสารถูกตัดทอนเนื่องจากความยาวเกินกำหนด]"
        )

    checklist_json = json.dumps(checklist, ensure_ascii=False, indent=2)

    return f"""You are a document compliance checker. Your task is to check whether each item in the CHECKLIST is present in the DOCUMENT.

You MUST respond in THAI language using EXACTLY this JSON structure — do not change the key names, do not add extra keys:

{{
  "results": [
    {{
      "section": "SECTION_TITLE",
      "items": [
        {{
          "requirement": "ITEM_TEXT",
          "status": "pass",
          "reasoning": "EXPLANATION_IN_THAI",
          "evidence": "SHORT_QUOTE_OR_null"
        }}
      ]
    }}
  ]
}}

Rules:
- "results" must be an array, one entry per checklist section
- "section" = the section title exactly as given in the checklist
- "items" = array of results, one per sub-item in that section
- "status" must be exactly one of: "pass", "partial", "fail"
  - "pass" = item is clearly present in the document
  - "partial" = item is partially addressed
  - "fail" = item is absent from the document
- "reasoning" = 1-2 sentences in Thai explaining the decision
- "evidence" = a direct quote (≤100 chars) from the document if found, otherwise the JSON value null (not the string "null")

DOCUMENT:
{document_text}

CHECKLIST:
{checklist_json}

Now output ONLY the JSON object. No explanation, no markdown, no extra text."""


def _extract_json(text: str) -> dict:
    """Parse JSON from the LLM response, tolerating markdown fences."""
    text = text.strip()
    # Strip ```json ... ``` fences if present
    fenced = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fenced:
        text = fenced.group(1)
    return json.loads(text)


_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["results"],
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["section", "items"],
                "properties": {
                    "section": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["requirement", "status", "reasoning", "evidence"],
                            "properties": {
                                "requirement": {"type": "string"},
                                "status": {"type": "string", "enum": ["pass", "partial", "fail"]},
                                "reasoning": {"type": "string"},
                                "evidence": {"type": ["string", "null"]},
                            },
                        },
                    },
                },
            },
        }
    },
}


async def analyze_with_llm(document_text: str, checklist: list[dict]) -> dict:
    """Send document + checklist to Ollama and return the parsed result dict."""
    prompt = build_prompt(document_text, checklist)

    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "format": _RESPONSE_SCHEMA,
            },
        )
        response.raise_for_status()

    raw = response.json()
    llm_text = raw.get("response", "")
    print(f"[DEBUG] LLM raw response (first 300 chars):\n{llm_text[:300]}")
    result = _extract_json(llm_text)
    print(f"[DEBUG] Parsed result keys: {list(result.keys())}")
    print(f"[DEBUG] Number of sections in results: {len(result.get('results', []))}")
    return result
