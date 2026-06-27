"""
recommend.py
------------
RAG Step 4: the full pipeline that turns a user's situation into a grounded
hardware recommendation.

Flow:
    user inputs (use-case, budget, model size, buy/rent)
      -> work out the minimum VRAM the workload needs
      -> structured shortlist of parts that FIT the budget + need   (retrieve.candidate_hardware)
      -> relevant reasoning chunks                                   (retrieve.semantic_search)
      -> strict prompt -> Groq -> grounded recommendation

The LLM is told to ONLY use the shortlist + context. It cannot invent a GPU or a price,
which is exactly what stops the "outdated / hallucinated / too expensive" problem.

Usage:
    python recommend.py                # interactive: it asks you the questions
    python recommend.py "I want to fine-tune a 13B model, budget $900"   # one-shot free text
"""

import re
import sys
from retrieve import semantic_search, candidate_hardware
from llm import ask_llm

# Known use-case keywords -> the catalog's use_case tags.
_USE_CASE_WORDS = {
    "train": "training", "fine-tune": "fine-tuning", "finetune": "fine-tuning",
    "fine tuning": "fine-tuning", "inference": "ai-inference", "infer": "ai-inference",
    "gaming": "gaming", "game": "gaming", "general": "general",
}


def parse_free_text(text):
    """Pull (budget_usd, model_size, use_case) out of a free-text request, so the
    STRUCTURED budget/VRAM filter still kicks in for one-shot CLI questions.
    Anything we can't find stays None (the pipeline then relaxes that filter)."""
    low = text.lower()

    # Budget: "$900", "900 dollars", "budget 900", "1.2k"
    budget = None
    m = re.search(r"\$\s?([0-9][0-9,]*)\b", low) or re.search(r"\b([0-9][0-9,]{2,})\s*(?:dollars|usd|rs|rupees|budget)?", low)
    if m:
        budget = int(m.group(1).replace(",", ""))
    mk = re.search(r"\b([0-9](?:\.[0-9])?)\s*k\b", low)   # "1.2k" -> 1200
    if mk and budget is None:
        budget = int(float(mk.group(1)) * 1000)

    # Model size: "13B", "7 b", "70b"
    ms = re.search(r"\b(7|13|34|70)\s*b\b", low)
    model_size = (ms.group(1) + "B") if ms else None

    # Use case: first keyword that appears.
    use_case = next((tag for word, tag in _USE_CASE_WORDS.items() if word in low), None)

    return budget, model_size, use_case

# Minimum VRAM (GB) to run a model comfortably in 4-bit, from vram_requirements.md.
# Used to set a hard floor so we never recommend a card too small for the model.
_MODEL_VRAM = {"7b": 6, "13b": 10, "34b": 20, "70b": 40}


def min_vram_for_model(model_size):
    """'13B' -> 10. Returns None if we don't recognise the size."""
    if not model_size:
        return None
    return _MODEL_VRAM.get(model_size.strip().lower().replace("-", ""))


SYSTEM_PROMPT = (
    "You are a no-nonsense hardware advisor for AI and general-purpose PCs. "
    "Hard rules: (1) Recommend ONLY hardware from the CANDIDATES list given to you. "
    "(2) NEVER invent a product or a price; use only the prices shown. "
    "(3) NEVER exceed the user's budget. (4) Prefer the CHEAPEST option that comfortably "
    "fits the workload -- more VRAM than needed is wasted money. (5) Always include a quick "
    "compatibility note (PSU, RAM) and a buy-vs-rent (cloud) comparison when relevant. "
    "Use the KNOWLEDGE section for your reasoning. Be concise and practical."
)

PROMPT_TEMPLATE = """USER SITUATION:
{situation}

CANDIDATES (the ONLY hardware you may recommend — already filtered to fit the budget & need):
{candidates}

KNOWLEDGE (use this for your reasoning about VRAM, budget tiers, compatibility, cloud-vs-local):
{knowledge}

Now give:
1. Top recommendation (which part + why, with its price).
2. A cheaper alternative and a step-up option from the candidates, if any.
3. Buy vs rent (cloud) — which makes sense for this user and why.
4. Compatibility check (PSU watts, system RAM) in one or two lines.
Keep it realistic and within budget."""


