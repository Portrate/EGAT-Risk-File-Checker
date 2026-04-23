# Risk File Checker — ระบบตรวจสอบเอกสาร PDF

ระบบตรวจสอบเอกสาร PDF ว่ามีเนื้อหาครบถ้วนตามข้อกำหนดที่ผู้ใช้กำหนด
โดยใช้ Local LLM (Gemma 4) เพื่อรักษาความลับของข้อมูล

---

## ความต้องการของระบบ

- Windows 10 / 11
- RAM อย่างน้อย **16 GB** (แนะนำ 32 GB ขึ้นไป)
- พื้นที่ว่างอย่างน้อย **20 GB** (สำหรับโมเดล AI)

---

## ขั้นตอนที่ 1 ติดตั้ง Tesseract OCR (สำหรับ PDF ที่เป็นรูปภาพ)

Tesseract ช่วยให้โปรแกรมอ่านข้อความจากหน้า PDF ที่เป็นภาพสแกน

1. เปิดเบราว์เซอร์ไปที่ https://github.com/UB-Mannheim/tesseract/wiki
2. ดาวน์โหลดไฟล์ **`tesseract-ocr-w64-setup-*.exe`** (เวอร์ชันล่าสุด)
3. เปิดไฟล์ติดตั้ง → กด Next จนถึงหน้า **"Choose Components"**
4. ขยาย **"Additional language data"** แล้วติ๊กถูกที่ **"Thai"**
5. ติ๊กถูกที่ **"Add to PATH"** (ถ้ามีให้เลือก) แล้วกด Install
6. ตรวจสอบโดยเปิด Command Prompt แล้วพิมพ์:
   ```
   tesseract --version
   ```
   ถ้าแสดงเลขเวอร์ชันแสดงว่าติดตั้งสำเร็จ

> **หมายเหตุ:** ถ้าไม่ติดตั้ง Tesseract โปรแกรมยังใช้งานได้ปกติกับ PDF ที่มีข้อความดิจิทัล
> แต่จะอ่านหน้าที่เป็นภาพสแกนไม่ได้

---

## ขั้นตอนที่ 2 ติดตั้ง Ollama

Ollama คือโปรแกรมที่ใช้รัน AI บนเครื่อง ต้องติดตั้งก่อนเสมอ

1. เปิดเบราว์เซอร์ไปที่ https://ollama.com
2. คลิก **"Download"** และเลือก **Windows**
3. เปิดไฟล์ `OllamaSetup.exe` แล้วกด Install
4. หลังติดตั้งเสร็จ Ollama จะทำงานอยู่เบื้องหลังอัตโนมัติ (มีไอคอนแสดงใน System Tray)
5. ตรวจสอบโดยเปิด Command Prompt แล้วพิมพ์:
   ```
   ollama --version
   ```
   ถ้าแสดงเลขเวอร์ชันแสดงว่าติดตั้งสำเร็จ

---

## ขั้นตอนที่ 3 เลือกวิธีติดตั้งโปรแกรม

### วิธีที่ 1 ดาวน์โหลด EXE (แนะนำ)

