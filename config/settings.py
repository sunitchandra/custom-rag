import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

APP_TITLE = "Custom RAG Document Assistant"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# DEFAULT_CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:3b")
DEFAULT_CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen3:14b")
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
CHROMA_PATH = PROJECT_ROOT / os.getenv("CHROMA_PATH", "data/chroma")
UPLOAD_PATH = PROJECT_ROOT / os.getenv("UPLOAD_PATH", "data/uploads")
SQLITE_PATH = PROJECT_ROOT / os.getenv("SQLITE_PATH", "data/app.db")
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")
DEFAULT_CHUNK_SIZE = 900
DEFAULT_CHUNK_OVERLAP = 150
DEFAULT_TOP_K = 5
DEFAULT_TEMPERATURE = 0.1

for path in (CHROMA_PATH, UPLOAD_PATH, SQLITE_PATH.parent):
    path.mkdir(parents=True, exist_ok=True)
