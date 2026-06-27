"""
ui.py
-----
A simple Streamlit chat UI on top of the RAG pipeline.

Run with:
    streamlit run 01-rag/ui.py
"""

import streamlit as st

import config
from app import answer_question

st.set_page_config(page_title="ZephyrPay Support RAG", page_icon="💬")

st.title("💬 ZephyrPay Support Assistant")
st.caption("Ask about refunds, limits, support hours — answers come only from the policy document.")

# --- Sidebar: show the current config (nice for demos) ---
with st.sidebar:
    st.header("Settings")
    st.write(f"**LLM backend:** `{config.LLM_BACKEND}`")
    model = config.GROQ_MODEL if config.LLM_BACKEND == "groq" else config.OLLAMA_MODEL
    st.write(f"**Model:** `{model}`")
    st.write(f"**Embeddings:** `{config.EMBED_MODEL}`")
    st.write(f"**Top-k chunks:** `{config.TOP_K}`")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

# --- Chat history (kept across reruns in session_state) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption(f"Sources: {', '.join(msg['sources'])}")

# --- New question input ---
if question := st.chat_input("Ask a question..."):
    # Show the user's message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Get and show the assistant's answer
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and thinking..."):
            answer, sources = answer_question(question)
        st.markdown(answer)
        st.caption(f"Sources: {', '.join(sources)}")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
