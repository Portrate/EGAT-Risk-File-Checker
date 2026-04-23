import io
import logging
import re
from pathlib import Path
import fitz  # pymupdf

logger = logging.getLogger(__name__)

# Optional OCR support via Tesseract (pytesseract + Pillow).
# If either package is missing the extractor falls back to native text only.
try:
    import pytesseract
    from PIL import Image as PILImage

    # On Windows the installer puts Tesseract here by default.
    # pytesseract picks it up from PATH first; this is a fallback.
    import sys
    if sys.platform == "win32":
        import shutil
        if not shutil.which("tesseract"):
            pytesseract.pytesseract.tesseract_cmd = (
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )

    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False
    logger.warning(
        "pytesseract / Pillow not installed — OCR disabled. "
        "Run: pip install pytesseract pillow  (and install Tesseract binary)"
    )

# Minimum selectable-text length before we treat a page as image-only.
_OCR_THRESHOLD = 50
# Render DPI for OCR — higher = better accuracy but work slower.
_OCR_DPI = 200
# Tesseract language string. Thai + English.
_OCR_LANG = "tha+eng"


def _clean_text(text: str) -> str:
    # Collapse multiple spaces/tabs on the same line into a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3+ consecutive blank lines into 2 to reduce noise
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _ocr_page(page: fitz.Page) -> str:
    # Render *page* to a bitmap and return OCR text. Returns '' on any error.
    if not _OCR_AVAILABLE:
        return ""
    try:
        # Build a scale matrix from the target DPI (PDF default unit is 72 pt/in)
        mat = fitz.Matrix(_OCR_DPI / 72, _OCR_DPI / 72)
        # Render the PDF page to an RGB pixel map at the scaled resolution
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        # Convert the pixel map to a PIL Image via PNG bytes
        img = PILImage.open(io.BytesIO(pix.tobytes("png")))
        # Run Tesseract OCR and clean up the result text before returning
        text = pytesseract.image_to_string(img, lang=_OCR_LANG)
        return _clean_text(text)
    except Exception as exc:
        logger.warning("OCR failed on page %s: %s", page.number + 1, exc)
        return ""


def _extract_page_text(page: fitz.Page) -> str:
    # Return the best text for a single page, using OCR when needed.
    # Try to get embedded (selectable) text first — much faster than OCR
    native = _clean_text(page.get_text("text"))
    if len(native) >= _OCR_THRESHOLD:
        # Enough native text found; skip OCR
        return native
    # Page has little/no selectable text — try OCR.
    ocr = _ocr_page(page)
    # Fall back to native text if OCR also returns nothing (e.g. truly blank page)
    return ocr if ocr else native


def _doc_to_text(doc: fitz.Document) -> str:
    # Collect non-empty pages and prefix each with its page number label
    pages: list[str] = []
    for page_num, page in enumerate(doc, start=1):
        text = _extract_page_text(page)
        if text:
            pages.append(f"[หน้า {page_num}]\n{text}")
    # Join all pages with a blank line separator
    return "\n\n".join(pages)


def extract_text_from_path(pdf_path: str | Path) -> str:
    # Open a PDF from a file path and return the full concatenated text
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    with fitz.open(str(pdf_path)) as doc:
        return _doc_to_text(doc)


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    # Open a PDF from an in-memory bytes object
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        return _doc_to_text(doc)


def extract_pages_from_bytes(pdf_bytes: bytes) -> list[dict]:
    # Return a list of {"page": n, "text": "..."} for each non-empty page
    pages: list[dict] = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page_num, page in enumerate(doc, start=1):
            text = _extract_page_text(page)
            if text:
                pages.append({"page": page_num, "text": text})
    return pages


def extract_pages_from_path(pdf_path: str | Path) -> list[dict]:
    # Same as extract_pages_from_bytes but reads from a file path instead
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    pages: list[dict] = []
    with fitz.open(str(pdf_path)) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = _extract_page_text(page)
            if text:
                pages.append({"page": page_num, "text": text})
    return pages
