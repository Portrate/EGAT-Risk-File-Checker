import httpx

# --- Server ---
HOST = "127.0.0.1"
PORT = 8000
BROWSER_OPEN_DELAY = 2.0

# --- EGAT AI Gateway (OpenAI-compatible) ---
EGAT_GATEWAY_BASE_URL = "https://aigateway.egat.co.th/v1"

# --- Ollama ---
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"

# --- Models ---
DEFAULT_MODEL = "gemma4:26b"
LOCAL_MODELS = [{"value": DEFAULT_MODEL, "label": "Gemma 4 26B (Local)"}]

# --- Timeouts ---
OLLAMA_TIMEOUT = httpx.Timeout(connect=30.0, read=1200.0, write=60.0, pool=10.0)
CLOUD_TIMEOUT = httpx.Timeout(connect=30.0, read=120.0, write=60.0, pool=10.0)
OLLAMA_CHECK_TIMEOUT = 3.0
HEALTH_CHECK_TIMEOUT = 5.0

# --- Ollama generation options ---
OLLAMA_OPTIONS = {
    "num_ctx": 32768,
    "num_predict": 256,
    "temperature": 0,
    "repeat_penalty": 1.3,
    "repeat_last_n": 64,
}

# --- Document chunking ---
CHUNK_SIZE = 24_000
CHUNK_OVERLAP = 2_000

# --- Retry ---
MAX_RETRIES = 5
