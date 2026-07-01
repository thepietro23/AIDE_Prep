# Results — Financial Sentiment QLoRA Fine-Tuning

**Base model:** Qwen2.5-0.5B-Instruct · **Method:** QLoRA (4-bit NF4 + LoRA r=16, α=32)
**Dataset:** zeroshot/twitter-financial-news-sentiment (9,543 train / 2,388 test)
**Hardware:** single 4 GB RTX 3050 laptop GPU · **Trainable params:** 8.8M / 502.8M = **1.75%**
**Eval:** 300-example held-out test sample, identical prompts for both models.

## Accuracy: 45.0% → 81.7%  (+36.7 points)

| Metric | Base model | Fine-tuned |
|--------|-----------:|-----------:|
| Accuracy        | 0.450 | **0.817** |
| Macro F1        | 0.37  | **0.81**  |
| bearish recall  | 0.55  | 0.72      |
| bullish recall  | 0.06  | **0.74**  |
| neutral recall  | 0.69  | 0.92      |

Majority-class (always "neutral") baseline ≈ 46% on this sample — the fine-tuned
model clearly beats both the base model and the trivial baseline.

Biggest gain: **bullish** detection (recall 0.06 → 0.74) — the base model almost
never identified bullish sentiment; fine-tuning fixed this.
