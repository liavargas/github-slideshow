import os
import sys
from dotenv import load_dotenv

from .search import search_listings
from .analyzer import analyze_listings
from .email_report import send_report


def run() -> None:
    load_dotenv()

    google_api_key = os.environ.get("GOOGLE_API_KEY")
    search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    sender = os.environ.get("SENDER_EMAIL")
    recipient = os.environ.get("RECIPIENT_EMAIL", "liabrielle@gmail.com")

    missing = [
        name for name, val in [
            ("GOOGLE_API_KEY", google_api_key),
            ("GOOGLE_SEARCH_ENGINE_ID", search_engine_id),
            ("ANTHROPIC_API_KEY", anthropic_key),
            ("GMAIL_APP_PASSWORD", gmail_app_password),
            ("SENDER_EMAIL", sender),
        ] if not val
    ]
    if missing:
        print(f"Error: missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    print("Searching for listings across 7 towns...")
    raw = search_listings(google_api_key, search_engine_id)
    print(f"Found {len(raw)} raw results (deduplicated)")

    print("Analyzing with Claude...")
    listings = analyze_listings(anthropic_key, raw)
    print(f"Identified {len(listings)} matching listings")

    print(f"Sending report to {recipient}...")
    send_report(gmail_app_password, recipient, sender, listings)
    print("Done.")
