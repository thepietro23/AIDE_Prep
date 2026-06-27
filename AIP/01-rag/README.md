# 💬 ZephyrPay Support RAG

A small but complete **Retrieval-Augmented Generation (RAG)** system that answers
questions about a company policy document — and **refuses to answer** anything not
in the documents (no hallucinations).

Built from scratch with FAISS + sentence-transformers, with a pluggable LLM backend
(local **Ollama** or cloud **Groq**) and a **Streamlit** chat UI.

---

## What it does

Ask a natural-language question → the system finds the most relevant pieces of the
document → an LLM answers using **only** that context, and cites its source.

```
Q: How many days do I have to request a refund?
A: Customers can request a refund within 14 calendar days of a transaction.
   Refunds for "ZephyrGold" premium subscriptions are allowed only within 7 days.
   Sources: zephyrpay_policies.txt

Q: Who is the CEO of ZephyrPay?
A: I don't know based on the provided documents.
```

---

## Architecture

```
                          INGEST (one time)
  documents ──► chunk ──► embed ──► FAISS index ──► saved to disk
   (.txt)      (overlap)  (vectors)               (docs.index + store.json)

                          QUERY (every question)
  question ──► embed ──► search FAISS ──► top-k chunks ──► prompt+LLM ──► answer
```

| File | Responsibility |
|------|----------------|
| `config.py`       | All settings (model, chunk size, top-k, paths, backend) |
| `ingest.py`       | Read `.txt` documents and split them into overlapping chunks |
| `build_index.py`  | Embed chunks and build/save the FAISS index + text store |
| `retrieve.py`     | Embed a query and return the top-k most similar chunks |
| `llm.py`          | Call Ollama (local) or Groq (cloud) — chosen via config |
| `app.py`          | Full pipeline: question → retrieve → prompt → answer (CLI) |
| `ui.py`           | Streamlit chat interface |

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install streamlit          # for the UI

# 2. Configure (copy and edit)
#    LLM_BACKEND=ollama   (default, local) — needs `ollama serve` + a pulled model
#    LLM_BACKEND=groq     (cloud)          — needs GROQ_API_KEY
```

Edit settings in `.env` (see the keys at the top of `config.py`).

## Usage

```bash
# 1. Build the index from the documents in data/
python build_index.py

# 2a. Ask a question from the command line
python app.py "What is the wallet limit after KYC verification?"

# 2b. Or launch the chat UI
streamlit run ui.py
```

To add your own knowledge base, drop `.txt` files into `data/` and re-run
`python build_index.py`.

---

## Key concepts demonstrated

- **Chunking with overlap** — so context isn't cut mid-sentence.
- **Embeddings + vector search** — cosine similarity via L2-normalized inner product (FAISS `IndexFlatIP`).
- **Grounding / anti-hallucination** — the prompt forces answers to come only from retrieved context.
- **Source attribution** — every answer reports which document it came from.
- **Backend abstraction** — the app is agnostic to local vs cloud LLM.

## Possible improvements

- Section-aware chunking (current char-based splitting can rank chunks imperfectly).
- Multi-document knowledge bases with richer metadata filtering.
- Re-ranking the retrieved chunks before sending them to the LLM.
- Streaming responses in the UI.
