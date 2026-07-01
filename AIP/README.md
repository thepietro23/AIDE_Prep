# AIP — RAG and Fine-tuning Learning Projects

This repo holds two separate projects, kept apart so the two concepts stay clear:

| Folder | Topic | Status |
|--------|-------|--------|
| [`01-rag/`](01-rag/) | Retrieval-Augmented Generation (RAG) | ✅ Working |
| [`02-fine-tuning/`](02-fine-tuning/) | Model fine-tuning (QLoRA, financial sentiment) | ✅ Working |

## RAG vs Fine-tuning — in one line

- **RAG** = give the model knowledge from *outside* (find documents, put them in the context). Best when the data keeps changing.
- **Fine-tuning** = put knowledge/behaviour *inside* the model (by retraining). Best when you need a fixed style/skill.

Real systems often use **both together**.

## Setup (common to both projects)

- Python 3.11+
- [Ollama](https://ollama.com) — for local models (you have qwen2.5:7b, qwen2.5:3b, phi4)
- [Groq](https://console.groq.com/keys) — free fast cloud API (optional)

Each folder has its own steps. Start with the RAG project.
