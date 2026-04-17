"""
Entry point for the Risk File Checker executable.
"""

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
            print(f"  [OK] โมเดล {model_name} พร้อมใช้งาน")
            return True
    except Exception:
        pass

    print(f"  กำลังดาวน์โหลดโมเดล {model_name}...")
    print(f"  (ครั้งแรกอาจใช้เวลานาน โปรดรอ...)")
    print()
    try:
        subprocess.run(["ollama", "pull", model_name], timeout=1800)
        return True
    except Exception as e:
        print(f"  [ERROR] ดาวน์โหลดโมเดลไม่สำเร็จ: {e}")
        return False


def open_browser_delayed(url: str, delay: float = 2.0):
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()


def main():
    print_banner()

    print("[1/3] ตรวจสอบ Ollama...")
    if not check_ollama():
        print()
        print("  [ERROR] ไม่พบ Ollama ในเครื่อง")
        print("  กรุณาติดตั้ง Ollama จาก https://ollama.com")
        print()
        input("กด Enter เพื่อปิด...")
        sys.exit(1)
    print("  [OK] พบ Ollama")

    print()
    print("[2/3] ตรวจสอบ Ollama server...")
    if not is_ollama_running():
        print("  กำลังเปิด Ollama server...")
        if not start_ollama():
            print()
            print("  [ERROR] ไม่สามารถเปิด Ollama ได้")
            print("  กรุณาเปิด Ollama ด้วยตนเองก่อนรันโปรแกรม")
            print()
            input("กด Enter เพื่อปิด...")
            sys.exit(1)
    print("  [OK] Ollama server พร้อมใช้งาน")

    print()
    print("[3/3] ตรวจสอบโมเดล AI...")
    if not ensure_model("gemma4:26b"):
        print()
        print("  [ERROR] ไม่สามารถเตรียมโมเดลได้")
        print()
        input("กด Enter เพื่อปิด...")
        sys.exit(1)

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
