"""
config.py
---------
All settings live in one place. This keeps magic numbers out of the code
and makes tweaking easy (chunk size, top_k, model, etc.).

Some settings come from a .env file (keep secrets like API keys there),
the rest have sensible defaults here.
"""

import os
import pathlib
from dotenv import load_dotenv

# The embedding model is already cached locally, so skip the network check
# to HuggingFace on every load (faster startup, works offline).
os.environ.setdefault("HF_HUB_OFFLINE", "1")

# Load the .env file (if present). This way secrets like GROQ_API_KEY
# are never hardcoded in the source -> stays safe.
load_dotenv()

# ---- Choose the LLM backend: "ollama" (local) or "groq" (cloud) ----
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama").lower()

# Ollama = a model running locally on your laptop (free, private)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# Groq = cloud API (fast, has a free tier). Needs a key.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---- Embedding model ----
# Turns text into numbers (a vector). Local + free + small.
# First run downloads ~90MB, after that it loads from cache.
_EMBED_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")


def _resolve_embed_model(name):
    """Return a loadable model id.

    Normally we'd just pass the name and let HuggingFace find it in its cache. But this
    machine's cache got corrupted (a half-finished download whose 'refs/main' points at
    a snapshot missing the weights), so loading BY NAME fails even though a complete copy
    sits in another snapshot folder. So: scan the cache for a snapshot that actually has
    the weights and return its path; otherwise fall back to the name (lets a fresh
    download happen on first run).
    """
    repo = "models--sentence-transformers--" + name.split("/")[-1]
    base = pathlib.Path.home() / ".cache" / "huggingface" / "hub" / repo / "snapshots"
    if base.is_dir():
        for snap in base.iterdir():
            if (snap / "model.safetensors").exists() or (snap / "pytorch_model.bin").exists():
                return str(snap)
    return name


EMBED_MODEL = _resolve_embed_model(_EMBED_NAME)

# ---- Paths ----
BASE_DIR = pathlib.Path(__file__).parent
DATA_DIR = BASE_DIR / "data"          # documents are read from here
DB_DIR = BASE_DIR / "faiss_store"     # the vector index is saved here

# ---- Chunking + retrieval tuning ----
CHUNK_SIZE = 500      # roughly this many characters per chunk
CHUNK_OVERLAP = 80    # overlap between two chunks (so context isn't cut)
TOP_K = 4             # return this many most-relevant chunks per search
