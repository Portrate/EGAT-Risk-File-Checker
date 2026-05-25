# File Checker — ระบบตรวจสอบเอกสาร PDF

ระบบตรวจสอบเอกสาร PDF ว่ามีเนื้อหาครบถ้วนตามข้อกำหนดที่ผู้ใช้กำหนด
รองรับทั้ง Local AI (Gemma 4 ผ่าน Ollama), Cloud AI (Gemini, OpenAI) และ EGAT AI Gateway

[สื่อการนำเสนอ](https://portrate.github.io/EGAT-File-Checker/)

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

| ประเภท | ข้อดี | ข้อเสีย / ข้อจำกัด |
|---|---|---|
| **Local AI** (Gemma 4 ผ่าน Ollama) | • ข้อมูลไม่ออกนอกเครื่อง เหมาะกับเอกสารที่มีความลับ<br>• ไม่มีค่าใช้จ่ายต่อครั้ง ใช้ได้ไม่จำกัด<br>• ใช้งานแบบออฟไลน์ได้<br> | • ต้องการ RAM อย่างน้อย 16 GB (แนะนำ 32 GB) และพื้นที่จัดเก็บข้อมูล ~20 GB<br>• ทำงานช้า โดยเฉพาะถ้าไม่มี GPU<br>• ความแม่นยำต่ำกว่าโมเดล Cloud<br> |
| **EGAT AI Gateway** | • ใช้ผ่านเครือข่าย กฟผ. ไม่ต้องสมัคร API Key ส่วนตัว<br>• ข้อมูลผ่าน Gateway ภายในของ กฟผ.<br>• ตอบเร็วเทียบเท่า Cloud<br>• ใช้งานได้กับคอมพิวเตอร์สเปคต่ำ | • ต้องเชื่อมต่อเครือข่าย กฟผ.<br>• ต้องใช้ Model ID ที่ออกโดย กฟผ. (มี suffix `-GW-POC` หรือ `-EGAT-GATEWAY`) |
| **Cloud AI** (Gemini, OpenAI) | • ตอบเร็ว<br>• ใช้งานได้กับคอมพิวเตอร์สเปคต่ำ<br>• มีโมเดลให้เลือกหลายระดับราคา | • ต้องต่ออินเทอร์เน็ต<br>• ข้อมูลถูกส่งออกนอกเครื่อง ไม่เหมาะกับเอกสารที่มีความลับ<br>• ต้องสมัครและจัดการ API Key<br>• มีค่าใช้จ่ายตามจำนวน Token ที่ใช้ |

> **คำแนะนำในการเลือก:**
> - เอกสาร**ลับ** → ใช้ **Local AI**
> - ผู้ใช้งานภายใน **กฟผ.** ต้องการความเร็วโดยไม่ต้องจัดการ API Key เอง → ใช้ **EGAT AI Gateway**
> - เอกสาร**ทั่วไป** ต้องการความเร็วและความแม่นยำ → ใช้ **Gemini** หรือ **OpenAI**
> - คอมพิวเตอร์**สเปคต่ำ** → ใช้ **EGAT AI Gateway** หรือ **Cloud AI**

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

1. ไปที่หน้า **[Releases](https://github.com/Portrate/EGAT-File-Checker/releases/)** ของ GitHub
2. ดาวน์โหลดไฟล์ **`FileChecker.exe`** จาก Assets
3. เปิดไฟล์ `FileChecker.exe`
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
6. **ดูประวัติย้อนหลัง** ระบบจะบันทึกผลการตรวจสอบทุกครั้งโดยอัตโนมัติ สามารถเปิดดูประวัติได้ที่ `http://localhost:8000/history` เพื่อเรียกดูผลเก่า ดาวน์โหลด Excel ซ้ำ หรือลบรายการที่ไม่ต้องการ ข้อมูลเก็บไว้ในเครื่องผู้ใช้ที่ `%USERPROFILE%\.egat-file-checker\history.db`

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

## วิธีการทำงานของระบบ

### ภาพรวม

เมื่อผู้ใช้กด "ตรวจสอบ" ระบบจะทำงานตามลำดับขั้นตอนดังนี้

```
1. รับไฟล์ PDF + Checklist
2. แยกข้อความออกจาก PDF
   ├── หน้าที่มีข้อความดิจิทัล  → อ่านโดยตรง (เร็ว)
   └── หน้าที่เป็นภาพสแกน   → OCR ด้วย Tesseract (ช้ากว่า)
3. แบ่งข้อความเป็นชิ้นเล็กๆ (Chunking)
   เพราะ AI มีขีดจำกัดของข้อความที่รับได้ต่อครั้ง
4. ส่งแต่ละรายการใน Checklist ให้ AI ตรวจสอบ
   วนตรวจสอบทีละชิ้น จนพบว่า "ผ่าน" หรือตรวจครบทุกชิ้นแล้ว "ไม่ผ่าน"
5. รวบรวมผลลัพธ์และคำนวณคะแนน
6. แสดงผลบนหน้าเว็บ
```

---

### การอ่านข้อความจาก PDF

ระบบใช้ **PyMuPDF** อ่านเนื้อหาจาก PDF โดยตรวจสอบแต่ละหน้าว่ามีข้อความดิจิทัลอยู่หรือไม่

- **หน้าที่มีข้อความ ≥ 100 ตัวอักษร** จะดึงข้อความออกโดยตรง เหมือนการ Copy-Paste
- **หน้าที่มีข้อความ < 100 ตัวอักษร** จะถือว่าเป็นภาพสแกน ระบบจะแปลงหน้านั้นเป็นรูปภาพ แล้วส่งให้ **Tesseract OCR** อ่านภาษาไทยและอังกฤษ

จากนั้นจะถูกส่งต่อให้ AI วิเคราะห์

---

### การแบ่งข้อความ (Chunking)

AI แต่ละโมเดลมีขีดจำกัดของข้อความที่สามารถรับได้ต่อครั้ง (Context Window) หากเอกสาร PDF มีขนาดใหญ่เกินไป จะต้องแบ่งเป็นชิ้นเล็กๆ ก่อน

| พารามิเตอร์ | ค่าที่ใช้ | ความหมาย |
|---|---|---|
| CHUNK_SIZE | 24,000 ตัวอักษร | ประมาณ 6,000–8,000 คำ |
| CHUNK_OVERLAP | 2,000 ตัวอักษร | ป้องกันเนื้อหาที่อยู่ตรงรอยต่อหายไป |

ระบบจะส่งชิ้นข้อความทีละชิ้นให้ AI ตรวจสอบ หากพบว่ารายการนั้น "ผ่าน" ในชิ้นใดชิ้นหนึ่ง ระบบจะหยุดและข้ามไปรายการถัดไปทันที โดยไม่ต้องรอให้ตรวจครบทุกชิ้น ทำให้ประหยัดเวลาได้

---

### การส่งคำสั่งให้ AI (Prompt)

สำหรับแต่ละรายการใน Checklist ระบบจะสร้างคำสั่งในรูปแบบนี้ส่งให้ AI

```
คุณคือผู้ตรวจสอบความครบถ้วนของเอกสาร

ข้อกำหนดที่ต้องตรวจสอบ:
<requirement>
[ข้อกำหนดจาก Checklist]
</requirement>

ข้อความจากเอกสาร:
<document_chunk>
[ส่วนหนึ่งของข้อความจาก PDF]
</document_chunk>

ตรวจสอบว่าเอกสารนี้มีเนื้อหาที่ตรงตามข้อกำหนดหรือไม่ ตอบเป็น JSON:
{
  "found": true/false,
  "reasoning": "อธิบายเป็นภาษาไทย 1-2 ประโยค",
  "evidence": "ข้อความจากเอกสารที่เป็นหลักฐาน (ไม่เกิน 100 ตัวอักษร) หรือ null"
}
```

AI ต้องตอบเป็นภาษาไทยเท่านั้น หากตอบเป็นภาษาอังกฤษ ระบบจะลองส่งคำสั่งใหม่อัตโนมัติ

---

### การคำนวณคะแนน

แต่ละรายการใน Checklist มีคะแนนที่ผู้ใช้กำหนดเอง ผลลัพธ์จะถูกคำนวณดังนี้

- **ผ่าน (pass)** → ได้คะแนนเต็มของรายการนั้น
- **ไม่ผ่าน (fail)** → ได้ 0 คะแนน

---

### การแสดงผลแบบ Real-time (Streaming)

ระบบใช้ **Server-Sent Events (SSE)** เพื่อส่งผลลัพธ์กลับมาแสดงบนหน้าเว็บทีละรายการขณะที่ AI กำลังวิเคราะห์อยู่ ผู้ใช้ไม่ต้องรอจนกว่าการตรวจสอบทั้งหมดจะเสร็จ แต่ผลลัพธ์แต่ละรายการจะแสดงทันทีที่ AI ตอบกลับมา

---

### การส่งออก Excel

เมื่อตรวจสอบเสร็จ สามารถดาวน์โหลดผลลัพธ์เป็นไฟล์ `.xlsx` ที่ประกอบด้วย

- **ชีทที่ 1 สรุปผล** แสดงคะแนนรวมของแต่ละหัวข้อใหญ่
- **ชีทที่ 2 รายละเอียด** แสดงผลของรายการย่อยทุกข้อ พร้อมเหตุผลและหลักฐาน

---

# ผลการทดสอบระบบ

## 1. ความเร็ว

### 1.1 OCR

ก่อนที่ระบบจะให้ AI วิเคราะห์เอกสารได้ ระบบต้องอ่านข้อความออกจากไฟล์ PDF ก่อน ซึ่งทำได้ 2 วิธี

- **ไม่มี OCR (อ่านข้อความโดยตรง)** เหมาะกับ PDF ที่พิมพ์ด้วยคอมพิวเตอร์ เช่น ส่งออกจาก Word หรือ Excel ระบบสามารถดึงออกมาได้ทันที เหมือนคัดลอกข้อความจากหน้าจอ
- **OCR (แปลงภาพเป็นข้อความ)** เหมาะกับ PDF ที่ได้จากการสแกนเอกสารกระดาษ ไฟล์ประเภทนี้ไม่มีข้อความฝังอยู่ มีแต่รูปภาพของตัวหนังสือ ระบบต้องแปลงเป็นภาพก่อน แล้วใช้ AI อีกตัวหนึ่งอ่านภาพนั้นแปลงกลับมาเป็นตัวหนังสือ จึงใช้เวลานานกว่ามาก โดยเฉพาะเอกสารที่มีหลายหน้า

| รูปแบบ | เวลาที่ใช้ (นาที) |
|---|---|
| ไม่มี OCR | 0:27 |
| OCR | 4:41 |

### 1.2 ความเร็วของแต่ละโมเดล

"โมเดล" คือตัว AI ที่ทำหน้าที่อ่านและตัดสินว่าเอกสารผ่านหรือไม่ผ่าน

โมเดลที่ฉลาดกว่าและมีขนาดใหญ่กว่า จะใช้เวลาคิดนานกว่า ใช้เวลาพิจารณาละเอียดกว่า ผลที่ได้มักแม่นยำกว่า แต่โมเดลขนาดเล็กตอบได้เร็วกว่า แต่อาจพลาดรายละเอียดบางอย่าง และโมเดลขนาดเล็กจะมีค่าใช้จ่ายที่ต่ำกว่าโมเดลขนาดใหญ่

| โมเดล | เวลาที่ใช้ (นาที) |
|---|---|
| Gemma 4 26B (ทดสอบกับโน๊ตบุ๊ค Dell G5 15) | 20:26 |
| GPT-5 | 14:41 |
| GPT-4o | 6:32 |

---

## 2. ความฉลาด

### 2.1 OCR

ความฉลาดของ AI ไม่ได้ขึ้นอยู่กับตัว AI เพียงอย่างเดียว แต่ขึ้นอยู่กับคุณภาพของข้อความที่ส่งให้อ่านด้วย ถ้าข้อความที่ส่งให้มีข้อผิดพลาด AI ก็จะตัดสินผิดพลาดตามไปด้วย แม้จะเป็น AI ที่ฉลาดแค่ไหนก็ตาม

- **ไม่มี OCR** ข้อความที่ได้มีความถูกต้องสูงมาก ตัวสะกดครบถ้วน วรรณยุกต์ถูกต้อง AI จึงสามารถทำความเข้าใจเนื้อหาและค้นหาหลักฐานได้แม่นยำ แต่ไม่สามารถอ่านข้อความที่อยู่ในรูปภาพได้
- **OCR** เหมาะกับ PDF ที่ได้จากการสแกนเอกสารกระดาษ ซึ่งไฟล์ประเภทนี้ไม่มีข้อความฝังอยู่ มีแต่รูปภาพของตัวหนังสือ OCR จะแปลงรูปภาพเหล่านั้นให้กลายเป็นข้อความที่ AI สามารถอ่านและวิเคราะห์ได้ ทำให้ระบบรองรับเอกสารได้ทุกประเภท

จากผลการทดสอบพบว่า เอกสารแนบ - นโยบายการบูรณาการด้านการกำกับดูแลกิจการที่ดีการบริหารความเสี่ยง และการปฏิบัติตามกฎหมายและกฎระเบียบ (Governance Risk and Compliance : GRC) กฟผ. มีผลลัพธ์เป็น FOUND จากการใช้ OCR เนื่องจากเอกสารดังกล่าวเป็นภาพจากการสแกนเอกสารกระดาษ ซึ่งระบบสามารถอ่านได้จากการใช้ OCR เท่านั้น

### 2.2 ความฉลาดของแต่ละโมเดล

โมเดลแต่ละตัวมีความสามารถในการเข้าใจภาษาไทยและตีความเอกสารที่แตกต่างกัน อธิบายได้ดังนี้

- **ขนาดของโมเดล** โมเดลที่มีขนาดใหญ่กว่าผ่านการฝึกมาจากข้อมูลมากกว่า มีความเข้าใจบริบทและความหมายแฝงของภาษาดีกว่า เช่น เข้าใจว่าประโยคนี้แม้ไม่ได้พูดตรงๆ แต่ก็ครอบคลุมข้อกำหนดที่ถามอยู่ ในขณะที่โมเดลขนาดเล็กอาจตรวจสอบได้เฉพาะคำที่ตรงกันพอดีเท่านั้น
- **ความสามารถด้านภาษาไทย** บางโมเดลถูกฝึกมาด้วยข้อมูลภาษาไทยน้อย ทำให้บางครั้งตอบกลับมาเป็นภาษาอังกฤษ หรืออธิบายเหตุผลได้ไม่ชัดเจน ซึ่งระบบมีกลไกให้ AI ลองใหม่อัตโนมัติแต่ก็ใช้เวลาเพิ่มขึ้น
- **ความเคร่งครัดในการทำตามคำสั่ง** ระบบกำหนดให้ AI ต้องตอบในรูปแบบที่ชัดเจน เช่น ต้องมีเหตุผล ต้องมีหลักฐาน ต้องตอบเป็นภาษาไทย บางโมเดลทำตามได้ดีกว่า ให้ผลลัพธ์ที่อ่านเข้าใจง่ายและนำไปใช้ได้ทันที ในขณะที่บางโมเดลอาจตอบผิดรูปแบบหรืออธิบายเหตุผลคลุมเครือ

---

# Architecture

แอปพลิเคชันนี้ใช้ **FastAPI** (ทำงานบน **Uvicorn**) เป็น Backend web framework ทำหน้าที่ให้บริการทั้ง API endpoint และ UI
UI สร้างด้วย HTML, CSS และ Vanilla JavaScript โดยใช้ Jinja2 templates

สำหรับการวิเคราะห์ด้วย AI รองรับ 3 ช่องทาง ได้แก่ **Ollama** (Local) ที่ `localhost:11434`, **EGAT AI Gateway** และ **Cloud AI** โดยผู้ใช้เลือก Model ได้ผ่าน UI และ Backend เรียกใช้งานผ่าน **httpx** ทั้งหมด
โมเดล Local AI ที่ใช้คือ **Gemma 4 (26B)** จาก Google

ประวัติการตรวจสอบจะถูกบันทึกอัตโนมัติลง **SQLite** (`history.db`) ที่ `~/.egat-file-checker/` ของผู้ใช้ ทำให้ไฟล์ `.exe` ที่ติดตั้งใน Program Files ยังสามารถเขียนได้

การดึงข้อความจาก PDF ดำเนินการโดยใช้ **PyMuPDF** (Python wrapper สำหรับ MuPDF) ซึ่งอ่านแต่ละหน้าและดึงข้อความที่เลือกได้ออกมา สำหรับหน้าที่เป็นภาพสแกนและไม่มีข้อความดิจิทัล แอปจะ Fallback ไปใช้ **Tesseract OCR** ผ่าน **pytesseract** และ **Pillow** เพื่ออ่านข้อความจากภาพของหน้านั้น ๆ โดย Tesseract เป็น Optional (แอปยังทำงานได้ปกติกับ PDF ที่มีข้อความดิจิทัลโดยไม่ต้องติดตั้ง)

ข้อมูล Checklist ที่ส่งเข้ามาจะถูกตรวจสอบความถูกต้องด้วย **Pydantic** ก่อนประมวลผล หากโครงสร้างไม่ถูกต้อง ผู้ใช้จะได้รับ HTTP 422 error

ฟีเจอร์ส่งออก Excel ใช้ **openpyxl** สร้างไฟล์ `.xlsx`

แอปพลิเคชันทั้งหมดถูกแพ็กเป็นไฟล์ `.exe` ไฟล์เดียวด้วย **PyInstaller** ทำให้ผู้ใช้ไม่จำเป็นต้องติดตั้ง Python

---

## โครงสร้างและการทำงานของโค้ด

### Project Structure

```
EGAT-File-Checker/
├── run.py                      ← entry point (EXE / python run.py)
├── main.py                     ← FastAPI app + API routes
├── config.py                   ← all tuneable constants (URLs, timeouts, model name, chunk sizes)
├── build.bat                   ← PyInstaller build script
├── requirements.txt
│
├── checker/
│   ├── models.py               ← Pydantic request/response schemas
│   ├── pdf_extractor.py        ← PDF to plain text (native + OCR fallback)
│   ├── orchestrator.py         ← LLM prompt logic, chunking, result parsing
│   ├── excel_exporter.py       ← build .xlsx download response
│   └── history.py              ← SQLite-backed history persistence
│
├── static/
│   ├── css/style.css
│   └── js/app.js               ← frontend logic (fetch/analyze, render results)
│
├── templates/
│   ├── index.html              ← single-page UI served by Jinja2
│   └── history.html            ← history browser page
│
└── docs/
    ├── index.html              ← project presentation slides (open in browser)
    └── deck-stage.js           ← slide deck controller
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
         orchestrator.analyze_with_llm_stream()
              │  loops over each checklist section and each sub-item
              │  splits document into CHUNK_SIZE chars (CHUNK_OVERLAP overlap) — from config.py
              │  calls Ollama / Gemini / OpenAI per chunk until a "pass" is found
              │  Gemini + OpenAI: exponential backoff retry on 429/503 (MAX_RETRIES from config.py)
              │  parses JSON from LLM response (_extract_json)
              │  sanitizes reasoning to remove repetition artifacts
              │  retries once if reasoning is not in Thai (Ollama only)
              ▼
         main.py  computes summary counts + scores
              ▼
  JSON response  →  Browser renders pass/fail table
```

---

### Files Explained

**`config.py`** จะรวมตัวแปรต่างๆ ได้แก่ `HOST`, `PORT`, `OLLAMA_BASE_URL`, `DEFAULT_MODEL`, `OLLAMA_TIMEOUT`, `CLOUD_TIMEOUT`, `OLLAMA_OPTIONS`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `MAX_RETRIES` และอื่นๆ หากต้องการปรับแต่งพารามิเตอร์ใดๆ ให้แก้ไขที่ไฟล์นี้เพียงไฟล์เดียว

**`run.py`** — ไฟล์สำหรับเปิดโปรแกรม ใช้โดย `.exe` และ `start.bat`.
1. ตรวจสอบว่ามีคำสั่ง `ollama` อยู่ใน PATH หรือไม่ (ข้ามหากไม่พบ)
2. ตรวจสอบ Ollama URL (กำหนดใน `config.py`) ว่ากำลังทำงานอยู่ ถ้าไม่ได้ทำงานจะสั่ง ollama serve
3. ตรวจสอบว่าดาวน์โหลดโมเดล (`DEFAULT_MODEL` ใน `config.py`) ไว้แล้วหรือไม่ (ไม่ดาวน์โหลดอัตโนมัติ)
4. เปิดเบราว์เซอร์หลังจากรอตาม `BROWSER_OPEN_DELAY` แล้วส่งต่อการทำงานให้ uvicorn

**`main.py`**:
- `GET /` — แสดงหน้า `index.html` ผ่าน Jinja2
- `POST /analyze/stream` — ตรวจสอบ PDF และ JSON ของรายการที่ตรวจสอบ เรียกใช้ orchestrator ส่งผลลัพธ์เป็น Server-Sent Events และบันทึกประวัติเมื่อเสร็จ
- `POST /export/excel` — รับผลลัพธ์ที่คำนวณแล้วจากเบราว์เซอร์ แล้วส่งออกเป็นไฟล์ `.xlsx`
- `GET /ollama/status` — รายงานว่า Ollama เชื่อมต่อได้หรือไม่ พร้อมรายชื่อโมเดลที่ติดตั้ง
- `GET /history` — หน้าเว็บแสดงรายการประวัติการตรวจสอบทั้งหมด
- `GET /history/list` — คืนรายการประวัติเป็น JSON
- `GET /history/{id}` — คืนรายละเอียดผลการตรวจสอบที่บันทึกไว้
- `GET /history/{id}/excel` — ดาวน์โหลดผลที่บันทึกไว้เป็น Excel ซ้ำ
- `DELETE /history/{id}` — ลบรายการประวัติ
- `GET /health` — ตรวจสอบสถานะการเชื่อมต่อของ Ollama และโมเดลที่กำหนดไว้

**`checker/history.py`** — จัดการประวัติการตรวจสอบด้วย SQLite ไฟล์ฐานข้อมูลอยู่ที่ `~/.egat-file-checker/history.db` (per-user เพื่อให้ `.exe` ใน Program Files เขียนได้) บันทึก `filename`, `model`, summary, คะแนน, similarity score และ `results_json` ของทุกครั้งที่ตรวจสอบสำเร็จ พร้อม index บน `created_at` สำหรับเรียงประวัติย้อนหลัง

**`checker/pdf_extractor.py`** — ใช้ `PyMuPDF` (`fitz`) อ่านแต่ละหน้า หน้าที่มีข้อความน้อยกว่า 100 ตัวอักษรถือว่าเป็นภาพสแกน จะส่งผ่าน Tesseract OCR เพื่อแปลงเป็นตัวอักษร โดยรองรับทั้งภาษาไทยและภาษาอังกฤษ ผลลัพธ์จะถูกรวมเป็นบล็อก

**`checker/orchestrator.py`** — Core LLM logic:
- `_split_chunks()` — แบ่งข้อความทั้งหมดเป็นชิ้นตาม `CHUNK_SIZE` และ `CHUNK_OVERLAP` ที่กำหนดใน `config.py`
- `_check_chunk_ollama()` — ส่งคำถามไปยัง Ollama พร้อม retry 1 ครั้งหากตอบกลับเป็นภาษาอังกฤษ
- `_check_chunk_gemini()` — ส่งคำถามไปยัง Gemini API พร้อม exponential backoff retry สูงสุด `MAX_RETRIES` ครั้งสำหรับ HTTP 429 (quota) และ 503 (overload)
- `_check_chunk_openai()` — ส่งคำถามไปยัง OpenAI API (หรือ EGAT AI Gateway ผ่าน `base_url` ที่กำหนด เนื่องจาก Gateway เป็น OpenAI-compatible) พร้อม exponential backoff retry สูงสุด `MAX_RETRIES` ครั้งสำหรับ HTTP 429 รองรับ o1/o3 series ด้วย
- `_check_chunk()` — router เลือก provider ตามชื่อโมเดล (`gemini*` → Gemini, ชื่อที่มี `-GW-POC` หรือ `-EGAT-GATEWAY` → EGAT AI Gateway, `gpt*/o1*/o3*` → OpenAI, อื่นๆ → Ollama)
- `_check_single_item()` — วนตรวจสอบข้อความแต่ละชิ้น คืนค่า `"pass"` ทันทีที่พบ หรือ `"fail"` หากไม่พบในทุกชิ้น
- `_extract_json()` — จัดการผลลัพธ์ที่ส่งกลับมาในรูปแบบที่ไม่ถูกต้อง ลอง `json.loads` ก่อน แล้วใช้ regex ในกรณีที่ผลลัพธ์ถูกตัด
- `_sanitize_reasoning()` — ตรวจหาการวนซ้ำของตัวอักษร คำที่ซ้ำกัน และคำอังกฤษแปลกปลอม แล้วตัดทิ้ง
- `analyze_with_llm_stream()` — Top-level async generator เรียกใช้โดย `main.py` ส่งผลลัพธ์แบบ SSE ทีละรายการขณะวิเคราะห์

**`checker/models.py`** — ตรวจสอบรายการขาเข้า (`ChecklistSection` → `ChecklistItem` with `name` + `score`) และขาออก (`ItemResult`, `SectionResult`, `AnalysisResponse`).

**`checker/excel_exporter.py`** — สร้างไฟล์ `.xlsx` โดยใช้ `openpyxl` ประกอบด้วย 2 ชีท ชีทที่ 1 เป็นตารางสรุป ชีทที่ 2 เป็นรายละเอียดของแต่ละรายการย่อยที่ตรวจสอบ

---

### LLM Configuration (`config.py`)

| Parameter | Value | Notes |
|---|---|---|
| Default model | `gemma4:26b` | change `DEFAULT_MODEL` in `config.py` or select via UI |
| Context window | 32,768 tokens | `num_ctx` in `OLLAMA_OPTIONS` (Ollama only) |
| Max output tokens | 256 | `num_predict` — enough for one JSON object |
| Temperature | 0 | deterministic output |
| Chunk size | 24,000 chars | `CHUNK_SIZE` in `config.py` |
| Chunk overlap | 2,000 chars | `CHUNK_OVERLAP` in `config.py` |
| Read timeout (Ollama) | 1,200 s (20 min) | `OLLAMA_TIMEOUT` in `config.py` |
| Read timeout (Cloud) | 120 s | `CLOUD_TIMEOUT` in `config.py` — shared by Gemini and OpenAI |
| Max retries (Cloud) | 5 | `MAX_RETRIES` in `config.py` — applies to Gemini and OpenAI |

---

### Building the EXE

```bat
build.bat
```

ใช้ PyInstaller โดยสามารถรัน `run.py` ซึ่งจะรวม `static/`, `templates/` และ `checker/` ไว้ในไฟล์เดียวชื่อ `FileChecker.exe` ในโฟลเดอร์ `dist/`.
