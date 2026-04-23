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

SERPER_URL = "https://google.serper.dev/search"


def search_listings(api_key: str) -> List[Dict]:
    all_results = []
    seen_urls = set()

    for town in TOWNS:
        query = f'3 4 bedroom house for sale {town} NJ 750000 900000'
        results = _serper_search(api_key, query, town)
        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)

    return all_results


def _serper_search(api_key: str, query: str, town: str) -> List[Dict]:
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": 10}

    try:
        response = requests.post(SERPER_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("organic", []):
            link = item.get("link", "")
            if any(site in link for site in REAL_ESTATE_SITES):
                results.append({
                    "town": town,
                    "title": item.get("title", ""),
                    "url": link,
                    "snippet": item.get("snippet", ""),
                })

        return results

    except Exception as e:
        print(f"Search error for {town}: {e}")
        return []
