# 🧠 AIDE_Prep — AI / ML Development & Interview Prep

A personal, hands-on workspace for mastering **Machine Learning, Deep Learning, and Applied AI (LLMs/RAG)** — built from scratch implementations, complete concept guides, and end-to-end mini-projects.

> Personal learning repository — code, notes, and projects built while preparing for AI/ML engineering roles.

---

## 📂 Repository Structure

| Folder | What's inside |
|--------|---------------|
| [`AIP/`](AIP/) | **Applied AI Projects** — production-style RAG apps, fine-tuning, and an LLM hardware advisor |
| [`Expert/`](Expert/) | **ML algorithms from scratch** — Linear & Tree models with revision notes |
| [`IMP_Notes/`](IMP_Notes/) | **Complete concept guides** (20 algorithms) — Hindi + English (`Eng/`) |
| [`DeepML/`](DeepML/) | Deep ML / DL learning notebooks & notes |
| [`DL/`](DL/) | Deep Learning notes |
| [`CRag/`](CRag/) | Custom RAG (Retrieval-Augmented Generation) experiments |
| [`api/`](api/) | LLM API experiments — LangChain, Groq, chatbots |
| [`mlflow/`](mlflow/) | MLflow experiment tracking practice |
| [`Week-1/`](Week-1/) | Foundations — pandas, pipelines, Titanic walkthrough |
| [`Prep/`](Prep/) | Misc practice notebooks |

Top-level `.xlsx` / `.docx` files are interview trackers and study roadmaps.

---

## 🚀 Applied AI Projects (`AIP/`)

| # | Project | Description |
|---|---------|-------------|
| 01 | [**RAG App**](AIP/01-rag/) | Document Q&A over a FAISS vector store with an LLM — ingest → index → retrieve → answer |
| 02 | [**Fine-Tuning**](AIP/02-fine-tuning/) | Data prep, baseline, and inference pipeline for model fine-tuning |
| 03 | [**Hardware Advisor**](AIP/03-hardware-advisor/) | RAG-powered assistant that recommends GPU/hardware for local LLMs (VRAM, budget tiers, compatibility) |

Each project ships with its own `requirements.txt`, config, and a Streamlit/CLI entry point.

---

## 📘 Concept Guides (`IMP_Notes/`)

Deep-dive guides covering **20 core ML algorithms**, available in both **Hindi** and **English** (`Eng/`):

- **Regression** — Linear, Normal Equation, Polynomial, Ridge, Lasso, ElasticNet
- **Classification** — Logistic Regression (binary + multiclass)
- **Tree / Ensembles** — Decision Tree, Random Forest, AdaBoost, Gradient Boosting, XGBoost, LightGBM
- **Clustering** — K-Means, K-Medoids, DBSCAN, Hierarchical, Gaussian Mixture Models
- **Dimensionality Reduction** — PCA, Kernel PCA

`Expert/` complements these with **from-scratch implementations** and revision notes.

---

## 🛠️ Tech Stack

`Python` · `NumPy` · `pandas` · `scikit-learn` · `FAISS` · `LangChain` · `Groq` · `MLflow` · `Jupyter`

---

## ⚙️ Getting Started

```bash
# Clone
git clone https://github.com/thepietro23/AIDE_Prep.git
cd AIDE_Prep

# Example: run the RAG project
cd AIP/01-rag
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python build_index.py        # build the vector index
streamlit run ui.py          # launch the app
```

> ℹ️ Virtual environments, model weights (`*.safetensors`, etc.), and `.env` secrets are intentionally **git-ignored**. Add your own API keys in a local `.env` per project.

---

## 📄 License

Released under the [MIT License](LICENSE).
