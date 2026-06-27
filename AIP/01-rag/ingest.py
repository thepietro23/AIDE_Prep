"""
ingest.py
---------
RAG Step 1: read documents and split them into chunks (small pieces).

Two jobs:
  1. load_documents() -> read all .txt files in the data/ folder
  2. chunk_text()     -> split a large text into overlapping chunks
"""

import config


def load_documents():
    """
    Read all .txt files inside config.DATA_DIR (= 01-rag/data).
    Return: list of (filename, text) tuples.
    (We keep the filename so we can show the source of an answer later.)
    """
    docs = []
    for file in config.DATA_DIR.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:   # encoding matters on Windows
            docs.append((file.name, f.read()))         # save (name, text)
    return docs


def chunk_text(text, chunk_size=config.CHUNK_SIZE, overlap=config.CHUNK_OVERLAP):
    """Split a large text into overlapping chunks. Return: list of strings."""
    if overlap >= chunk_size:                          # safety: otherwise infinite loop
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)
        start = start + (chunk_size - overlap)
    return chunks


if __name__ == "__main__":
    documents = load_documents()
    print(f"Total documents found: {len(documents)}\n")

    all_chunks = []
    for filename, text in documents:
        chunks = chunk_text(text)                      # defaults come from config
        all_chunks.extend(chunks)
        print(f"  {filename}: {len(text)} chars -> {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")
    print("\n--- First chunk ---")
    print(all_chunks[0])
