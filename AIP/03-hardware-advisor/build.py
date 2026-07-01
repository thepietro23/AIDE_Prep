"""
build.py
--------
Full-PC-build assembler (the PCPartPicker-style feature).

Given a budget + workload, it picks a COMPLETE, COMPATIBLE build:
    GPU + CPU + motherboard + RAM + PSU + storage
respecting the rules from data/knowledge/compatibility_rules.md:
    - PSU watts  >= 1.5 x (GPU TDP + CPU TDP)
    - system RAM >= 2 x GPU VRAM (and >= 32GB)
    - motherboard socket must match the CPU socket
    - GPU VRAM must fit the target model (if given)
    - stay within budget; spend most on the GPU, the rest is supporting cast.

It's a greedy assembler (GPU first, then size everything around it), which is exactly
how a human builder thinks. Returns a dict the CLI / UI can render.
"""

import config
from price_fetch import load_catalog, refresh_catalog
from retrieve import _use_case_matches   # reuse the loose use-case matcher

# Rough cost of everything EXCEPT the GPU (cpu+mobo+ram+psu+storage), so we know how
# much of the budget to leave for the supporting parts before picking the GPU.
_SUPPORT_RESERVE_USD = 560


def _cat(catalog, name):
    """All items in a category list (e.g. 'gpus', 'cpus')."""
    return catalog.get(name, [])


def _price(item):
    return item.get("price_usd", 0) or 0


def assemble_build(budget_usd, use_case=None, model_size=None, min_vram_gb=None):
    """Return a complete compatible build within budget.

    Result: {parts: {role: item}, total_usd, total_inr, warnings: [...], notes: [...]}
    """
    catalog = refresh_catalog(load_catalog(), verbose=False)
    warnings, notes = [], []

    # ---- 1. GPU first (the heart of the build) -----------------------------
    # Consumer GPUs only (skip enterprise H100/B200 - those are rent-only).
    gpus = [g for g in _cat(catalog, "gpus") if g["tier"] != "enterprise"]

    # Leave room in the budget for the rest of the parts.
    gpu_budget = max(budget_usd - _SUPPORT_RESERVE_USD, budget_usd * 0.45)

    def gpu_ok(g):
        if _price(g) > gpu_budget:
            return False
        if min_vram_gb and g["specs"].get("vram_gb", 0) < min_vram_gb:
            return False
        return _use_case_matches(use_case, g.get("use_cases", []))

    affordable = [g for g in gpus if gpu_ok(g)]
    if not affordable:
        # Relax: ignore use-case, then ignore VRAM floor, so we still return a build.
        affordable = [g for g in gpus if _price(g) <= gpu_budget
                      and (not min_vram_gb or g["specs"].get("vram_gb", 0) >= min_vram_gb)]
    if not affordable:
        affordable = [g for g in gpus if _price(g) <= gpu_budget]
        if min_vram_gb:
            warnings.append(f"No GPU with >={min_vram_gb}GB VRAM fits the budget; "
                            f"picked the most VRAM that does. Consider renting cloud for big models.")
    if not affordable:
        return {"parts": {}, "total_usd": 0, "total_inr": 0,
                "warnings": [f"Budget ${budget_usd} is too low for any full build. "
                             f"Raise it or rent a cloud GPU."], "notes": []}

    # Best GPU = most VRAM, then cheapest at that VRAM.
    gpu = sorted(affordable, key=lambda g: (-g["specs"].get("vram_gb", 0), _price(g)))[0]
    vram = gpu["specs"].get("vram_gb", 0)
    gpu_tdp = gpu["specs"].get("tdp_w", 250)
    is_amd = gpu["specs"].get("cuda") is False
    if is_amd:
        notes.append("Chosen GPU is AMD (no CUDA) - AI library support is rougher. "
                     "Great for gaming, trickier for AI.")

    # ---- 2. CPU (don't bottleneck, don't overspend) ------------------------
    cpus = _cat(catalog, "cpus")
    heavy = use_case in ("training", "data-preprocessing") or vram >= 24
    cpu_pref_tier = "high" if heavy else ("mid" if vram >= 16 else "budget")
    cpu = (_pick_tier(cpus, cpu_pref_tier) or _cheapest(cpus))

    # ---- 3. Motherboard matching the CPU socket ----------------------------
    socket = cpu["specs"].get("socket")
    mobos = [m for m in _cat(catalog, "motherboards") if m["specs"].get("socket") == socket]
    mobo = _cheapest(mobos)
    if not mobo:
        warnings.append(f"No motherboard for socket {socket} in catalog.")

    # ---- 4. RAM >= 2x VRAM, floor 32GB -------------------------------------
    need_ram = max(32, vram * 2)
    rams = sorted(_cat(catalog, "ram"), key=lambda r: r["specs"]["capacity_gb"])
    ram = next((r for r in rams if r["specs"]["capacity_gb"] >= need_ram), rams[-1] if rams else None)

    # ---- 5. PSU >= 1.5x (GPU TDP + CPU TDP) --------------------------------
    cpu_tdp = cpu["specs"].get("tdp_w", 105)
    need_watts = (gpu_tdp + cpu_tdp) * 1.5
    psus = sorted(_cat(catalog, "psu"), key=lambda p: p["specs"]["watts"])
    psu = next((p for p in psus if p["specs"]["watts"] >= need_watts), psus[-1] if psus else None)
    if psu and psu["specs"]["watts"] < need_watts:
        warnings.append(f"Even the biggest catalog PSU ({psu['specs']['watts']}W) is below the "
                        f"recommended {need_watts:.0f}W. Add a bigger PSU.")

    # ---- 6. Storage (2TB if AI-heavy and budget allows, else 1TB) ----------
    storages = sorted(_cat(catalog, "storage"), key=_price)
    storage = storages[-1] if (heavy or vram >= 24) else storages[0]

    # ---- 7. Total + budget fit --------------------------------------------
    parts = {"GPU": gpu, "CPU": cpu, "Motherboard": mobo, "RAM": ram, "PSU": psu, "Storage": storage}
    parts = {k: v for k, v in parts.items() if v}
    total = sum(_price(v) for v in parts.values())

    # If over budget, trim the cheapest-impact parts (storage -> RAM -> CPU).
    if total > budget_usd:
        if storage and storage is storages[-1] and len(storages) > 1:
            parts["Storage"] = storages[0]; total = sum(_price(v) for v in parts.values())
        if total > budget_usd and ram and ram["specs"]["capacity_gb"] > need_ram and len(rams) > 1:
            parts["RAM"] = rams[0]; total = sum(_price(v) for v in parts.values())
        if total > budget_usd:
            warnings.append(f"Full build (${total:,}) is ${total - budget_usd:,} over budget. "
                            f"Drop to a cheaper GPU or raise the budget.")

    return {
        "parts": parts,
        "total_usd": total,
        "total_inr": round(total * config.USD_TO_INR),
        "psu_required_watts": round(need_watts),
        "ram_required_gb": need_ram,
        "warnings": warnings,
        "notes": notes,
    }


