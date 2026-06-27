"""
ui.py
-----
A Streamlit UI that ASKS you the questions (like an AI PC builder) and then shows a
grounded recommendation + the exact shortlist it chose from.

Run with:
    streamlit run 03-hardware-advisor/ui.py
"""

import streamlit as st

import config
from recommend import recommend

st.set_page_config(page_title="AI Hardware Advisor", page_icon="🖥️")
st.title("🖥️ AI & PC Hardware Advisor")
st.caption("Realistic, current, budget-aware hardware picks — grounded in a live catalog, not the model's memory.")

# --- Sidebar: show config + how it works ---
with st.sidebar:
    st.header("Settings")
    st.write(f"**LLM backend:** `{config.LLM_BACKEND}`")
    st.write(f"**Model:** `{config.GROQ_MODEL if config.LLM_BACKEND == 'groq' else config.OLLAMA_MODEL}`")
    st.write(f"**Live prices:** `{config.ENABLE_LIVE_PRICES}`")
    st.divider()
    st.markdown(
        "**How it works**\n\n"
        "1. Your budget + workload set a hard filter.\n"
        "2. Only parts that *fit* are shortlisted.\n"
        "3. Groq explains the pick using the knowledge docs.\n\n"
        "It can never suggest a part over budget or invent a price."
    )

# --- The questions (AI-PC-builder style form) ---
with st.form("advisor"):
    col1, col2 = st.columns(2)
    with col1:
        use_case = st.selectbox(
            "What will you do?",
            ["ai-inference", "fine-tuning", "training", "general", "gaming"],
        )
        model_size = st.selectbox("Target model size (LLM)?", ["n/a", "7B", "13B", "34B", "70B"])
    with col2:
        budget = st.slider("Budget (USD)", 300, 4000, 1200, step=100)
        st.caption("Enterprise (80GB+) GPUs are rent-only and shown as cloud options.")
    extra = st.text_input("Anything else? (optional free text)", placeholder="e.g. I already have a 750W PSU")
    submitted = st.form_submit_button("Recommend hardware")

if submitted:
    free_text = extra.strip() or None
    ms = None if model_size == "n/a" else model_size
    with st.spinner("Filtering catalog and reasoning with Groq..."):
        answer, cands, sources = recommend(
            use_case=use_case, budget_usd=budget, model_size=ms, free_text=free_text
        )
    st.markdown(answer)

    with st.expander("Shortlist the advisor chose from"):
        for it in cands:
            m = it["metadata"]
            if m.get("price_usd_per_hour") is not None:
                price = f"${m['price_usd_per_hour']}/hr (cloud)"
            else:
                tag = "live" if m.get("price_live") else "seed"
                price = f"${m.get('price_usd'):,} ({tag})"
            vram = f"{m['vram_gb']}GB" if m.get("vram_gb") else "—"
            st.write(f"**{m['name']}** · {m['category']}/{m['tier']} · {vram} · {price}")

    st.caption(f"Reasoning sources: {', '.join(sources)}")
