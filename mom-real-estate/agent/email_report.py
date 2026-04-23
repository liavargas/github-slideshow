import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
from typing import List, Dict

STARS = {5: "★★★★★", 4: "★★★★☆", 3: "★★★☆☆", 2: "★★☆☆☆", 1: "★☆☆☆☆"}
GREEN = "#2c5f2e"


def send_report(gmail_app_password: str, recipient: str, sender: str, listings: List[Dict]) -> None:
    today = date.today().strftime("%B %d, %Y")
    subject = f"Daily Home Report — Morris County NJ — {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(_build_text(today, listings), "plain"))
    msg.attach(MIMEText(_build_html(today, listings), "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, gmail_app_password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Email sent to {recipient}")


def _build_html(today: str, listings: List[Dict]) -> str:
    top_count = sum(1 for l in listings if l.get("score", 0) >= 4)

    by_town: Dict[str, List[Dict]] = {}
    for l in listings:
        by_town.setdefault(l.get("town", "Unknown"), []).append(l)

    cards = ""
    for town in sorted(by_town):
        cards += f"""
        <h2 style="color:{GREEN};border-bottom:2px solid {GREEN};padding-bottom:6px;margin-top:32px">{town}</h2>
        """
        for l in by_town[town]:
            score = l.get("score", 0)
            stars = STARS.get(score, "")
            road_badge = (
                '<span style="background:#c0392b;color:white;font-size:11px;'
                'padding:2px 7px;border-radius:4px;margin-left:8px">&#9888; Main road</span>'
                if l.get("main_road_flag") else ""
            )
            tax_row = (
                f'<div style="color:#c0392b;font-size:13px;margin-top:4px">'
                f'&#127991; {l["tax_note"]}</div>'
                if l.get("tax_note") else ""
            )
            notes_row = (
                f'<div style="font-size:13px;color:#666;margin-top:6px">{l["notes"]}</div>'
                if l.get("notes") else ""
            )
            cards += f"""
            <div style="background:#f9f9f9;border:1px solid #ddd;border-radius:8px;
                        padding:18px;margin:12px 0">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <strong style="font-size:16px">{l.get("address", "Address unknown")}</strong>
                  {road_badge}
                  <div style="color:#888;font-size:13px;margin-top:2px">{l.get("town","")}</div>
                </div>
                <div style="font-size:24px;color:#f5a623;white-space:nowrap">{stars}</div>
              </div>
              <div style="display:flex;gap:20px;margin:10px 0;font-size:15px">
                <span>&#128176; <strong>{l.get("price","Unknown")}</strong></span>
                <span>&#128716; {l.get("beds","?")} bed</span>
                <span>&#128704; {l.get("baths","?")} bath</span>
              </div>
              {tax_row}
              <div style="margin-top:8px;font-size:13px;color:#555">
                {l.get("score_reason","")}
              </div>
              {notes_row}
              <a href="{l.get("url","#")}"
                 style="display:inline-block;margin-top:14px;padding:9px 18px;
                        background:{GREEN};color:white;text-decoration:none;
                        border-radius:5px;font-size:13px;font-weight:bold">
                View Listing &rarr;
              </a>
            </div>
            """

    if not listings:
        cards = '<p style="color:#888">No new listings found today. Check back tomorrow!</p>'

    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;
                 padding:20px;color:#333;background:#fff">

      <div style="background:{GREEN};color:white;padding:24px 28px;border-radius:10px;
                  margin-bottom:24px">
        <h1 style="margin:0;font-size:26px">&#127968; Daily Home Report</h1>
        <p style="margin:6px 0 0;opacity:0.85;font-size:14px">{today} &middot; Morris County, NJ</p>
      </div>

      <div style="background:#eaf4ea;border:1px solid #c3dfc3;border-radius:8px;
                  padding:14px 18px;margin-bottom:8px;font-size:14px">
        <strong>Today:</strong> {len(listings)} listing{"s" if len(listings) != 1 else ""} found
        &middot; <strong>{top_count}</strong> high-match (4&ndash;5 stars)
        <div style="margin-top:6px;color:#555;font-size:12px">
          Criteria: 3&ndash;4 bed &middot; 2&ndash;3 bath &middot; $750K&ndash;$900K
          &middot; Open floor plan &middot; Not on main road &middot; Lower taxes
        </div>
      </div>

      {cards}

      <div style="margin-top:36px;padding-top:14px;border-top:1px solid #eee;
                  font-size:11px;color:#aaa;line-height:1.6">
        This report runs automatically every morning. Listings sourced from Zillow, Redfin,
        and realtor.com via Google Search. Scores are AI estimates &mdash; always verify details
        on the listing page before scheduling a showing.
      </div>
    </body>
    </html>
    """


def _build_text(today: str, listings: List[Dict]) -> str:
    lines = [f"Daily Home Report — Morris County NJ — {today}", "=" * 52, ""]
    if not listings:
        lines.append("No listings found today. Check back tomorrow!")
        return "\n".join(lines)

    for l in listings:
        road = " [MAIN ROAD WARNING]" if l.get("main_road_flag") else ""
        lines += [
            f"{l.get('address','Unknown')} — {l.get('town','')}{road}",
            f"Price: {l.get('price','Unknown')} | "
            f"{l.get('beds','?')} bed / {l.get('baths','?')} bath | "
            f"Score: {l.get('score',0)}/5",
            f"{l.get('score_reason','')}",
            f"URL: {l.get('url','')}",
            "",
        ]
    return "\n".join(lines)
