from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge multiple news CSV sources into one cleaned dataset.")
    parser.add_argument("--gdelt", default="Final Project/data/news_articles.csv")
    parser.add_argument("--rss", default="Final Project/data/news_articles_google_rss.csv")
    parser.add_argument("--out", default="Final Project/data/news_articles_merged.csv")
    parser.add_argument("--target", type=int, default=1200)
    args = parser.parse_args()

    frames = []
    for path in [args.gdelt, args.rss]:
        p = Path(path)
        if p.exists():
            df = pd.read_csv(p)
            if not df.empty:
                frames.append(df)

    if not frames:
        pd.DataFrame().to_csv(args.out, index=False)
        print("No source files found with records.")
        return

    merged = pd.concat(frames, ignore_index=True)
    merged["publication_date"] = pd.to_datetime(merged["publication_date"], errors="coerce", utc=True)
    merged = merged.dropna(subset=["title", "url", "publication_date", "region"])
    merged = merged.drop_duplicates(subset=["url"])

    # Keep a balanced-ish set across regions by sorting newest first then trimming.
    merged = merged.sort_values("publication_date", ascending=False)
    if len(merged) > args.target:
        merged = merged.head(args.target)

    merged.to_csv(args.out, index=False)
    print(f"Saved merged news: {len(merged)} rows -> {args.out}")
    print("Rows by collector:")
    if "collector" in merged.columns:
        print(merged["collector"].value_counts())
    print("Rows by region:")
    print(merged["region"].value_counts())


if __name__ == "__main__":
    main()