def _pick_tier(items, tier):
    """Cheapest item of a given tier (or None)."""
    same = [i for i in items if i.get("tier") == tier]
    return _cheapest(same)


def _cheapest(items):
    return sorted(items, key=_price)[0] if items else None


def format_build(build):
    """Pretty multi-line string for the CLI."""
    if not build["parts"]:
        return "No build possible.\n" + "\n".join("  ! " + w for w in build["warnings"])
    lines = ["FULL PC BUILD", "-" * 60]
    for role, item in build["parts"].items():
        p = item.get("price_usd", 0)
        tag = "live" if item.get("price_live") else "seed"
        lines.append(f"  {role:<12} {item['name']:<34} ${p:>6,} (~Rs {item.get('price_inr', 0):,}) [{tag}]")
    lines.append("-" * 60)
    lines.append(f"  {'TOTAL':<12} {'':<34} ${build['total_usd']:>6,} (~Rs {build['total_inr']:,})")
    lines.append(f"\n  PSU sized for >= {build['psu_required_watts']}W | RAM >= {build['ram_required_gb']}GB")
    for n in build["notes"]:
        lines.append(f"  note: {n}")
    for w in build["warnings"]:
        lines.append(f"  !  {w}")
    return "\n".join(lines)


if __name__ == "__main__":
    from recommend import min_vram_for_model
    for budget, uc, ms in [(1200, "fine-tuning", "13B"), (800, "ai-inference", "7B"), (2500, "training", "13B")]:
        print(f"\n### budget=${budget}, use={uc}, model={ms} ###")
        b = assemble_build(budget, use_case=uc, model_size=ms, min_vram_gb=min_vram_for_model(ms))
        print(format_build(b))
