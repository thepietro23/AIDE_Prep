"""
build_index.py
---------------
RAG Step 2: turn chunks into embeddings and store them in a FAISS index.

Pipeline:
    documents -> chunks -> embeddings (vectors) -> FAISS index -> saved to disk

We also save the chunk text + metadata in a JSON file, because FAISS only
stores the vectors (numbers), NOT the original text.
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

import config
from ingest import load_documents, chunk_text


def build_index():
    # 1. Collect all chunks + their source metadata -------------------------
    all_chunks = []   # the chunk texts
    metadata = []     # info about each chunk (same order as all_chunks)

    documents = load_documents()
    for filename, text in documents:
        for chunk in chunk_text(text):
            all_chunks.append(chunk)
            metadata.append({"source": filename})

    print(f"Collected {len(all_chunks)} chunks from {len(documents)} document(s)")

    # 2. Load the embedding model and embed every chunk ---------------------
    # First run downloads the model (~90MB), then it loads from cache.
    print(f"Loading embedding model: {config.EMBED_MODEL} ...")
    model = SentenceTransformer(config.EMBED_MODEL)

    print("Encoding chunks into vectors ...")
    embeddings = model.encode(all_chunks)   # shape: [num_chunks, 384]

    # 3. Build the FAISS index ---------------------------------------------
    emb = np.array(embeddings, dtype="float32")   # FAISS needs float32
    faiss.normalize_L2(emb)                        # so inner product = cosine sim

    dimension = emb.shape[1]                       # 384 for all-MiniLM-L6-v2
    index = faiss.IndexFlatIP(dimension)           # IP = inner product index
    index.add(emb)                                 # add all vectors

    print(f"FAISS index built: {index.ntotal} vectors, dimension {dimension}")

    # 4. Save the index + the text/metadata to disk ------------------------
    config.DB_DIR.mkdir(exist_ok=True)             # make faiss_store/ folder
    index_path = config.DB_DIR / "docs.index"
    store_path = config.DB_DIR / "store.json"

    faiss.write_index(index, str(index_path))      # save the vectors
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump({"chunks": all_chunks, "metadata": metadata}, f, indent=2)

    print(f"\nSaved:\n  index -> {index_path}\n  store -> {store_path}")
    print("Done. The knowledge base is ready to search.")


if __name__ == "__main__":
    build_index()
