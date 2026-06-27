"""
llm.py
------
A tiny wrapper that calls either Ollama (local) or Groq (cloud),
depending on config.LLM_BACKEND. The rest of the app doesn't care which.
"""

import requests
import config


def _ask_ollama(prompt):
    """Call the local Ollama HTTP API (needs `ollama serve` running)."""
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": config.OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def _ask_groq(prompt):
    """Call the Groq cloud API (needs GROQ_API_KEY in .env)."""
    from groq import Groq
    client = Groq(api_key=config.GROQ_API_KEY)
    completion = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


def ask_llm(prompt):
    """Send the prompt to whichever backend config.LLM_BACKEND selects."""
    if config.LLM_BACKEND == "groq":
        return _ask_groq(prompt)
    return _ask_ollama(prompt)   # default: ollama


if __name__ == "__main__":
    print(f"Backend: {config.LLM_BACKEND}")
    print(ask_llm("Say 'hello, RAG is working' in 5 words."))
