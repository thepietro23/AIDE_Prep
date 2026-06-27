# How much VRAM does an AI workload actually need?

This is the single most important question for AI hardware. VRAM (the memory ON the
GPU) decides which models you can run at all. Compute speed only decides how fast.

## Rule of thumb for Large Language Models (LLMs)

Memory needed scales with model size (parameters) and precision.

| Model size | Full precision (FP16) | 8-bit | 4-bit (QLoRA / GGUF) |
|------------|-----------------------|-------|----------------------|
| 7B         | ~14 GB                | ~8 GB | ~5-6 GB              |
| 13B        | ~26 GB                | ~14 GB| ~9-10 GB             |
| 34B        | ~68 GB                | ~36 GB| ~20 GB               |
| 70B        | ~140 GB               | ~75 GB| ~40 GB               |

Inference (just running the model) needs roughly the numbers above plus a little for
the context/KV-cache. Longer context = more memory.

## Fine-tuning needs MORE than inference

Training/fine-tuning also stores gradients and optimizer states, so full fine-tuning
can need 3-4x the inference memory. This is why almost nobody full-fine-tunes at home.

**QLoRA** is the trick that makes fine-tuning affordable: it loads the model in 4-bit
and only trains small adapter layers. A 13B model can be QLoRA-fine-tuned on a single
24GB GPU (e.g. RTX 3090/4090). A 7B QLoRA fits in ~12-16GB.

## Practical mapping (what to buy for what)

- **Learning / 7B inference in 4-bit:** 12 GB is enough (RTX 3060 12GB).
- **Comfortable 7B FP16 or 13B in 4-bit:** 16 GB (RTX 4060 Ti 16GB).
- **13B FP16, 34B in 4-bit, QLoRA fine-tuning:** 24 GB (used RTX 3090 = best value, or 4090 for speed).
- **Headroom + newest features, 32GB:** RTX 5090.
- **70B models or real training:** 80GB+ (H100/A100) — rent on the cloud, don't buy.

## Key takeaway

Pick the GPU by the VRAM your target model needs FIRST. Only then compare speed and
price. A cheaper card with enough VRAM beats an expensive card that can't fit the model.
