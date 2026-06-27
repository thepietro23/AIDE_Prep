"""
retrieve.py
-----------
RAG Step 3: retrieval. This file is the brain of the advisor.

A plain RAG only does SEMANTIC search ("find chunks similar to the question").
That alone can't guarantee "within my budget" or "enough VRAM" -- those are HARD
numeric facts. So we do HYBRID retrieval:

  A) semantic_search()    -> find relevant KNOWLEDGE (the reasoning: VRAM rules,
                             budget tiers, cloud-vs-local, compatibility).
  B) candidate_hardware() -> structured FILTER over the catalog: drop anything over
                             budget, keep items matching the use-case / VRAM need,
                             rank the survivors. This is what makes answers REALISTIC
                             and REASONABLY PRICED (the whole point of the project).

recommend.py combines both and hands them to the LLM.
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

import config

# Load the embedding model, the FAISS index, and the saved texts+metadata once.
_model = SentenceTransformer(config.EMBED_MODEL)
_index = faiss.read_index(str(config.DB_DIR / "docs.index"))
with open(config.DB_DIR / "store.json", "r", encoding="utf-8") as f:
    _store = json.load(f)
_texts = _store["texts"]
_metadata = _store["metadata"]


# ---------------------------------------------------------------------------
# A) Semantic search -- "what knowledge is relevant to this question?"
# ---------------------------------------------------------------------------
def semantic_search(query, top_k=config.TOP_K, type_filter=None):
    """Return the top_k records most similar to the query (by cosine similarity).
    type_filter: None | "knowledge" | "catalog" to restrict the kind of record."""
    q = np.array(_model.encode([query]), dtype="float32")
    faiss.normalize_L2(q)

    # Over-fetch, then filter by type, so a type_filter still returns top_k items.
    scores, indices = _index.search(q, top_k * 3)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        meta = _metadata[idx]
        if type_filter and meta["type"] != type_filter:
            continue
        results.append({"text": _texts[idx], "metadata": meta, "score": float(score)})
        if len(results) >= top_k:
            break
    return results


# ---------------------------------------------------------------------------
# B) Structured filter -- "which parts are realistic for THIS budget + need?"
# ---------------------------------------------------------------------------
def _use_case_matches(requested, item_tags):
    """Loose match so a request for 'ai-inference' also accepts 'ai-inference-small'
    (and vice-versa). True if the requested tag equals, is a prefix of, or has as a
    prefix any of the item's tags. Keeps the catalog tags granular without making the
    filter miss obviously-suitable parts."""
    if requested is None:
        return True
    for tag in item_tags:
        if requested == tag or tag.startswith(requested) or requested.startswith(tag):
            return True
    return False


def _catalog_items():
    """All catalog records straight from the saved store (already has metadata)."""
    return [
        {"text": t, "metadata": m}
        for t, m in zip(_texts, _metadata)
        if m["type"] == "catalog"
    ]


def candidate_hardware(budget_usd=None, use_case=None, min_vram_gb=None,
                       category="gpu", include_cloud=True,
                       max_items=config.MAX_CANDIDATES):
    """Structured shortlist of hardware that ACTUALLY fits the constraints.

    Filters applied (any that are provided):
      - category    : "gpu" / "cpu" / "ram" / "psu" (cloud handled separately)
      - budget_usd  : drop one-off-buy items priced above the budget  <-- the key filter
      - use_case    : keep items whose use_cases list contains this tag
      - min_vram_gb : keep items with at least this much VRAM

    Ranking: most capable first (VRAM desc), then cheaper first -> the best card
    that still fits the wallet floats to the top. Cloud options are appended so the
    LLM can offer a rent-vs-buy comparison.
    """
    buy_items, cloud_items = [], []

    for item in _catalog_items():
        m = item["metadata"]

        # Split cloud (per-hour) from one-off-buy parts.
        is_cloud = m["category"] == "cloud-gpu"
        if is_cloud:
            if include_cloud and _use_case_matches(use_case, m["use_cases"]):
                cloud_items.append(item)
            continue

        # Category filter (e.g. only GPUs).
        if category and m["category"] != category:
            continue
        # Budget filter -- the heart of "reasonably priced". Over budget => dropped.
        if budget_usd is not None and m.get("price_usd") and m["price_usd"] > budget_usd:
            continue
        # Use-case filter (loose: 'ai-inference' also accepts 'ai-inference-small').
        if not _use_case_matches(use_case, m["use_cases"]):
            continue
        # VRAM floor (so we never suggest a card too small for the target model).
        if min_vram_gb is not None:
            if not m.get("vram_gb") or m["vram_gb"] < min_vram_gb:
                continue
        buy_items.append(item)

    # Rank: more VRAM first (more capable), then cheaper first.
    buy_items.sort(
        key=lambda it: (-(it["metadata"].get("vram_gb") or 0),
                        it["metadata"].get("price_usd") or 1e9)
    )

    shortlist = buy_items[:max_items]
    if include_cloud:
        shortlist += cloud_items
    return shortlist


if __name__ == "__main__":
    print("=== semantic_search('how much vram for a 13B model?') ===")
    for r in semantic_search("how much vram for a 13B model?", top_k=3, type_filter="knowledge"):
        print(f"[{r['score']:.3f}] {r['metadata']['source']}: {r['text'][:90]}...")

    print("\n=== candidate_hardware(budget=$800, fine-tuning, min 24GB VRAM) ===")
    for it in candidate_hardware(budget_usd=800, use_case="fine-tuning", min_vram_gb=24):
        m = it["metadata"]
        price = m.get("price_usd") or f"{m.get('price_usd_per_hour')}/hr"
        print(f"  {m['name']:<34} vram={m.get('vram_gb')}  ${price}")
