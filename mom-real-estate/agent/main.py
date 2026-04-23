import os
import sys
from dotenv import load_dotenv

from .search import search_listings
from .analyzer import analyze_listings
from .email_report import send_report


def run() -> None:
    load_dotenv()

    serper_key = os.environ.get("SERPER_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    sendgrid_key = os.environ.get("SENDGRID_API_KEY")
    recipient = os.environ.get("RECIPIENT_EMAIL", "liabrielle@gmail.com")
    sender = os.environ.get("SENDER_EMAIL")

    missing = [
        name for name, val in [
            ("SERPER_API_KEY", serper_key),
            ("ANTHROPIC_API_KEY", anthropic_key),
            ("SENDGRID_API_KEY", sendgrid_key),
            ("SENDER_EMAIL", sender),
        ] if not val
    ]
    if missing:
        print(f"Error: missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    print("Searching for listings across 7 towns...")
    raw = search_listings(serper_key)
    print(f"Found {len(raw)} raw results (deduplicated)")

    print("Analyzing with Claude...")
    listings = analyze_listings(anthropic_key, raw)
    print(f"Identified {len(listings)} matching listings")

    print(f"Sending report to {recipient}...")
    send_report(sendgrid_key, recipient, sender, listings)
    print("Done.")
