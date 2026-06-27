# Compatibility & "will it actually work" rules

Inspired by PCPartPicker's compatibility checks. A recommendation is useless if the parts
don't physically work together. These are the rules the advisor must respect.

## Power supply (PSU) sizing
- Rule: PSU wattage >= 1.5x the sum of GPU TDP + CPU TDP (headroom for spikes + the rest).
- A single GPU up to ~350W (e.g. RTX 3090 @ 350W) + a mid CPU -> **750W** PSU minimum.
- RTX 4090 (450W) or RTX 5090 (575W) -> **1000W** PSU minimum.
- Cheaping out on the PSU causes random crashes under load. Never undersize it.

## System RAM vs GPU VRAM
- Rule of thumb: system RAM >= 2x GPU VRAM.
- 24GB GPU -> at least 48-64GB system RAM is comfortable (32GB is the floor).
- If you offload large models partly to CPU, you need even MORE system RAM.

## CPU should not bottleneck the GPU (but don't overspend)
- A single-GPU inference box is fine with a 6-8 core CPU (Ryzen 5/7).
- Heavy data preprocessing or multi-GPU rigs want 12-16 cores (Ryzen 9).
- Spending big on CPU for a pure-inference box is wasted money.

## CUDA / software reality
- NVIDIA + CUDA is the default for AI in 2026. PyTorch, TensorFlow, vLLM, bitsandbytes,
  TensorRT-LLM all target CUDA first.
- AMD (ROCm) and Apple Silicon (MPS) work for inference but have rougher tooling and less
  library support. For a smooth experience, recommend NVIDIA unless the user insists.

## Physical fit (quick checks)
- Big GPUs (4090/5090) are long + 3-slot thick: check case clearance.
- High-TDP builds need good airflow/cooling, not just a big PSU.

## The compatibility checklist the advisor should output
1. PSU watts >= 1.5 x (GPU TDP + CPU TDP)?
2. System RAM >= 2x GPU VRAM (and >= 32GB)?
3. CPU core count matched to workload (not under, not wastefully over)?
4. NVIDIA/CUDA unless the user explicitly wants AMD/Apple?
5. Does the chosen GPU's VRAM actually fit the user's target model? (see vram_requirements)
