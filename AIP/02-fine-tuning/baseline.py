"""
baseline.py
-----------
Measure the base model's accuracy on financial sentiment BEFORE fine-tuning.

IMPORTANT (Windows): we build the dataset FIRST and import torch only AFTER,
because pyarrow dataset ops crash if torch's threading is initialized first.
"""

import config   # FIRST: sets HF offline env before anything loads
from prepare_data import build_datasets


def main():
    # 1. Build the dataset BEFORE importing torch (avoids the pyarrow/torch crash)
    _, test = build_datasets()
    test = test[:config.EVAL_SAMPLES]
    prompts = [r["prompt"] for r in test]
    gold = [r["label_word"] for r in test]

    # 2. NOW import torch and load the model
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from infer import predict_labels

    print(f"Loading base model: {config.BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(config.BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        config.BASE_MODEL, dtype=torch.float16, device_map="cuda"
    )

    # 3. Predict + score
    print(f"Evaluating base model on {len(prompts)} examples...")
    preds = predict_labels(model, tokenizer, prompts)

    from sklearn.metrics import accuracy_score, classification_report
    acc = accuracy_score(gold, preds)
    print(f"\n=== BASELINE (no fine-tuning) ===")
    print(f"Accuracy: {acc:.3f}")
    print(classification_report(gold, preds, labels=config.LABELS, zero_division=0))


if __name__ == "__main__":
    main()
