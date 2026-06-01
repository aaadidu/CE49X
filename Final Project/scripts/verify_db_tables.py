from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text


def main() -> None:
    load_dotenv()
    db_url = os.getenv("DATABASE_URL", "postgresql://ce49x@localhost:5432/conflict_monitoring")
    engine = create_engine(db_url)

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    required = {"firms_detections", "news_articles", "thermal_events", "event_matches"}

    print("Available tables:")
    for t in sorted(tables):
        print(f" - {t}")

    missing = sorted(required - tables)
    if missing:
        print("Missing required tables:", missing)
    else:
        print("All required tables exist.")


if __name__ == "__main__":
    main()
