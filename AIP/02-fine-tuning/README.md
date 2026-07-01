# 📈 Financial Sentiment LLM — QLoRA Fine-Tuning

Fine-tune a small instruction-tuned LLM to classify the sentiment of financial
news & tweets as **bullish / bearish / neutral** — using **QLoRA**, trained
end-to-end on a single **4 GB consumer laptop GPU** (RTX 3050).

> **Result: accuracy 45.0% → 81.7%** (+36.7 points) by training only **1.75%**
> of the model's parameters. Full numbers in [`RESULTS.md`](RESULTS.md).

---

## Why this project

Financial news/tweet sentiment is a real signal in quantitative finance
(news → trading signals). A general small LLM is bad at it out of the box
(45% accuracy, and it almost never spots *bullish*). Fine-tuning teaches it
the task cheaply — without retraining the whole model.

**RAG vs fine-tuning:** RAG injects *knowledge* from outside; fine-tuning
bakes a *skill/behaviour* into the weights. Sentiment classification is a
skill → fine-tuning is the right tool (this pairs with the RAG project in
`../01-rag`).

---

## What is QLoRA (the method here)

```
  Base model (502M params)  ──load in 4-bit──►  frozen, tiny memory   (the "Q")
            +
  LoRA adapters (8.8M params = 1.75%)  ──train only these──►          (the "LoRA")
```

- **Q (quantization):** load the base model in 4-bit (NF4) via bitsandbytes → fits 4 GB.
- **LoRA:** add small adapter matrices and train only those → ~1.75% of params, a 35 MB adapter.

---

## Files

| File | Responsibility |
|------|----------------|
| `config.py`       | All settings (model path, dataset, labels, prompt, LoRA + training hyperparams) |
| `prepare_data.py` | Load the dataset and format each row as an instruction example (pure Python, no pyarrow `.map`) |
| `infer.py`        | Shared prediction helper (generate a label, parse it) — used by baseline & evaluate |
| `baseline.py`     | Accuracy of the **base** model (the "before" number) |
| `train.py`        | **QLoRA** fine-tuning → saves a LoRA adapter |
| `evaluate.py`     | Accuracy of the **fine-tuned** model (the "after" number) |
| `RESULTS.md`      | Measured before/after metrics |

## Results

| Metric | Base | Fine-tuned |
|--------|-----:|-----------:|
| Accuracy | 45.0% | **81.7%** |
| Macro F1 | 0.37 | **0.81** |
| bullish recall | 0.06 | **0.74** |

Base model: `Qwen2.5-0.5B-Instruct` · Dataset: `zeroshot/twitter-financial-news-sentiment`
(9,543 train / 2,388 test) · evaluated on a 300-example held-out sample with identical prompts.

---

## Setup

```bash
pip install -r requirements.txt
# torch with CUDA (match your driver; this project used cu124):
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

The base model is loaded from a local folder (`models/Qwen2.5-0.5B-Instruct/`).
Download it once with curl (config + tokenizer + weights), e.g.:

```bash
BASE=https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main
for f in config.json generation_config.json tokenizer.json tokenizer_config.json vocab.json merges.txt model.safetensors; do
  curl -L "$BASE/$f" -o "models/Qwen2.5-0.5B-Instruct/$f"
done
```

## Usage

```bash
python baseline.py    # measure the base model (before)
python train.py       # QLoRA fine-tune -> saves lora_adapter/
python evaluate.py    # measure the fine-tuned model (after)
```

---

## Key concepts demonstrated

- **QLoRA**: 4-bit quantization + LoRA adapters → fine-tune a 0.5B model on 4 GB VRAM.
- **Parameter-efficient training**: only 1.75% of params trained; a portable 35 MB adapter.
- **Honest evaluation**: identical prompts for base vs fine-tuned, per-class precision/recall, and awareness of class imbalance (majority-class baseline ≈ 46%).
- **Instruction-style SFT**: format each example as `instruction + text → label`.

## Engineering notes (real issues solved)

- **Corporate TLS proxy** blocked HuggingFace's Xet downloader → downloaded the
  model weights with `curl` (OS cert store) instead, and pointed the code at a
  local model folder.
- **Windows pyarrow + torch crash**: calling `datasets.map()` after torch is
  imported segfaults (exit 139). Fixed by formatting data in plain Python and
  building the dataset **before** importing torch (see `prepare_data.py` /
  `train.py`), plus `KMP_DUPLICATE_LIB_OK` and `HF_HUB_OFFLINE` in `config.py`.

## Possible improvements

- Try a larger base model (Qwen2.5-1.5B-Instruct) now that the pipeline works.
- Train for more epochs / tune LoRA rank; add a validation-loss early stop.
- Completion-only loss (mask the prompt tokens) for cleaner SFT.
- Combine with the RAG project: a fine-tuned sentiment model inside a finance assistant.
