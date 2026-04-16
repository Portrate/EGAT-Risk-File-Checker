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

    return f"""You are a document compliance checker. Analyze the document below and determine whether each required checklist item is present in the document. Respond with valid JSON only — no prose, no markdown fences.

DOCUMENT:
{document_text}

CHECKLIST:
{checklist_json}

For every checklist item produce:
- status: "pass" if clearly present, "partial" if partially addressed, "fail" if absent
- reasoning: one or two sentences in Thai explaining the decision
- evidence: a short direct quote (≤ 100 characters) from the document that supports the decision, or null if none found

Respond ONLY with this JSON structure:
{{
  "results": [
    {{
      "section": "<section title from checklist>",
      "items": [
        {{
          "requirement": "<item text from checklist>",
          "status": "pass",
          "reasoning": "<Thai explanation>",
          "evidence": "<quote or null>"
        }}
      ]
    }}
  ]
}}"""


def _extract_json(text: str) -> dict:
    """Parse JSON from the LLM response, tolerating markdown fences."""
    text = text.strip()
    # Strip ```json ... ``` fences if present
    fenced = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fenced:
        text = fenced.group(1)
    return json.loads(text)


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
                "format": "json",
            },
        )
        response.raise_for_status()

    raw = response.json()
    return _extract_json(raw["response"])
