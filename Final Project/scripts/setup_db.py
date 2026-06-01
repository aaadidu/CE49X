from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect


REQUIRED_TABLES = [
    "firms_detections",
    "news_articles",
    "thermal_events",
    "event_matches",
]


def get_engine(force_postgres: bool = False):
    load_dotenv()
    db_url = os.getenv("DATABASE_URL", "postgresql://ce49x@localhost:5432/conflict_monitoring")
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"Using database: {db_url}")
        return engine
    except Exception:
        if force_postgres:
            raise RuntimeError(
                "PostgreSQL connection failed while --force-postgres is enabled. "
                "Start Docker PostgreSQL container and retry."
            )
        sqlite_path = Path("Final Project/data/conflict_monitoring.db")
        sqlite_url = f"sqlite:///{sqlite_path.as_posix()}"
        print("PostgreSQL connection failed, falling back to SQLite:", sqlite_url)
        return create_engine(sqlite_url)


def ensure_empty_tables(engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS thermal_events (
                    event_id TEXT PRIMARY KEY,
                    region TEXT,
                    centroid_lat DOUBLE PRECISION,
                    centroid_lon DOUBLE PRECISION,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    duration_days INTEGER,
                    total_frp DOUBLE PRECISION,
                    max_brightness DOUBLE PRECISION,
                    detection_count INTEGER,
                    daynight_ratio DOUBLE PRECISION
                );
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS event_matches (
                    event_id TEXT,
                    article_url TEXT,
                    region TEXT,
                    date_delta_days INTEGER,
                    matched BOOLEAN,
                    PRIMARY KEY (event_id, article_url)
                );
                """
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Load FIRMS/news CSVs into PostgreSQL and verify required tables.")
    parser.add_argument("--firms", required=True, help="Path to cleaned FIRMS CSV")
    parser.add_argument("--news", required=True, help="Path to cleaned news CSV")
    parser.add_argument("--force-postgres", action="store_true", help="Fail if PostgreSQL is unavailable")
    args = parser.parse_args()

    engine = get_engine(force_postgres=args.force_postgres)

    df_firms = pd.read_csv(args.firms)
    df_news = pd.read_csv(args.news)

    df_firms.to_sql("firms_detections", engine, if_exists="replace", index=False)
    df_news.to_sql("news_articles", engine, if_exists="replace", index=False)

    ensure_empty_tables(engine)

    inspector = inspect(engine)
    existing = set(inspector.get_table_names())

    print("Existing tables:")
    for t in sorted(existing):
        print(f" - {t}")

    missing = [t for t in REQUIRED_TABLES if t not in existing]
    if missing:
        print("Missing required tables:", missing)
    else:
        print("All required tables exist.")


if __name__ == "__main__":
    main()
