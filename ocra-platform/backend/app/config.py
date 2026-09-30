import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    NGC_API_KEY: str = os.getenv("NGC_API_KEY", "")
    EARTH2STUDIO_CACHE_DIR: str = os.getenv("EARTH2STUDIO_CACHE_DIR", os.path.expanduser("~/.cache/earth2studio"))
    DEFAULT_SCIDL_MODEL: str = os.getenv("DEFAULT_SCIDL_MODEL", "SFNO")
    DEVICE: str = os.getenv("DEVICE", "auto")

    # Local LLM (Ollama)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3:4b")
    OLLAMA_FALLBACK_MODELS: list = [
        m.strip() for m in os.getenv("OLLAMA_FALLBACK_MODELS", "llama3.2:3b,gemma3:1b,llama3.2:1b,gemma2:2b").split(",") if m.strip()
    ]
    OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", 300))
    OLLAMA_KEEP_ALIVE: str = os.getenv("OLLAMA_KEEP_ALIVE", "1h")
    # Set on Render: key sent to the PC's ORCA gateway (OLLAMA_BASE_URL=https://<tunnel>/gateway)
    OLLAMA_API_KEY: str = os.getenv("OLLAMA_API_KEY", "")
    # Set on the PC: enables /gateway/* so a remote ORCA (Render) can use this PC's Ollama
    ORCA_GATEWAY_KEY: str = os.getenv("ORCA_GATEWAY_KEY", "")

    # Chat memory (per browser session, in-memory)
    CHAT_HISTORY_TURNS: int = int(os.getenv("CHAT_HISTORY_TURNS", 4))
    MAX_SESSIONS: int = int(os.getenv("MAX_SESSIONS", 500))

settings = Settings()
