# Budget tiers — match the build to the wallet, not to hype

Inspired by tiered build guides (like Logical Increments): instead of one "best" answer,
give the right answer for each budget. The goal is REALISTIC and REASONABLE, never
"buy the most expensive thing".

All prices are approximate full-system (GPU + CPU + RAM + PSU + board + storage + case),
USD, 2026. Treat as ballparks; the live price fetch refines individual parts.

## Tier 1 — Entry / Learning ($700-1000)
- GPU: RTX 3060 12GB (or used 3060)
- CPU: Ryzen 5 7600 · RAM: 32GB DDR5 · PSU: 750W
- Can do: 7B LLMs in 4-bit, Stable Diffusion, learning RAG/fine-tuning basics, general use + gaming.
- Who: students, first AI box, "I want to learn without burning money".

## Tier 2 — Value sweet spot ($1100-1500)  ⭐ best bang-for-buck
- GPU: **used RTX 3090 24GB** (the value king) or new RTX 4060 Ti 16GB
- CPU: Ryzen 7 7700X · RAM: 32-64GB DDR5 · PSU: 750W (3090 needs the full 750W)
- Can do: 13B FP16, 34B in 4-bit, QLoRA fine-tuning, fast Stable Diffusion.
- Who: serious hobbyist / indie dev / real side projects. Most people should stop here.

## Tier 3 — High end ($2000-3500)
- GPU: RTX 4090 24GB (speed) or RTX 5090 32GB (VRAM + newest)
- CPU: Ryzen 9 7950X · RAM: 64GB DDR5 · PSU: 1000W
- Can do: fast fine-tuning, small training runs, heavy Stable Diffusion/video, pro workloads.
- Who: professionals, startups prototyping, content creators.

## Tier 4 — Don't buy, RENT (enterprise)
- Need H100 / A100 / B200 (80GB+)? Buying = $25k-40k PER CARD plus a server.
- For 99% of projects this is the WRONG move. Rent by the hour instead (see local_vs_cloud).
- Buy only if you have constant, year-round, multi-GPU demand.

## The reasonableness rule

If a recommendation pushes you a tier above what your stated workload needs, that is a
red flag. More VRAM than your model needs is wasted money. The best build is the
CHEAPEST one that comfortably fits your actual workload + a little headroom.
