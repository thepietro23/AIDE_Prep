"""
prepare_data.py
---------------
Load the financial sentiment dataset and turn each row into an
instruction-formatted training example.

NOTE: we deliberately do NOT use datasets' `.map()` here. On this Windows
setup, calling pyarrow `.map()` after torch is imported segfaults. So we read
the columns into plain Python lists and format them in a normal loop instead.
Returns plain lists of dicts (no pyarrow objects held afterwards).
"""

import config   # FIRST: sets HF offline env before datasets loads

from datasets import load_dataset


def _records(ds):
    """Turn a raw dataset into a plain list of formatted dicts."""
    texts = ds["text"]      # column access -> plain Python list
    labels = ds["label"]
    records = []
    for text, label in zip(texts, labels):
        label_word = config.ID2LABEL[label]
        prompt = config.build_prompt(text)
        records.append({
            "prompt": prompt,                       # for evaluation (no answer)
            "label_word": label_word,               # the gold answer
            "sft_text": f"{prompt} {label_word}",   # what the model trains on
        })
    return records


def build_datasets():
    """Return (train_records, test_records) as plain Python lists of dicts."""
    train = _records(load_dataset(config.DATASET, split="train"))
    test = _records(load_dataset(config.DATASET, split="validation"))
    return train, test


if __name__ == "__main__":
    train, test = build_datasets()
    print(f"Train rows: {len(train)}")
    print(f"Test rows:  {len(test)}")
    from collections import Counter
    print("Train label distribution:", dict(Counter(r["label_word"] for r in train)))
    print("\n--- Example training text (sft_text) ---")
    print(train[0]["sft_text"])
    print("\n--- Example eval prompt + gold ---")
    print("PROMPT:", test[0]["prompt"])
    print("GOLD  :", test[0]["label_word"])
