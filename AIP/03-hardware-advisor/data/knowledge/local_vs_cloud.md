# Local (buy) vs Cloud (rent) — the break-even math

The most money-saving decision. Don't buy a GPU you'll use 2 hours a week, and don't
rent for 10 hours a day if you'll do it for a year. Decide with numbers.

## The simple break-even formula

    break_even_hours = price_to_buy_card / cloud_price_per_hour

Then:

    hours_you_will_actually_use_per_month  ->  hours over the card's ~2-3 year life
    if total_lifetime_hours > break_even_hours  ->  BUYING is cheaper
    else                                        ->  RENTING is cheaper

### Worked example
- Used RTX 3090: ~$700 to buy.
- Cloud RTX 4090-class: ~$0.69/hour.
- Break-even = 700 / 0.69 ≈ **1015 hours**.
- If you'll use the GPU more than ~1000 hours total (e.g. 1 hr/day for ~3 years, or a
  few heavy months), BUYING wins. For occasional bursts, RENT.

(Buying also adds electricity + the rest of the PC; renting adds data egress + setup time.
Keep it simple: use the formula as the first filter, then adjust.)

## When CLOUD clearly wins
- You need an 80GB+ GPU (H100/A100/B200) — buying is $25k-40k; rent at ~$1.6-3/hr.
- Spiky workload: a few big training runs, then nothing for weeks.
- You want the newest GPU without committing capital.
- You're just learning / prototyping.

## When LOCAL (buying) clearly wins
- Steady daily use (inference service, constant experiments).
- Privacy/data can't leave your machine.
- You hate per-hour billing anxiety and want a fixed cost.
- A 12-24GB consumer card covers your models (most hobby/indie cases).

## Cloud cost-control tips
- Use community/spot pricing, checkpoint often, and TEAR DOWN the instance the moment a
  run finishes. Idle cloud GPUs are where money silently dies.

## Takeaway
Small/occasional -> rent. Steady + fits a consumer card -> buy. Need 80GB+ -> rent
unless you're literally running a data center.
