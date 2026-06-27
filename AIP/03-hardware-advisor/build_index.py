"""
build_index.py
--------------
RAG Step 2: records -> embeddings (vectors) -> FAISS index -> saved to disk.

FAISS only stores the vectors (numbers). It does NOT store the original text or our
structured metadata, so we save those alongside in store.json (same order as the vectors).

Run this once (and again whenever the catalog or knowledge docs change):
    python build_index.py
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

import config
from ingest import load_all_records


def build_index():
    # 1. Gather all records (catalog items + knowledge chunks) -------------------
    records = load_all_records()
    texts = [r["text"] for r in records]
    metadata = [r["metadata"] for r in records]
    print(f"Collected {len(records)} records "
          f"({sum(m['type'] == 'catalog' for m in metadata)} catalog, "
          f"{sum(m['type'] == 'knowledge' for m in metadata)} knowledge).")

    # 2. Embed every record's text ----------------------------------------------
    print(f"Loading embedding model: {config.EMBED_MODEL} ...")
    model = SentenceTransformer(config.EMBED_MODEL)
    print("Encoding records into vectors ...")
    embeddings = model.encode(texts, show_progress_bar=True)

    # 3. Build the FAISS index ---------------------------------------------------
    emb = np.array(embeddings, dtype="float32")  # FAISS needs float32
    faiss.normalize_L2(emb)                       # normalize -> inner product = cosine
    dim = emb.shape[1]                            # 384 for all-MiniLM-L6-v2
    index = faiss.IndexFlatIP(dim)                # IP = inner product (cosine) index
    index.add(emb)
    print(f"FAISS index built: {index.ntotal} vectors, dim {dim}")

    # 4. Save the index + the text/metadata --------------------------------------
    config.DB_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(config.DB_DIR / "docs.index"))
    with open(config.DB_DIR / "store.json", "w", encoding="utf-8") as f:
        json.dump({"texts": texts, "metadata": metadata}, f, indent=2)

    print(f"\nSaved index + store to {config.DB_DIR}")
    print("Done. Knowledge base is ready. Run: python recommend.py")


if __name__ == "__main__":
    build_index()
