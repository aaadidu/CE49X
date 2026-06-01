from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

import pandas as pd
import requests


@dataclass(frozen=True)
class RegionQuery:
    region: str
    query: str


REGION_QUERY_VARIANTS = {
    "Black_Sea_Ukraine": [
        "Ukraine OR Crimea OR Donbas war conflict missile attack",
        "Russia Ukraine conflict shelling artillery strike",
        "Black Sea military attack drone war",
    ],
    "Levant_EastMed": [
        "Gaza OR Israel OR Lebanon OR Syria war bombing airstrike attack",
        "Middle East conflict missile military operation",
        "Levant war shelling strike troops",
    ],
    "Red_Sea_Gulf_Aden": [
        "Yemen OR Red Sea OR Aden conflict military strike attack",
        "Houthi Red Sea shipping attack conflict",
        "Bab el-Mandeb military strike war",
    ],
    "Persian_Gulf": [
        "Iran OR Iraq OR Strait of Hormuz OR Persian Gulf conflict military attack",
        "Hormuz security incident military conflict",
        "Gulf region war missile attack",
    ],
}


def fetch_google_rss(query: str, limit: int = 120) -> pd.DataFrame:
    url = (
        "https://news.google.com/rss/search"
        f"?q={quote_plus(query)}"
        "&hl=en-US&gl=US&ceid=US:en"
    )
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    items = root.findall(".//item")
    rows = []
    for item in items[:limit]:
        title = item.findtext("title")
        link = item.findtext("link")
        pub = item.findtext("pubDate")
        source_elem = item.find("source")
        source = source_elem.text if source_elem is not None else "unknown"
        try:
            pub_dt = parsedate_to_datetime(pub) if pub else None
        except Exception:
            pub_dt = None
        rows.append(
            {
                "title": title,
                "publication_date": pub_dt,
                "source": source,
                "domain": "news.google.com",
                "url": link,
                "collector": "google_rss",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect conflict-related articles from Google News RSS.")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--target", type=int, default=1200, help="Target max output rows")
    parser.add_argument("--per-query", type=int, default=200, help="Max rows per RSS query")
    parser.add_argument("--strict-date", action="store_true", help="Keep only records inside start/end range")
    parser.add_argument("--out", default="Final Project/data/news_articles_google_rss.csv", help="Output CSV path")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    frames: list[pd.DataFrame] = []
    for region, queries in REGION_QUERY_VARIANTS.items():
        total_region = 0
        for q in queries:
            df = fetch_google_rss(q, limit=args.per_query)
            if df.empty:
                continue
            df["region"] = region
            frames.append(df)
            total_region += len(df)
        print(f"{region}: {total_region} raw rows")

    if not frames:
        pd.DataFrame().to_csv(args.out, index=False)
        print("No RSS records fetched.")
        return

    news = pd.concat(frames, ignore_index=True)
    news["publication_date"] = pd.to_datetime(news["publication_date"], errors="coerce", utc=True)
    news = news.dropna(subset=["title", "url", "publication_date"])
    if args.strict_date:
        news = news[(news["publication_date"] >= pd.Timestamp(start, tz="UTC")) & (news["publication_date"] <= pd.Timestamp(end, tz="UTC"))]
    news = news.drop_duplicates(subset=["url"])
    news["location_mention"] = news["region"]

    if len(news) > args.target:
        news = news.sort_values("publication_date", ascending=False).head(args.target)

    news.to_csv(args.out, index=False)
    print(f"Saved {len(news)} rows to {args.out}")


if __name__ == "__main__":
    main()
