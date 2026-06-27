"""
config.py
---------
One place for all settings, so magic numbers don't get scattered in the code.

Secrets (like GROQ_API_KEY) come from a .env file -> never hardcoded.
Everything else has a sensible default here that you can tweak.
"""

import os
import pathlib
from dotenv import load_dotenv

# The embedding model is cached locally after first download, so skip the
# network check to HuggingFace on every load (faster startup + works offline).
os.environ.setdefault("HF_HUB_OFFLINE", "1")

# Corporate networks often run a TLS-inspecting proxy with a self-signed root CA.
# Python's default cert bundle (certifi) doesn't know that CA -> every HTTPS call to
# Groq / the web fails with CERTIFICATE_VERIFY_FAILED. truststore makes Python use the
# OS (Windows) certificate store instead, where the corporate CA is already installed.
# Best-effort: if truststore isn't installed, we just carry on.
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

# Load .env so secrets stay out of the source code.
load_dotenv()

# ---- LLM backend: "groq" (cloud, fast, what you have a key for) or "ollama" (local) ----
LLM_BACKEND = os.getenv("LLM_BACKEND", "groq").lower()

# Groq = cloud API. You have a key -> this is the default here.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Ollama = a model running locally (free, private). Optional fallback.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# ---- Embedding model (turns text into vectors) ----
# Local + free + small. First run downloads ~90MB, then loads from cache.
# (Groq has NO embeddings endpoint, so embeddings MUST be done locally.)
_EMBED_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")


def _resolve_embed_model(name):
    """Return a loadable model id.

    Normally we'd just pass the name ("all-MiniLM-L6-v2") and let HuggingFace find it
    in its cache. But a cache can get corrupted (e.g. a half-finished download whose
    'refs/main' points at a snapshot missing the weights). When that happens, loading
    BY NAME fails even though a complete copy sits in another snapshot folder.

    So: scan the HF cache for a snapshot that actually contains the model weights and
    return its full path. If we can't find one, fall back to the plain name (which lets
    a fresh online download happen on first run).
    """
    import glob
    repo = "models--sentence-transformers--" + name.split("/")[-1]
    base = pathlib.Path.home() / ".cache" / "huggingface" / "hub" / repo / "snapshots"
    if base.is_dir():
        for snap in base.iterdir():
            if (snap / "model.safetensors").exists() or (snap / "pytorch_model.bin").exists():
                return str(snap)        # complete snapshot found -> load from here
    return name                          # not cached yet -> let HF download by name


EMBED_MODEL = _resolve_embed_model(_EMBED_NAME)

# ---- Paths ----
BASE_DIR = pathlib.Path(__file__).parent
DATA_DIR = BASE_DIR / "data"                       # catalog + knowledge live here
CATALOG_PATH = DATA_DIR / "hardware_catalog.json"  # structured hardware data
KNOWLEDGE_DIR = DATA_DIR / "knowledge"             # markdown guidance docs
DB_DIR = BASE_DIR / "faiss_store"                  # vector index is saved here

# ---- Retrieval tuning ----
TOP_K = 6            # how many knowledge chunks to pull per query
MAX_CANDIDATES = 8   # how many catalog items to shortlist for the LLM

# ---- Currency ----
USD_TO_INR = float(os.getenv("USD_TO_INR", "85"))  # rough convenience conversion

# ---- Live price fetch ----
# If True, price_fetch tries to refresh prices from the web (best-effort) and
# falls back to the seed price on any failure. If False, it uses seed prices only.
ENABLE_LIVE_PRICES = os.getenv("ENABLE_LIVE_PRICES", "false").lower() == "true"
PRICE_FETCH_TIMEOUT = 8  # seconds per request before giving up
