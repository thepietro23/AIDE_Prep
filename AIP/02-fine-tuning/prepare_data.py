"""
prepare_data.py
---------------
Load the financial sentiment dataset and turn each row into an
instruction-formatted training example.

  raw row:   {"text": "$BYND ... reels in expectations", "label": 0}
  becomes ->
      prompt: "Classify ... Text: $BYND ... Sentiment:"
      answer: "bearish"
      sft_text (prompt + answer) is what the model trains on.
"""

from datasets import load_dataset

import config


def _format(row):
    """Add the prompt, the gold answer word, and the full SFT text to a row."""
    label_word = config.ID2LABEL[row["label"]]
    prompt = config.build_prompt(row["text"])
    return {
        "prompt": prompt,                       # used for evaluation (no answer)
        "label_word": label_word,               # the gold answer
        "sft_text": f"{prompt} {label_word}",   # what the model trains on
    }


def build_datasets():
    """Return (train_ds, test_ds) with the extra formatted columns added."""
    train_ds = load_dataset(config.DATASET, split="train").map(_format)
    test_ds = load_dataset(config.DATASET, split="validation").map(_format)
    return train_ds, test_ds


if __name__ == "__main__":
    train_ds, test_ds = build_datasets()
    print(f"Train rows: {len(train_ds)}")
    print(f"Test rows:  {len(test_ds)}")

    # label distribution in the training set
    from collections import Counter
    dist = Counter(train_ds["label_word"])
    print("Train label distribution:", dict(dist))

    print("\n--- Example training text (sft_text) ---")
    print(train_ds[0]["sft_text"])
    print("\n--- Example eval prompt + gold label ---")
    print("PROMPT:", test_ds[0]["prompt"])
    print("GOLD  :", test_ds[0]["label_word"])
