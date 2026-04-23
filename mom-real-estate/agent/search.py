import requests
from typing import List, Dict

TOWNS = [
    "Whippany",
    "Cedar Knolls",
    "Morristown",
    "Morris Township",
    "Morris Plains",
    "East Hanover",
    "Florham Park",
]

REAL_ESTATE_SITES = [
    "zillow.com",
    "redfin.com",
    "realtor.com",
    "coldwellbanker.com",
    "compass.com",
    "trulia.com",
    "kw.com",
    "sothebysrealty.com",
]

BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"


def search_listings(api_key: str) -> List[Dict]:
    all_results = []
    seen_urls = set()

    for town in TOWNS:
        query = f'3 4 bedroom house for sale {town} NJ 750000 900000'
        results = _brave_search(api_key, query, town)
        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)

    return all_results


def _brave_search(api_key: str, query: str, town: str) -> List[Dict]:
    headers = {
        "X-Subscription-Token": api_key,
        "Accept": "application/json",
    }
    params = {"q": query, "count": 10}

    try:
        response = requests.get(BRAVE_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("web", {}).get("results", []):
            url = item.get("url", "")
            if any(site in url for site in REAL_ESTATE_SITES):
                results.append({
                    "town": town,
                    "title": item.get("title", ""),
                    "url": url,
                    "snippet": item.get("description", ""),
                })

        return results

    except Exception as e:
        print(f"Search error for {town}: {e}")
        return []
