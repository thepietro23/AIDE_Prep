"""
llm.py
------
A tiny wrapper that calls either Groq (cloud) or Ollama (local), depending on
config.LLM_BACKEND. The rest of the app calls ask_llm() and doesn't care which.

Supports an optional `system` message so we can give the model a strict persona
("you are a hardware advisor, only use the context, never invent prices").
"""

import requests
import config


def _ask_groq(prompt, system=None):
    """Call the Groq cloud API (needs GROQ_API_KEY in .env)."""
    from groq import Groq, AuthenticationError, APIConnectionError

    if not config.GROQ_API_KEY or config.GROQ_API_KEY.startswith("paste-"):
        raise SystemExit("No Groq key set. Put a valid key in .env (get one at "
                         "https://console.groq.com/keys), or set LLM_BACKEND=ollama.")

    client = Groq(api_key=config.GROQ_API_KEY)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        completion = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=messages,
            temperature=0.3,   # low -> factual, less "creative" (good for recommendations)
        )
    except AuthenticationError:
        raise SystemExit("Groq rejected the API key (401). Get a fresh one at "
                         "https://console.groq.com/keys and update .env.")
    except APIConnectionError:
        raise SystemExit("Can't reach Groq. If you're behind a corporate proxy, ensure "
                         "`truststore` is installed (it's in requirements.txt).")
    return completion.choices[0].message.content


def _ask_ollama(prompt, system=None):
    """Call the local Ollama HTTP API (needs `ollama serve` running)."""
    payload = {"model": config.OLLAMA_MODEL, "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system
    resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"]


def ask_llm(prompt, system=None):
    """Send prompt (+ optional system message) to whichever backend is configured."""
    if config.LLM_BACKEND == "groq":
        return _ask_groq(prompt, system)
    return _ask_ollama(prompt, system)   # default fallback: ollama


if __name__ == "__main__":
    print(f"Backend: {config.LLM_BACKEND}  Model: {config.GROQ_MODEL}")
    print(ask_llm("Reply with exactly: 'hardware advisor LLM is working'."))
