"""
ingest.py
---------
RAG Step 1: turn our two kinds of source data into a single list of "records"
that we can embed and search.

Two sources, two record types:
  1. CATALOG items (structured JSON) -> one record per hardware item. We write a
     readable sentence for the embedding, and keep the structured fields
     (price, vram, use_cases...) in metadata so retrieve.py can FILTER on them.
  2. KNOWLEDGE docs (markdown) -> chunked into pieces, like a normal text RAG.
     These carry the "reasoning" (VRAM rules, budget tiers, cloud-vs-local, compatibility).

Every record looks like:  {"text": <str to embed>, "metadata": {...}}
"""

import config
from price_fetch import load_catalog, refresh_catalog


def item_to_text(item):
    """Turn one structured catalog item into a readable sentence for embedding.
    (The embedding model understands prose far better than raw JSON.)"""
    specs = item.get("specs", {})
    spec_str = ", ".join(f"{k}={v}" for k, v in specs.items())

    if "price_usd" in item:
        price = f"approx ${item['price_usd']:,} (~Rs {item.get('price_inr', 0):,})"
    elif "price_usd_per_hour" in item:
        price = f"approx ${item['price_usd_per_hour']}/hour (cloud rental)"
    else:
        price = "price n/a"

    return (
        f"{item['name']} is a {item['tier']}-tier {item['category']}. "
        f"Good for: {', '.join(item.get('use_cases', []))}. "
        f"Specs: {spec_str}. Price: {price}. "
        f"{item.get('good_for', '')} Watch out: {item.get('watch_out', '')}"
    )


def load_catalog_records(catalog=None):
    """Build one record per catalog item, with structured metadata for filtering."""
    if catalog is None:
        catalog = refresh_catalog(load_catalog(), verbose=False)

    records = []
    for key, items in catalog.items():
        if key.startswith("_"):       # skip "_meta"
            continue
        for item in items:
            specs = item.get("specs", {})
            records.append({
                "text": item_to_text(item),
                "metadata": {
                    "type": "catalog",
                    "id": item["id"],
                    "name": item["name"],
                    "category": item["category"],
                    "tier": item["tier"],
                    "use_cases": item.get("use_cases", []),
                    "vram_gb": specs.get("vram_gb"),          # may be None (non-GPU)
                    "price_usd": item.get("price_usd"),       # one-off buy
                    "price_usd_per_hour": item.get("price_usd_per_hour"),  # cloud
                    "price_inr": item.get("price_inr"),
                    "price_live": item.get("price_live", False),
                    "source": "hardware_catalog.json",
                },
            })
    return records


def chunk_text(text, chunk_size=700, overlap=120):
    """Split a long markdown doc into overlapping chunks (same idea as 01-rag)."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += (chunk_size - overlap)
    return chunks


def load_knowledge_records():
    """Read every .md in data/knowledge/, chunk it, and tag each chunk's source."""
    records = []
    for file in sorted(config.KNOWLEDGE_DIR.glob("*.md")):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        for chunk in chunk_text(text):
            records.append({
                "text": chunk,
                "metadata": {"type": "knowledge", "source": file.name},
            })
    return records


def load_all_records():
    """Catalog records + knowledge records, combined."""
    return load_catalog_records() + load_knowledge_records()


if __name__ == "__main__":
    cat_recs = load_catalog_records()
    kb_recs = load_knowledge_records()
    print(f"Catalog records:   {len(cat_recs)}")
    print(f"Knowledge records: {len(kb_recs)}")
    print("\n--- sample catalog record text ---")
    print(cat_recs[0]["text"])
    print("\n--- sample knowledge record text ---")
    print(kb_recs[0]["text"][:200], "...")
