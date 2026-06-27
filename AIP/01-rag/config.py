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
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

# ---- Paths ----
BASE_DIR = pathlib.Path(__file__).parent
DATA_DIR = BASE_DIR / "data"          # documents are read from here
DB_DIR = BASE_DIR / "faiss_store"     # the vector index is saved here

# ---- Chunking + retrieval tuning ----
CHUNK_SIZE = 500      # roughly this many characters per chunk
CHUNK_OVERLAP = 80    # overlap between two chunks (so context isn't cut)
TOP_K = 4             # return this many most-relevant chunks per search
