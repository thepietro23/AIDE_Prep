"""
evaluate.py
-----------
Measure the FINE-TUNED model's accuracy AFTER training. Loads the same base
model as baseline.py and attaches the trained LoRA adapter, so the only
difference vs the baseline is the fine-tuning itself.

Same Windows ordering rule: build data BEFORE importing torch.
"""

import config   # FIRST: sets HF offline env before anything loads
from prepare_data import build_datasets


def main():
    # 1. Build the dataset BEFORE importing torch
    _, test = build_datasets()
    test = test[:config.EVAL_SAMPLES]
    prompts = [r["prompt"] for r in test]
    gold = [r["label_word"] for r in test]

    # 2. Now import torch and load base model + LoRA adapter
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    from infer import predict_labels

    print(f"Loading base model + LoRA adapter from {config.ADAPTER_DIR}")
    tokenizer = AutoTokenizer.from_pretrained(config.BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        config.BASE_MODEL, dtype=torch.float16, device_map="cuda"
    )
    model = PeftModel.from_pretrained(model, str(config.ADAPTER_DIR))

    # 3. Predict + score
    print(f"Evaluating fine-tuned model on {len(prompts)} examples...")
    preds = predict_labels(model, tokenizer, prompts)

    from sklearn.metrics import accuracy_score, classification_report
    acc = accuracy_score(gold, preds)
    print(f"\n=== FINE-TUNED (after QLoRA) ===")
    print(f"Accuracy: {acc:.3f}")
    print(classification_report(gold, preds, labels=config.LABELS, zero_division=0))


if __name__ == "__main__":
    main()
