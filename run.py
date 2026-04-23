# Entry point for the Risk File Checker executable.

import os
import shutil
import subprocess
import sys
import threading
import time
import traceback
import webbrowser

# Ensure bundled modules are importable when frozen
if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)

import uvicorn


def print_banner():
    print("=" * 50)
    print("  Risk File Checker")
    print("  ระบบตรวจสอบเอกสาร PDF ด้วย AI")
    print("=" * 50)
    print()


def check_ollama() -> bool:
    return shutil.which("ollama") is not None


def is_ollama_running() -> bool:
    try:
        import httpx
        r = httpx.get("http://localhost:11434/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def start_ollama():
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        for _ in range(15):
            time.sleep(1)
            if is_ollama_running():
                return True
    except Exception:
        pass
    return False


def ensure_model(model_name: str) -> bool:
    try:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10,
            creationflags=flags,
        )
        if model_name in result.stdout:
            return True
    except Exception:
        pass
    return False


def open_browser_delayed(url: str, delay: float = 2.0):
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()


def main():
    print_banner()

    # --- ตรวจสอบ Local AI (Ollama) ---
    local_ai_ready = False
    if check_ollama():
        if not is_ollama_running():
            print("  กำลังเปิด Ollama server...")
            is_running = start_ollama()
        else:
            is_running = True

        if is_running and ensure_model("gemma4:26b"):
            local_ai_ready = True

    # --- สรุปสถานะ ---
    print()
    if local_ai_ready:
        print("  Local AI (gemma4:26b) : พร้อมใช้งาน")
    else:
        print("  Local AI (gemma4:26b) : ไม่พร้อม — ใช้ Gemini หรือ OpenAI แทนได้ผ่าน UI")

    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    print()
    print("=" * 50)
    print(f"  เปิดเบราว์เซอร์ไปที่ {url}")
    print("  กด Ctrl+C เพื่อปิดโปรแกรม")
    print("=" * 50)
    print()

    from main import app  # noqa: E402
    open_browser_delayed(url)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nปิดโปรแกรมแล้ว")
    except Exception:
        print()
        print("=" * 50)
        print("  เกิดข้อผิดพลาด:")
        print("=" * 50)
        traceback.print_exc()
        print()
        input("กด Enter เพื่อปิด...")
        sys.exit(1)
