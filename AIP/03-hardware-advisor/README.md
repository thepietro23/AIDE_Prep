# 03 — AI & PC Hardware Advisor (a real-world RAG)

A RAG that recommends **realistic, current, budget-aware** hardware for a project —
solving the exact problem you hit when asking GPT/Claude directly:

| Problem with asking an LLM directly | How this RAG fixes it |
|-------------------------------------|------------------------|
| Suggests **outdated** hardware (frozen training data) | Answers come from a **catalog we control** + optional **live price fetch** |
| **Hallucinates** parts/prices | LLM may ONLY pick from a filtered **shortlist**; can't invent anything |
| Prices are **unrealistic / too costly** | A hard **budget filter** drops anything you can't afford |

### Best ideas borrowed from existing products
- **PCPartPicker** → live prices + compatibility checks (PSU/RAM rules)
- **AI PC Builder / MSI EZ** → conversational, asks budget + use-case
- **Logical Increments** → budget tiers (right answer per wallet)
- **Northflank/RunPod guides** → ML workload awareness (VRAM per model size)
- **Cloud calculators** → cloud GPU pricing + a buy-vs-rent break-even

## How it works (the RAG pipeline)

```
data/hardware_catalog.json   (structured: specs + prices + compatibility)
data/knowledge/*.md          (reasoning: VRAM rules, tiers, cloud-vs-local)
        │
        ▼  ingest.py        turn both into "records" (text + metadata)
        ▼  build_index.py   embed records -> FAISS vector index
        │
user asks ──► recommend.py
        ├─ retrieve.candidate_hardware()  → STRUCTURED filter (budget, VRAM, use-case)
        ├─ retrieve.semantic_search()     → relevant reasoning chunks
        └─ llm.ask_llm() (Groq)           → grounded recommendation
```

The twist vs a basic RAG: **hybrid retrieval** = semantic search (for reasoning)
+ structured numeric filtering (for budget/VRAM guarantees).

## Setup

```bash
# from repo root, with the .venv active
pip install -r 03-hardware-advisor/requirements.txt

# add your Groq key
#   edit 03-hardware-advisor/.env  ->  GROQ_API_KEY=...

cd 03-hardware-advisor
python build_index.py          # build the vector index (run once / after data edits)
```

## Use it

```bash
python recommend.py                                   # interactive Q&A
python recommend.py "fine-tune a 13B model, budget $900"   # one-shot
streamlit run ui.py                                   # web UI
```

## Files
| File | Job |
|------|-----|
| `config.py` | all settings (paths, model, budget knobs) |
| `data/hardware_catalog.json` | structured catalog: GPUs/CPUs/RAM/PSU/cloud + seed prices |
| `data/knowledge/*.md` | reasoning docs (VRAM, tiers, cloud-vs-local, compatibility) |
| `price_fetch.py` | best-effort live price refresh + seed fallback |
| `ingest.py` | catalog + docs → records (text + metadata) |
| `build_index.py` | records → embeddings → FAISS index |
| `retrieve.py` | **hybrid** retrieval (semantic + structured filter) |
| `recommend.py` | full pipeline → Groq → grounded answer |
| `llm.py` | Groq / Ollama wrapper |
| `ui.py` | Streamlit conversational UI |

> **Note on live prices:** retailers block scrapers and change their HTML, so live
> fetch is best-effort and OFF by default. The seed catalog is the reliable backbone;
> in production you'd swap in an official API (Amazon PA-API) or a price-tracking API.
