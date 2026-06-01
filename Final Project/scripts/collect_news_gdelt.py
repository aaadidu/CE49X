from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import time
from urllib.parse import quote_plus

import pandas as pd
import requests


@dataclass(frozen=True)
class RegionQuery:
    region: str
    query: str


REGION_QUERIES = [
    RegionQuery("Black_Sea_Ukraine", "(Ukraine OR Crimea OR Donbas) AND (war OR conflict OR missile OR attack)"),
    RegionQuery("Levant_EastMed", "(Gaza OR Israel OR Lebanon OR Syria) AND (war OR bombing OR airstrike OR attack)"),
    RegionQuery("Red_Sea_Gulf_Aden", "(Yemen OR Red Sea OR Aden) AND (conflict OR military OR strike OR attack)"),
    RegionQuery("Persian_Gulf", "(Iran OR Iraq OR Strait of Hormuz OR Persian Gulf) AND (conflict OR military OR attack)"),
]


def iter_windows(start: datetime, end: datetime, days_per_window: int = 14) -> list[tuple[datetime, datetime]]:
    out: list[tuple[datetime, datetime]] = []
    cur = start
    while cur <= end:
        win_end = min(cur + timedelta(days=days_per_window - 1), end)
        out.append((cur, win_end))
        cur = win_end + timedelta(days=1)
    return out


def fetch_gdelt(query: str, start_dt: datetime, end_dt: datetime, max_records: int = 80) -> pd.DataFrame:
    # GDELT DOC 2.0 API: no key required
    base = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = (
        f"query={quote_plus(query)}"
        f"&mode=ArtList&format=json&maxrecords={max_records}"
        f"&startdatetime={start_dt:%Y%m%d}000000"
        f"&enddatetime={end_dt:%Y%m%d}235959"
    )
    url = f"{base}?{params}"
    # Small retry policy for temporary API throttling (HTTP 429).
    for attempt in range(4):
        resp = requests.get(url, timeout=60)
        if resp.status_code == 429 and attempt < 3:
            sleep_s = (2 * (attempt + 1)) + random.uniform(0.3, 1.2)
            time.sleep(sleep_s)
            continue
        resp.raise_for_status()
        break
    payload = resp.json()
    articles = payload.get("articles", [])
    if not articles:
        return pd.DataFrame()

    rows = []
    for a in articles:
        rows.append(
            {
                "title": a.get("title"),
                "publication_date": a.get("seendate"),
                "source": a.get("sourcecountry", "unknown"),
                "domain": a.get("domain"),
                "url": a.get("url"),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect conflict-related news with GDELT API.")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--target", type=int, default=1200, help="Target record count")
    parser.add_argument("--window-days", type=int, default=14, help="Date window size in days")
    parser.add_argument("--max-per-call", type=int, default=80, help="Max records per API call")
    parser.add_argument("--regions", default="", help="Comma-separated region names to include")
    parser.add_argument("--out", default="Final Project/data/news_articles.csv", help="Output CSV path")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")
    windows = iter_windows(start, end, days_per_window=args.window_days)

    selected = REGION_QUERIES
    if args.regions.strip():
        wanted = {x.strip() for x in args.regions.split(",") if x.strip()}
        selected = [rq for rq in REGION_QUERIES if rq.region in wanted]

    frames: list[pd.DataFrame] = []
    for rq in selected:
        print(f"Collecting region: {rq.region}")
        for w_start, w_end in windows:
            try:
                df = fetch_gdelt(rq.query, w_start, w_end, max_records=args.max_per_call)
                if not df.empty:
                    df["region"] = rq.region
                    df["collector"] = "gdelt"
                    frames.append(df)
                print(f"  {w_start:%Y-%m-%d} -> {w_end:%Y-%m-%d}: {len(df)} rows")
                # Gentle pacing to reduce API throttling likelihood.
                time.sleep(0.9)
            except Exception as exc:
                print(f"  failed {w_start:%Y-%m-%d} -> {w_end:%Y-%m-%d}: {exc}")

    if not frames:
        print("No articles fetched.")
        pd.DataFrame().to_csv(args.out, index=False)
        return

    all_news = pd.concat(frames, ignore_index=True)
    all_news["publication_date"] = pd.to_datetime(all_news["publication_date"], errors="coerce")
    all_news = all_news.drop_duplicates(subset=["url"])
    all_news = all_news.dropna(subset=["title", "url", "publication_date"])

    # Ensure a location mention field exists (region label proxy).
    all_news["location_mention"] = all_news["region"]

    if len(all_news) > args.target:
        all_news = all_news.sort_values("publication_date", ascending=False).head(args.target)

    all_news.to_csv(args.out, index=False)
    print(f"Saved {len(all_news)} articles to {args.out}")
    preview = all_news.head().to_string(index=False)
    print(preview.encode("ascii", errors="ignore").decode())


if __name__ == "__main__":
    main()
