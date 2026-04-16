import re
from pathlib import Path

import fitz  # pymupdf


def _clean_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph breaks."""
    # Collapse runs of spaces/tabs but keep newlines
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse more than two consecutive newlines into two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _doc_to_text(doc: fitz.Document) -> str:
    """Convert an open fitz Document to plain text with page markers."""
    pages: list[str] = []
    for page_num, page in enumerate(doc, start=1):
        raw = page.get_text("text")  # plain-text layout
        cleaned = _clean_text(raw)
        if cleaned:
            pages.append(f"[หน้า {page_num}]\n{cleaned}")
    return "\n\n".join(pages)


def extract_text_from_path(pdf_path: str | Path) -> str:
    """Extract text from a PDF file on disk.

    Returns plain text with ``[หน้า N]`` markers for each page.
    Raises FileNotFoundError if the path does not exist.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with fitz.open(str(pdf_path)) as doc:
        return _doc_to_text(doc)


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extract text from raw PDF bytes (e.g. from an uploaded file).

    Returns plain text with ``[หน้า N]`` markers for each page.
    """
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        return _doc_to_text(doc)


def extract_pages_from_bytes(pdf_bytes: bytes) -> list[dict]:
    """Return a list of dicts, one per page: ``{"page": N, "text": ...}``.

    Useful for RAG chunking — each page becomes an independent chunk.
    """
    pages: list[dict] = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page_num, page in enumerate(doc, start=1):
            raw = page.get_text("text")
            cleaned = _clean_text(raw)
            if cleaned:
                pages.append({"page": page_num, "text": cleaned})
    return pages


def extract_pages_from_path(pdf_path: str | Path) -> list[dict]:
    """Return a list of dicts, one per page: ``{"page": N, "text": ...}``.

    Useful for indexing reference documents into ChromaDB.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: list[dict] = []
    with fitz.open(str(pdf_path)) as doc:
        for page_num, page in enumerate(doc, start=1):
            raw = page.get_text("text")
            cleaned = _clean_text(raw)
            if cleaned:
                pages.append({"page": page_num, "text": cleaned})
    return pages
