# Risk File Checker — ระบบตรวจสอบเอกสาร PDF

ระบบตรวจสอบเอกสาร PDF ว่ามีเนื้อหาครบถ้วนตามข้อกำหนดที่ผู้ใช้กำหนด
รองรับทั้ง Local AI (Gemma 4 ผ่าน Ollama) และ Cloud AI (Gemini, OpenAI)

---

## ความต้องการของระบบ

- Windows 10 / 11
- RAM อย่างน้อย **8 GB** (ถ้าใช้ Local AI แนะนำ 32 GB ขึ้นไป)
- พื้นที่ว่างอย่างน้อย **20 GB** เฉพาะกรณีใช้ Local AI (โมเดล Gemma 4)

---

# วิธีติดตั้งโปรแกรม

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

## ขั้นตอนที่ 2 เลือก AI ที่จะใช้งาน

โปรแกรมรองรับ AI 3 ประเภท:

| ประเภท | ข้อดี | ข้อจำกัด |
|---|---|---|
| **Local AI** (Gemma 4 ผ่าน Ollama) | ข้อมูลไม่ออกนอกเครื่อง | ต้องการ RAM สูง ทำงานช้ากว่า |
| **Gemini** (Google) | เร็ว แม่นยำ | ต้องการ API Key และอินเทอร์เน็ต |
| **OpenAI** (GPT) | เร็ว แม่นยำ | ต้องการ API Key และอินเทอร์เน็ต |

### ติดตั้ง Ollama (เฉพาะกรณีต้องการใช้ Local AI)

1. เปิดเบราว์เซอร์ไปที่ https://ollama.com
2. คลิก **"Download"** และเลือก **Windows**
3. เปิดไฟล์ `OllamaSetup.exe` แล้วกด Install
4. หลังติดตั้งเสร็จ Ollama จะทำงานอยู่เบื้องหลังอัตโนมัติ (มีไอคอนแสดงใน System Tray)
5. ดาวน์โหลดโมเดล Gemma 4 โดยเปิด Command Prompt แล้วพิมพ์:
   ```
   ollama pull gemma4:26b
   ```
   > การดาวน์โหลดครั้งแรกจะใช้เวลา 10–20 นาที ขนาดประมาณ 18 GB

---

## ขั้นตอนที่ 3 เลือกวิธีติดตั้งโปรแกรม

### วิธีที่ 1 ดาวน์โหลด EXE (แนะนำ)

