"""
price_fetch.py
--------------
The "live price" layer. This is what fixes the core complaint: LLMs quote
outdated / unrealistic prices because their training data is frozen in time.

Strategy (best-effort with a safety net):
  1. Each catalog item has a SEED price (from data/hardware_catalog.json) and a
     price_source URL.
  2. If ENABLE_LIVE_PRICES is on, we try to fetch the current price from that URL.
  3. On ANY failure (blocked, timeout, HTML changed, no price found), we KEEP the
     seed price and just mark it stale. The app never crashes over a price.

HONEST NOTE (important engineering reality):
  Big retailers (Amazon, Newegg, PCPartPicker) actively block scrapers and change
  their HTML often, and scraping may violate their terms. So this generic scraper is
  deliberately "best-effort". In a real product you'd use an OFFICIAL API
  (Amazon Product Advertising API) or a paid price-tracking API (e.g. Keepa).
  The seed catalog is the reliable backbone; live fetch is the bonus refresh.
"""

import re
import json
import requests

import config

# Pretend to be a normal browser; many sites reject the default python-requests UA.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Match a price like $1,299.00  or  $699
_USD_RE = re.compile(r"\$\s?([0-9][0-9,]{1,6}(?:\.[0-9]{2})?)")


def load_catalog():
    """Read the structured catalog JSON. Returns the parsed dict."""
    with open(config.CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_price_usd(html):
    """Pull the first plausible USD price out of a page's HTML.
    Returns a float or None. (Naive on purpose; see HONEST NOTE above.)"""
    matches = _USD_RE.findall(html)
    for raw in matches:
        value = float(raw.replace(",", ""))
        if 50 <= value <= 100000:      # ignore junk like "$1" or "$0.00"
            return value
    return None


def fetch_live_price_usd(url):
    """Best-effort: GET the URL and try to read a current USD price.
    Returns a float on success, or None on any failure (never raises)."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=config.PRICE_FETCH_TIMEOUT)
        resp.raise_for_status()
        return _extract_price_usd(resp.text)
    except Exception:
        return None   # blocked, timeout, network error, HTML changed -> give up quietly


def _iter_priced_items(catalog):
    """Yield every catalog item that has a price (across all category lists)."""
    for key, items in catalog.items():
        if key.startswith("_"):          # skip "_meta"
            continue
        for item in items:
            yield item


def refresh_catalog(catalog, verbose=True):
    """Walk the catalog and refresh prices in place.

    For each item:
      - if live prices are enabled AND a live price is found -> use it, mark live
      - otherwise -> keep the seed price, mark it stale
    Returns the same catalog dict (mutated)."""
    live_on = config.ENABLE_LIVE_PRICES
    updated, kept = 0, 0

    for item in _iter_priced_items(catalog):
        # Cloud GPUs are priced per hour, not a one-off buy -> skip scraping them.
        if "price_usd" not in item:
            item["price_live"] = False
            continue

        new_price = fetch_live_price_usd(item["price_source"]) if live_on else None

        if new_price is not None:
            item["price_usd"] = round(new_price, 2)
            item["price_inr"] = round(new_price * config.USD_TO_INR)
            item["price_live"] = True
            item["price_updated"] = "live"
            updated += 1
            if verbose:
                print(f"  [live] {item['name']:<34} -> ${new_price:,.0f}")
        else:
            item["price_live"] = False           # using the seed/fallback price
            kept += 1
            if verbose and live_on:
                print(f"  [seed] {item['name']:<34} -> ${item['price_usd']:,.0f} (live fetch failed)")

    if verbose:
        mode = "LIVE" if live_on else "SEED-ONLY (ENABLE_LIVE_PRICES=false)"
        print(f"\nPrice refresh [{mode}]: {updated} live, {kept} from seed.")
    return catalog


if __name__ == "__main__":
    cat = load_catalog()
    print(f"Loaded catalog. Live prices enabled: {config.ENABLE_LIVE_PRICES}\n")
    refresh_catalog(cat)
