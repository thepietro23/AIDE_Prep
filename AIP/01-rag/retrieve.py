import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

import config

# Load everything we need to do retrieval: the FAISS index, the chunk text, and the metadata.
_model = SentenceTransformer(config.EMBED_MODEL)   # load embedding model
_index = faiss.read_index(str(config.DB_DIR / "docs.index"))

with open(config.DB_DIR / "store.json", "r", encoding="utf-8") as f:
    _store = json.load(f)
_chunks = _store["chunks"]
_metadata = _store["metadata"]


def retrieve(query, top_k = config.TOP_K):
    """Return the top_k chunks most relevant to the query.
    Each result: {"text": ..., "source": ..., "score": ...}
    """
    # 1. Embed the query the SAME way we embedded the chunks
    q = _model.encode([query])
    q = np.array(q, dtype="float32")
    faiss.normalize_L2(q)   # so inner product = cosine similarity

    # 2. Search the FAISS index for the top_k most similar chunks
    scores, indices = _index.search(q, top_k)   # shape: [1, top_k]

    # 3. Map each position back to its text and metadata, and return a list of dicts
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:   # FAISS returns -1 if there are fewer than top_k results
            continue
        results.append({
            "text": _chunks[idx],
            "source": _metadata[idx]["source"],
            "score": float(score)   # convert numpy.float32 to regular float
        })
    return results  


if __name__ == "__main__":
    query = "How many days do I have to request a refund?"
    print(f"Query: {query}\n")
    for i, r in enumerate(retrieve(query), 1):
        print(f"[{i}] score={r['score']:.3f}  source={r['source']}")
        print(r["text"][:200], "...\n")