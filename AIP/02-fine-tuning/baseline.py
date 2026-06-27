"""
baseline.py
-----------
Measure the base model's accuracy on financial sentiment BEFORE fine-tuning.
This is the "before" number we compare against later.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.metrics import accuracy_score, classification_report

import config
from prepare_data import build_datasets
from infer import predict_labels


def main():
    # 1. Load the base model + tokenizer (fp16 on GPU; 0.5B fits easily)
    print(f"Loading base model: {config.BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(config.BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"          # correct side for generation
    model = AutoModelForCausalLM.from_pretrained(
        config.BASE_MODEL, dtype=torch.float16, device_map="cuda"
    )

    # 2. Take a sample of the test set (full set is slow on a laptop GPU)
    _, test_ds = build_datasets()
    test_ds = test_ds.select(range(config.EVAL_SAMPLES))
    prompts = test_ds["prompt"]
    gold = test_ds["label_word"]

    # 3. Predict + score
    print(f"Evaluating base model on {len(prompts)} examples...")
    preds = predict_labels(model, tokenizer, prompts)

    acc = accuracy_score(gold, preds)
    print(f"\n=== BASELINE (no fine-tuning) ===")
    print(f"Accuracy: {acc:.3f}")
    print(classification_report(gold, preds, labels=config.LABELS, zero_division=0))


if __name__ == "__main__":
    main()
