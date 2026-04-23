import anthropic
import json
from typing import List, Dict

# NJ major roads to flag as main road risks
MAIN_ROADS = [
    "route 10", "rt 10", "rte 10",
    "route 202", "rt 202", "rte 202",
    "route 24", "rt 24", "rte 24",
    "route 287", "rt 287", "rte 287",
    "route 46", "rt 46", "rte 46",
    "route 80", "rt 80", "rte 80",
    "route 206", "rt 206", "rte 206",
    "columbia tpke", "columbia turnpike",
    "parsippany rd", "speedwell ave",
    "madison ave",  # main corridor in some towns
]

SYSTEM_PROMPT = """You are a real estate assistant helping find homes for a buyer in Morris County, NJ.

Her criteria:
- Price range: $750,000 to $900,000
- Bedrooms: 3 to 4
- Bathrooms: 2 to 3
- Style: Open floor plan strongly preferred
- Location: NOT on a main road (NJ Route 10, 202, 24, 287, 46, 80, or any major arterial)
- Property taxes: Lower is better for Morris County — flag anything likely over $15,000/year
- Target towns: Whippany, Cedar Knolls, Morristown, Morris Township, Morris Plains, East Hanover, Florham Park

You will receive a list of Google search results (title, snippet, URL) from real estate sites.

For each result that appears to be an actual property listing (not a search results page, agent bio, article, or neighborhood guide):
1. Extract what you can from the title and snippet
2. Score it 1–5 based on fit with the criteria (5 = excellent match, 1 = poor match)
3. Flag if the address suggests a main road
4. Note if price, beds, or baths are outside criteria

Return ONLY a valid JSON array. No markdown, no explanation — raw JSON only.

Schema:
[
  {
    "town": "town name",
    "address": "street address or 'Unknown'",
    "price": "$XXX,XXX or 'Unknown'",
    "beds": "number or 'Unknown'",
    "baths": "number or 'Unknown'",
    "score": 1-5,
    "score_reason": "one sentence explaining the score",
    "main_road_flag": true or false,
    "tax_note": "tax info if visible, or null",
    "url": "listing URL",
    "notes": "anything else relevant, or null"
  }
]

Skip results that are clearly not individual property listings."""


def analyze_listings(api_key: str, raw_listings: List[Dict]) -> List[Dict]:
    if not raw_listings:
        return []

    client = anthropic.Anthropic(api_key=api_key)

    listings_text = json.dumps(raw_listings, indent=2)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Analyze these search results and return the JSON array:\n\n{listings_text}",
            }
        ],
    )

    raw = response.content[0].text.strip()

    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start == -1 or end == 0:
            print("No JSON array found in Claude response")
            print(f"Response was: {raw[:500]}")
            return []

        analyzed = json.loads(raw[start:end])

        # Apply local main-road cross-check on top of Claude's flag
        for listing in analyzed:
            address_lower = listing.get("address", "").lower()
            if any(road in address_lower for road in MAIN_ROADS):
                listing["main_road_flag"] = True

        analyzed.sort(key=lambda x: x.get("score", 0), reverse=True)
        return analyzed

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {raw[:500]}")
        return []
