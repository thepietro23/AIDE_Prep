"""
app.py
------
The full RAG pipeline: question -> retrieve -> build prompt -> LLM -> answer.

Usage:
    python app.py "your question here"
    python app.py                # then type questions interactively
"""

import sys
from retrieve import retrieve
from llm import ask_llm

# The prompt template. {context} = retrieved chunks, {question} = user query.
PROMPT_TEMPLATE = """You are a helpful support assistant for ZephyrPay.
Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't know based on the provided documents."

Context:
{context}

Question: {question}

Answer:"""


def answer_question(question):
    # 1. Retrieve the most relevant chunks
    results = retrieve(question)

    # 2. Join the chunk texts into one context block
    context = "\n\n".join(r["text"] for r in results)

    # 3. Fill the template
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    # 4. Ask the LLM
    answer = ask_llm(prompt)

    # 5. Collect the unique sources (for transparency)
    sources = sorted({r["source"] for r in results})
    return answer, sources


def _run(question):
    answer, sources = answer_question(question)
    print(f"\nQ: {question}")
    print(f"\nA: {answer}")
    print(f"\nSources: {', '.join(sources)}")


def main():
    if len(sys.argv) > 1:
        # Question passed on the command line
        _run(" ".join(sys.argv[1:]))
    else:
        # Interactive mode
        print("Ask a question (or type 'quit'):")
        while True:
            q = input("\n> ").strip()
            if q.lower() in {"quit", "exit", ""}:
                break
            _run(q)


if __name__ == "__main__":
    main()
