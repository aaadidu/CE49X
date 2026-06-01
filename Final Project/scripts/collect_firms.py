from __future__ import annotations

import argparse
import io
import os
from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv


@dataclass(frozen=True)
class Region:
    name: str
    bbox: str  # west,south,east,north


REGIONS = [
    Region("Black_Sea_Ukraine", "26.0,44.0,41.0,52.5"),
    Region("Levant_EastMed", "32.0,30.0,38.5,37.8"),
    Region("Red_Sea_Gulf_Aden", "36.0,11.0,48.0,24.0"),
    Region("Persian_Gulf", "46.0,22.0,57.5,31.0"),
]


def chunk_5_days(start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
    windows: list[tuple[datetime, datetime]] = []
    current = start
    while current <= end:
        window_end = min(current + timedelta(days=4), end)
        windows.append((current, window_end))
        current = window_end + timedelta(days=1)
    return windows


def fetch_chunk(map_key: str, source: str, region: Region, chunk_end: datetime, days: int) -> pd.DataFrame:
    # FIRMS area endpoint format:
    # /api/area/csv/{MAP_KEY}/{SOURCE}/{WEST,SOUTH,EAST,NORTH}/{DAYS}/{YYYY-MM-DD}
    url = (
        "https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        f"{map_key}/{source}/{region.bbox}/{days}/{chunk_end:%Y-%m-%d}"
    )
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    if not resp.text.strip():
        return pd.DataFrame()

    # Sometimes FIRMS may return a message line instead of CSV table.
    if "latitude" not in resp.text.lower():
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(resp.text))
    if df.empty:
        return df
    df["region"] = region.name
    return df


def clean_firms(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    out["acq_date"] = pd.to_datetime(out["acq_date"], errors="coerce")
    out["acq_time"] = out["acq_time"].astype(str).str.zfill(4)

    # Keep moderate/high confidence only (string or numeric variants).
    if "confidence" in out.columns:
        conf_raw = out["confidence"].astype(str).str.strip().str.lower()
        conf_num = pd.to_numeric(out["confidence"], errors="coerce")
        keep_text = conf_raw.isin(["nominal", "high", "n", "h"])
        keep_num = conf_num >= 50
        out = out[keep_text | keep_num]

    numeric_cols = ["latitude", "longitude", "brightness", "frp"]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.dropna(subset=["latitude", "longitude", "acq_date"])
    out = out.drop_duplicates()
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect NASA FIRMS detections by region and date range.")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--source", default="VIIRS_SNPP_SP", help="FIRMS source code")
    parser.add_argument(
        "--out",
        default="Final Project/data/firms_detections.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    load_dotenv()
    map_key = os.getenv("FIRMS_MAP_KEY")
    if not map_key:
        raise RuntimeError("FIRMS_MAP_KEY is missing. Put it in environment or .env file.")

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")
    windows = chunk_5_days(start, end)

    frames: list[pd.DataFrame] = []
    for region in REGIONS:
        print(f"Collecting {region.name} ...")
        for w_start, w_end in windows:
            days = (w_end - w_start).days + 1
            try:
                df_chunk = fetch_chunk(map_key, args.source, region, w_end, days)
                if not df_chunk.empty:
                    frames.append(df_chunk)
                print(f"  {w_start:%Y-%m-%d} -> {w_end:%Y-%m-%d}: {len(df_chunk)} rows")
            except Exception as exc:
                print(f"  failed {w_start:%Y-%m-%d} -> {w_end:%Y-%m-%d}: {exc}")

    if not frames:
        print("No records fetched.")
        pd.DataFrame().to_csv(args.out, index=False)
        return

    df_all = pd.concat(frames, ignore_index=True)
    before = len(df_all)
    df_clean = clean_firms(df_all)
    after = len(df_clean)
    df_clean.to_csv(args.out, index=False)

    print(f"Saved: {args.out}")
    print(f"Records before cleaning: {before}")
    print(f"Records after cleaning:  {after}")
    print(df_clean.head())


if __name__ == "__main__":
    main()
