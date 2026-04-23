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

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


def search_listings(api_key: str, search_engine_id: str) -> List[Dict]:
    all_results = []
    seen_urls = set()

    for town in TOWNS:
        query = f'3 4 bedroom house for sale {town} NJ 750000 900000'
        results = _google_search(api_key, search_engine_id, query, town)
        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)

    return all_results


def _google_search(api_key: str, search_engine_id: str, query: str, town: str) -> List[Dict]:
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "num": 10,
    }

    try:
        response = requests.get(GOOGLE_SEARCH_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            url = item.get("link", "")
            if any(site in url for site in REAL_ESTATE_SITES):
                results.append({
                    "town": town,
                    "title": item.get("title", ""),
                    "url": url,
                    "snippet": item.get("snippet", ""),
                })

        return results

    except Exception as e:
        print(f"Search error for {town}: {e}")
        return []
