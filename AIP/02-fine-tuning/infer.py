"""
infer.py
--------
Shared inference helpers used by both baseline.py and evaluate.py, so the
"before" and "after" numbers are measured in exactly the same way.
"""

import torch
import config


def parse_label(generated_text):
    """Find which sentiment word the model produced. Return it, or 'unknown'."""
    text = generated_text.strip().lower()
    for label in config.LABELS:          # bearish / bullish / neutral
        if label in text:
            return label
    return "unknown"


@torch.no_grad()
def predict_labels(model, tokenizer, prompts, batch_size=16):
    """Generate a short answer for each prompt and parse the predicted label."""
    preds = []
    model.eval()
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        enc = tokenizer(batch, return_tensors="pt", padding=True,
                        truncation=True, max_length=config.MAX_SEQ_LEN).to(model.device)
        out = model.generate(
            **enc,
            max_new_tokens=5,            # we only need one word
            do_sample=False,             # greedy = deterministic
            pad_token_id=tokenizer.pad_token_id,
        )
        # keep only the newly generated tokens (after the prompt)
        gen = out[:, enc["input_ids"].shape[1]:]
        texts = tokenizer.batch_decode(gen, skip_special_tokens=True)
        preds.extend(parse_label(t) for t in texts)
        print(f"  predicted {min(i + batch_size, len(prompts))}/{len(prompts)}")
    return preds