def _format_candidates(items):
    if not items:
        return "(none matched — tell the user honestly and suggest relaxing the budget or VRAM need.)"
    lines = []
    for it in items:
        m = it["metadata"]
        if m.get("price_usd_per_hour") is not None:
            price = f"${m['price_usd_per_hour']}/hr (cloud)"
        else:
            tag = "live" if m.get("price_live") else "seed"
            price = f"${m.get('price_usd'):,} (~Rs {m.get('price_inr'):,}) [{tag}]"
        vram = f"{m['vram_gb']}GB VRAM" if m.get("vram_gb") else "—"
        lines.append(f"- {m['name']} | {m['category']}/{m['tier']} | {vram} | {price}")
    return "\n".join(lines)


def recommend(use_case=None, budget_usd=None, model_size=None, free_text=None):
    """Run the full pipeline and return (answer_text, candidates, knowledge_sources)."""
    # For one-shot free text, extract the constraints so the STRUCTURED filter still
    # applies (this is what guarantees "within budget" + "enough VRAM").
    if free_text:
        b, ms, uc = parse_free_text(free_text)
        budget_usd = budget_usd or b
        model_size = model_size or ms
        use_case = use_case or uc

    min_vram = min_vram_for_model(model_size)

    # 1. Structured shortlist. If no BUY option fits (cloud alone doesn't count),
    #    relax filters step by step so we still surface a real card to buy.
    def _has_buy(items):
        return any(it["metadata"]["category"] != "cloud-gpu" for it in items)

    cands = candidate_hardware(budget_usd=budget_usd, use_case=use_case, min_vram_gb=min_vram)
    if not _has_buy(cands):
        cands = candidate_hardware(budget_usd=budget_usd, min_vram_gb=min_vram)   # drop use_case
    if not _has_buy(cands):
        cands = candidate_hardware(budget_usd=budget_usd)                          # drop VRAM too

    # 2. Build a query for semantic retrieval of the reasoning docs.
    query = free_text or (
        f"best hardware for {use_case or 'AI'} "
        f"{('with a ' + model_size + ' model') if model_size else ''} "
        f"on a budget of ${budget_usd or 'flexible'}, buy vs cloud, compatibility"
    )
    knowledge = semantic_search(query, type_filter="knowledge")

    # 3. Describe the user's situation in plain words for the prompt.
    situation = free_text or (
        f"Use case: {use_case or 'general AI'}. "
        f"Budget: ${budget_usd if budget_usd else 'flexible'}. "
        f"Target model size: {model_size or 'n/a'} "
        f"(needs >= {min_vram}GB VRAM)." if min_vram else
        f"Use case: {use_case or 'general AI'}. Budget: ${budget_usd if budget_usd else 'flexible'}."
    )

    # 4. Assemble the prompt and ask the LLM.
    prompt = PROMPT_TEMPLATE.format(
        situation=situation,
        candidates=_format_candidates(cands),
        knowledge="\n\n".join(k["text"] for k in knowledge),
    )
    answer = ask_llm(prompt, system=SYSTEM_PROMPT)

    sources = sorted({k["metadata"]["source"] for k in knowledge})
    return answer, cands, sources


def _print_result(answer, cands, sources):
    print("\n" + "=" * 70 + "\nRECOMMENDATION\n" + "=" * 70)
    print(answer)
    print("\n--- shortlist considered ---")
    print(_format_candidates(cands))
    print(f"\n--- reasoning sources ---\n{', '.join(sources)}")


def _interactive():
    print("Hardware Advisor — answer a few questions (Enter to skip any).\n")
    use_case = input("Use case? [ai-inference / fine-tuning / training / general / gaming]: ").strip() or None
    model_size = input("Target model size? [7B / 13B / 34B / 70B, or blank]: ").strip() or None
    budget_raw = input("Budget in USD? (e.g. 900, or blank for flexible): ").strip()
    budget = int(budget_raw) if budget_raw.isdigit() else None
    _print_result(*recommend(use_case=use_case, budget_usd=budget, model_size=model_size))


def main():
    if len(sys.argv) > 1:
        _print_result(*recommend(free_text=" ".join(sys.argv[1:])))
    else:
        _interactive()


if __name__ == "__main__":
    main()