1. ไปที่หน้า **[Releases](https://github.com/Portrate/EGAT-Risk-File-Checker/releases/)** ของ GitHub
2. ดาวน์โหลดไฟล์ **`RiskFileChecker.exe`** จาก Assets
3. เปิดไฟล์ `RiskFileChecker.exe`
4. ถ้า Windows แจ้งเตือน **"Windows protected your PC"** → คลิก **"More info"** → **"Run anyway"**
5. โปรแกรมจะตรวจสอบ Ollama และดาวน์โหลดโมเดล AI โดยอัตโนมัติ และเปิดเบราว์เซอร์ให้เอง

> **หมายเหตุ:** การเปิดครั้งแรกอาจใช้เวลา 10–20 นาที เพื่อดาวน์โหลดโมเดล Gemma 4
> ครั้งต่อไปจะใช้เวลาเปิดเร็ว

---

### วิธีที่ 2 ใช้ start.bat (ต้องติดตั้ง Python)

#### ติดตั้ง Python

1. เปิดเบราว์เซอร์ไปที่ https://www.python.org/downloads/
2. คลิก **"Download Python 3.x.x"** (เวอร์ชันล่าสุด)
3. เปิดไฟล์ติดตั้ง ติ๊กถูกที่ **"Add Python to PATH"** ก่อนกด Install
4. ตรวจสอบโดยเปิด Command Prompt แล้วพิมพ์:
   ```
   python --version
   ```

#### ดาวน์โหลดและรัน

1. คลิกปุ่มสีเขียว **Code** → **Download ZIP** แล้วแตกไฟล์
2. ดับเบิลคลิกที่ **`start.bat`**
3. โปรแกรมจะสร้าง environment, ติดตั้ง library, ตรวจสอบโมเดล และเปิดเบราว์เซอร์อัตโนมัติ

---

## การใช้งาน

1. **กรอก Checklist และคะแนน** เพิ่มหัวข้อใหญ่และหัวข้อย่อยที่ต้องการตรวจสอบ
2. **อัปโหลด PDF** ลากไฟล์มาวางหรือคลิกเลือกไฟล์
3. **กด "ตรวจสอบ"** ระบบจะวิเคราะห์และแสดงผล
4. **ผลลัพธ์** แต่ละหัวข้อแสดงสถานะ ผ่าน / ไม่ผ่าน พร้อมหลักฐานจากเอกสาร และคะแนนรวม

---

## การปิดโปรแกรม

กด `Ctrl + C` ในหน้าต่าง Command Prompt

---

## แก้ไขปัญหาเบื้องต้น

| ปัญหา | วิธีแก้ |
|---|---|
| Windows เตือน "protected your PC" | คลิก **"More info"** → **"Run anyway"** |
| `Ollama not found` | ติดตั้ง Ollama จาก https://ollama.com แล้วรีสตาร์ท |
| เชื่อมต่อ Ollama ไม่ได้ | ตรวจสอบว่ามีไอคอน Ollama ใน System Tray ถ้าไม่มีให้เปิด Ollama ก่อน |
| หน้าเว็บไม่เปิด | เปิดเบราว์เซอร์แล้วพิมพ์ `http://localhost:8000` ด้วยตนเอง |
| โมเดลดาวน์โหลดช้า | ขึ้นอยู่กับความเร็วอินเทอร์เน็ต รอโหลดจนเสร็จ |
| ผลลัพธ์แสดงช้า | ควรมี RAM อย่างน้อย 16 GB ถ้ามี GPU จะทำงานได้เร็วขึ้น |
| `Port 8000 already in use` | รีสตาร์ทเครื่องหรือปิดโปรแกรมอื่นที่ใช้ port 8000 |
| `Python not found` (วิธีที่ 2) | ติดตั้ง Python ใหม่โดยติ๊ก **"Add Python to PATH"** |
| PDF ที่เป็นภาพสแกนอ่านไม่ออก | ติดตั้ง Tesseract ตามขั้นตอนที่ 1 และอย่าลืมติ๊ก **"Thai"** ระหว่างติดตั้ง |
| OCR อ่านภาษาไทยไม่ได้ | ถอนการติดตั้ง Tesseract แล้วติดตั้งใหม่ โดยติ๊ก **"Thai"** ใน Additional language data |

---

## Architecture

แอปพลิเคชันนี้ถูกออกแบบให้ทำงานภายในเครื่อง (Local) ทั้งหมด โดยใช้ **FastAPI** (ทำงานบน **Uvicorn**) เป็น Backend web framework ทำหน้าที่ให้บริการทั้ง API endpoint และ UI\
UI สร้างด้วย HTML, CSS และ Vanilla JavaScript โดยใช้ Jinja2 templates

สำหรับการวิเคราะห์ด้วย AI นั้น Backend จะสื่อสารกับ **Ollama** ซึ่งเป็น Runtime สำหรับรัน LLM บนเครื่องของผู้ใช้โดยตรง Ollama เปิด REST API ที่ `localhost:11434` และ Backend เรียกใช้งานผ่าน **httpx**\
โมเดลที่ใช้วิเคราะห์คือ **Gemma 4 (26B)** จาก Google ที่มีความสามารถในการเข้าใจเอกสารภาษาไทยได้ดี

การดึงข้อความจาก PDF ดำเนินการโดยใช้ **pymupdf** (Python wrapper สำหรับ MuPDF) ซึ่งอ่านแต่ละหน้าและดึงข้อความที่เลือกได้ออกมา สำหรับหน้าที่เป็นภาพสแกนและไม่มีข้อความดิจิทัล แอปจะ Fallback ไปใช้ **Tesseract OCR** ผ่าน **pytesseract** และ **Pillow** เพื่ออ่านข้อความจากภาพของหน้านั้น ๆ โดย Tesseract เป็น Optional (แอปยังทำงานได้ปกติกับ PDF ที่มีข้อความดิจิทัลโดยไม่ต้องติดตั้ง)

ข้อมูล Checklist ที่ส่งเข้ามาจะถูกตรวจสอบความถูกต้องด้วย **Pydantic** ก่อนประมวลผล หากโครงสร้างไม่ถูกต้อง ผู้ใช้จะได้รับ HTTP 422 error

ฟีเจอร์ส่งออก Excel ใช้ **openpyxl** สร้างไฟล์ `.xlsx`

แอปพลิเคชันทั้งหมดถูกแพ็กเป็นไฟล์ `.exe` ไฟล์เดียวด้วย **PyInstaller** ทำให้ผู้ใช้ไม่จำเป็นต้องติดตั้ง Python

---

## โครงสร้างและการทำงานของโค้ด

### Project Structure

```
EGAT-Risk-File-Checker/
├── run.py                      ← entry point (EXE / python run.py)
├── main.py                     ← FastAPI app + API routes
├── build.bat                   ← PyInstaller build script
├── requirements.txt
│
├── checker/
│   ├── models.py               ← Pydantic request/response schemas
│   ├── pdf_extractor.py        ← PDF to plain text (native + OCR fallback)
│   ├── orchestrator.py         ← LLM prompt logic, chunking, result parsing
│   └── excel_exporter.py       ← build .xlsx download response
│
├── static/
│   ├── css/style.css
│   └── js/app.js               ← frontend logic (fetch/analyze, render results)
│
└── templates/
    └── index.html              ← single-page UI served by Jinja2
```

---

### Request Flow

```
Browser
  │  POST /analyze  (PDF file + checklist JSON string)
  ▼
main.py  →  pdf_extractor.extract_text_from_bytes()
              │  pymupdf reads each page
              │  if page text < 50 chars → OCR via Tesseract (thai+english)
              │  output: plain text
              ▼
         orchestrator.analyze_with_llm()
              │  loops over each checklist section and each sub-item
              │  splits document into 24,000 char chunks (2,000 char overlap)
              │  calls Ollama /api/generate per chunk until a "pass" is found
              │  parses JSON from LLM response (_extract_json)
              │  sanitizes reasoning to remove repetition artifacts
              │  retries once if reasoning is not in Thai
              ▼
         main.py  computes summary counts + scores
              ▼
  JSON response  →  Browser renders pass/fail table
```

---

### Files Explained

**`run.py`** — Startup launcher used by the `.exe` and `start.bat`. Before starting uvicorn it:
1. Checks that `ollama` binary exists in PATH
2. Pings `localhost:11434` to confirm Ollama is running, starts `ollama serve` if not
3. Runs `ollama pull gemma4:26b` if the model is not yet downloaded
4. Opens the browser after a 2 second delay, then hands off to uvicorn

**`main.py`**:
- `GET /` — serves `index.html` via Jinja2
- `POST /analyze` — validates the uploaded PDF and checklist JSON, calls the orchestrator, aggregates scores, returns JSON
- `POST /export/excel` — receives the already computed results from the browser and streams back to `.xlsx` file
- `GET /health` — returns Ollama reachability status and the configured model name

**`checker/pdf_extractor.py`** — Uses `pymupdf` (`fitz`) to read each page. If a page has lower than 50 characters of selectable text it is treated as a scanned image and passed through Tesseract OCR at 200 DPI with `thai and english` language. Output is joined as `[หน้า N]\n<text>` blocks.

**`checker/orchestrator.py`** — Core LLM logic:
- `_split_chunks()` — splits the full document text into 24,000 character chunks with 2,000 character overlap so content near chunk boundaries is not missed
- `_check_chunk()` — sends one chunk + one requirement to Ollama and parses the result, retries once with a stronger Thai-only instruction if the model responds in English
- `_check_single_item()` — iterates chunks for a single requirement; returns the first `"pass"` result found, or `"fail"` if none
- `_extract_json()` — handles malformed LLM output: tries `json.loads` first, then falls back to regex field extraction for truncated responses
- `_sanitize_reasoning()` — detects character level loops, repeated words, and English artifact tokens (`Erased`, `Dok`) in the reasoning string and truncates before the first sign of repetition
- `analyze_with_llm()` — top-level function called by `main.py`, iterates all sections and items sequentially (one Ollama call per item per chunk)

**`checker/models.py`** — Pydantic schemas for the inbound checklist (`ChecklistSection` → `ChecklistItem` with `name` + `score`) and the outbound results (`ItemResult`, `SectionResult`, `AnalysisResponse`).

**`checker/excel_exporter.py`** — Builds a two-sheet `.xlsx` workbook using `openpyxl`: Sheet 1 is a summary table; Sheet 2 has one row per checklist item. Returns a `StreamingResponse` with a UTF-8–encoded filename.

---

### LLM Configuration (`orchestrator.py`)

| Parameter | Value | Notes |
|---|---|---|
| Model | `gemma4:26b` | change `MODEL` constant to swap models |
| Context window | 32,768 tokens | `num_ctx` in `OLLAMA_OPTIONS` |
| Max output tokens | 256 | `num_predict` — enough for one JSON object |
| Temperature | 0 | deterministic output |
| Chunk size | 24,000 chars | `CHUNK_SIZE` |
| Chunk overlap | 2,000 chars | `CHUNK_OVERLAP` |
| Read timeout | 1,200 s (20 min) | long documents with many items can be slow |

---

### Building the EXE

```bat
build.bat
```

This runs PyInstaller with `run.py` as the entry point and bundles `static/`, `templates/`, and `checker/` into a single `RiskFileChecker.exe` under `dist/`.