1. ไปที่หน้า **[Releases](https://github.com/Portrate/EGAT-Risk-File-Checker/releases/)** ของ GitHub
2. ดาวน์โหลดไฟล์ **`RiskFileChecker.exe`** จาก Assets
3. เปิดไฟล์ `RiskFileChecker.exe`
4. ถ้า Windows แจ้งเตือน **"Windows protected your PC"** → คลิก **"More info"** → **"Run anyway"**
5. โปรแกรมจะตรวจสอบ Ollama และเปิดเบราว์เซอร์ให้อัตโนมัติ

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
3. โปรแกรมจะสร้าง environment, ติดตั้ง library, ตรวจสอบ Ollama และเปิดเบราว์เซอร์อัตโนมัติ

---

## การใช้งาน

1. **กรอก Checklist และคะแนน** เพิ่มหัวข้อใหญ่และหัวข้อย่อยที่ต้องการตรวจสอบ สามารถบันทึกหัวข้อใหญ่และหัวข้อย่อยเพื่อใช้ในครั้งต่อไปได้
2. **อัปโหลด PDF** ลากไฟล์มาวางหรือคลิกเลือกไฟล์
3. **เลือก AI Model** เลือก Local AI, Gemini หรือ OpenAI พร้อมกรอก API Key (ถ้าใช้ Cloud AI) และสามารถเพิ่มโมเดลอื่นๆ เพิ่มเติมได้
4. **กด "ตรวจสอบ"** ระบบจะวิเคราะห์และแสดงผล
5. **ระบบแสดงผลลัพธ์** แต่ละหัวข้อแสดงสถานะ ผ่าน / ไม่ผ่าน พร้อมหลักฐานจากเอกสาร และคะแนนรวม

---

## การปิดโปรแกรม

กด `Ctrl + C` ในหน้าต่าง Command Prompt

---

## แก้ไขปัญหาเบื้องต้น

| ปัญหา | วิธีแก้ |
|---|---|
| Windows เตือน "protected your PC" | คลิก **"More info"** → **"Run anyway"** |
| Local AI ไม่พร้อมใช้งาน | ติดตั้ง Ollama และรัน `ollama pull gemma4:26b` หรือใช้ Gemini / OpenAI แทน |
| เชื่อมต่อ Ollama ไม่ได้ | ตรวจสอบว่ามีไอคอน Ollama ใน System Tray ถ้าไม่มีให้เปิด Ollama ก่อน |
| หน้าเว็บไม่เปิด | เปิดเบราว์เซอร์แล้วพิมพ์ `http://localhost:8000` ด้วยตนเอง |
| ผลลัพธ์แสดงช้า (Local AI) | ควรมี RAM อย่างน้อย 16 GB ถ้ามี GPU จะทำงานได้เร็วขึ้น |
| `Port 8000 already in use` | รีสตาร์ทเครื่องหรือปิดโปรแกรมอื่นที่ใช้ port 8000 |
| `Python not found` (วิธีที่ 2) | ติดตั้ง Python ใหม่โดยติ๊ก **"Add Python to PATH"** |
| PDF ที่เป็นภาพสแกนอ่านไม่ออก | ติดตั้ง Tesseract ตามขั้นตอนที่ 1 และอย่าลืมติ๊ก **"Thai"** ระหว่างติดตั้ง |
| OCR อ่านภาษาไทยไม่ได้ | ถอนการติดตั้ง Tesseract แล้วติดตั้งใหม่ โดยติ๊ก **"Thai"** ใน Additional language data |

---

# Architecture

แอปพลิเคชันนี้ใช้ **FastAPI** (ทำงานบน **Uvicorn**) เป็น Backend web framework ทำหน้าที่ให้บริการทั้ง API endpoint และ UI
UI สร้างด้วย HTML, CSS และ Vanilla JavaScript โดยใช้ Jinja2 templates

สำหรับการวิเคราะห์ด้วย AI รองรับ 3 ช่องทาง ได้แก่ **Ollama** (Local) ที่ `localhost:11434`, **Gemini API** และ **OpenAI API** โดยผู้ใช้เลือก Model ได้ผ่าน UI และ Backend เรียกใช้งานผ่าน **httpx** ทั้งหมด
โมเดล Local AI ที่ใช้คือ **Gemma 4 (26B)** จาก Google

การดึงข้อความจาก PDF ดำเนินการโดยใช้ **PyMuPDF** (Python wrapper สำหรับ MuPDF) ซึ่งอ่านแต่ละหน้าและดึงข้อความที่เลือกได้ออกมา สำหรับหน้าที่เป็นภาพสแกนและไม่มีข้อความดิจิทัล แอปจะ Fallback ไปใช้ **Tesseract OCR** ผ่าน **pytesseract** และ **Pillow** เพื่ออ่านข้อความจากภาพของหน้านั้น ๆ โดย Tesseract เป็น Optional (แอปยังทำงานได้ปกติกับ PDF ที่มีข้อความดิจิทัลโดยไม่ต้องติดตั้ง)

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
              │  if page text < 100 chars → OCR via Tesseract (thai+english)
              │  output: plain text
              ▼
         orchestrator.analyze_with_llm()
              │  loops over each checklist section and each sub-item
              │  splits document into 24,000 char chunks (2,000 char overlap)
              │  calls Ollama / Gemini / OpenAI per chunk until a "pass" is found
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

**`run.py`** — ไฟล์สำหรับเปิดโปรแกรม ใช้โดย `.exe` และ `start.bat`.
1. ตรวจสอบว่ามีคำสั่ง `ollama` อยู่ใน PATH หรือไม่ (ข้ามหากไม่พบ)
2. ตรวจสอบ `localhost:11434` ว่า Ollama กำลังทำงานอยู่ ถ้าไม่ได้ทำงานจะสั่ง ollama serve
3. ตรวจสอบว่าดาวน์โหลด `gemma4:26b` ไว้แล้วหรือไม่ (ไม่ดาวน์โหลดอัตโนมัติ)
4. เปิดเบราว์เซอร์หลังจากรอ 2 วินาที แล้วส่งต่อการทำงานให้ uvicorn

**`main.py`**:
- `GET /` — แสดงหน้า `index.html` ผ่าน Jinja2
- `POST /analyze` — ตรวจสอบ PDF และ JSON ของรายการที่ตรวจสอบ เรียกใช้ orchestrator รวบรวมคะแนน แล้วส่งผลลัพธ์เป็น JSON
- `POST /export/excel` — รับผลลัพธ์ที่คำนวณแล้วจากเบราว์เซอร์ แล้วส่งออกเป็นไฟล์ `.xlsx`
- `GET /health` — ตรวจสอบสถานะการเชื่อมต่อของ Ollama และโมเดลที่กำหนดไว้

**`checker/pdf_extractor.py`** — ใช้ `PyMuPDF` (`fitz`) อ่านแต่ละหน้า หน้าที่มีข้อความน้อยกว่า 100 ตัวอักษรถือว่าเป็นภาพสแกน จะส่งผ่าน Tesseract OCR เพื่อแปลงเป็นตัวอักษร โดยรองรับทั้งภาษาไทยและภาษาอังกฤษ ผลลัพธ์จะถูกรวมเป็นบล็อก

**`checker/orchestrator.py`** — Core LLM logic:
- `_split_chunks()` — แบ่งข้อความทั้งหมดเป็นชิ้น ชิ้นละ 24,000 ตัวอักษร มีส่วนทับซ้อน 2,000 ตัวอักษร เพื่อไม่ให้เนื้อหาตรงขอบรอยต่อหายไป
- `_check_chunk()` — ส่งไปยัง Ollama, Gemini หรือ OpenAI ตามโมเดลที่เลือก หากโมเดลตอบกลับเป็นภาษาอังกฤษจะแยกผลลัพธ์ และลองใหม่อีกครั้งด้วยคำสั่งภาษาไทย
- `_check_single_item()` — วนตรวจสอบข้อความแต่ละชิ้น คืนค่า `"pass"` หากพบ หรือ `"fail"` หากไม่พบ
- `_extract_json()` — จัดการผลลัพธ์ที่ส่งกลับมาในรูปแบบที่ไม่ถูกต้อง ลอง `json.loads` ก่อน แล้วใช้ regex ในกรณีที่ผลลัพธ์ถูกตัด
- `_sanitize_reasoning()` — ตรวจหาการวนซ้ำของตัวอักษร คำที่ซ้ำกัน และคำอังกฤษแปลกปลอม แล้วตัดทิ้ง
- `analyze_with_llm()` — Top-level function เรียกใช้โดย `main.py` เพื่อ วนตรวจสอบทุกหมวดและรายการตามลำดับ

**`checker/models.py`** — ตรวจสอบรายการขาเข้า (`ChecklistSection` → `ChecklistItem` with `name` + `score`) และขาออก (`ItemResult`, `SectionResult`, `AnalysisResponse`).

**`checker/excel_exporter.py`** — สร้างไฟล์ `.xlsx` โดยใช้ `openpyxl` ประกอบด้วย 2 ชีท ชีทที่ 1 เป็นตารางสรุป ชีทที่ 2 เป็นรายละเอียดของแต่ละรายการย่อยที่ตรวจสอบ

---

### LLM Configuration (`orchestrator.py`)

| Parameter | Value | Notes |
|---|---|---|
| Default model | `gemma4:26b` | change `MODEL` constant or select via UI |
| Context window | 32,768 tokens | `num_ctx` in `OLLAMA_OPTIONS` (Ollama only) |
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

ใช้ PyInstaller โดยสามารถรัน `run.py` ซึ่งจะรวม `static/`, `templates/` และ `checker/` ไว้ในไฟล์เดียวชื่อ `RiskFileChecker.exe` ในโฟลเดอร์ `dist/`.
