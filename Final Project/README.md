# CE49X Final Project

Conflict Situation Monitoring for Maritime Shipping:
Correlating Satellite Thermal Anomalies with War-Related Events

## Project Structure

- `notebooks/Final_Project_Analysis.ipynb`: main notebook (single end-to-end deliverable)
- `scripts/collect_firms.py`: NASA FIRMS collection script (requires MAP key)
- `scripts/collect_news_gdelt.py`: conflict news collection from GDELT API
- `scripts/collect_news_google_rss.py`: conflict news collection from Google News RSS
- `scripts/merge_news_sources.py`: merge and deduplicate multi-source news data
- `scripts/setup_db.py`: PostgreSQL table setup and write/read helpers
- `data/`: local CSV artifacts (raw/processed exports)
- `dashboard.png`: final multi-panel dashboard (to be generated from notebook)

## Environment Setup

Install dependencies:

```bash
pip install -r "Final Project/requirements.txt"
```

## Database (Docker + PostgreSQL)

Start local PostgreSQL container:

```bash
docker run --name ce49x-postgres ^
  -e POSTGRES_USER=ce49x ^
  -e POSTGRES_HOST_AUTH_METHOD=trust ^
  -e POSTGRES_DB=conflict_monitoring ^
  -p 5432:5432 ^
  -d postgres:16
```

Check container:

```bash
docker ps
```

If Docker is installed, you can also use:

```bash
docker compose -f "Final Project/docker-compose.yml" up -d
```

## Environment Variables

Create a local `.env` (do not commit secrets):

```env
FIRMS_MAP_KEY=YOUR_FIRMS_KEY
DATABASE_URL=postgresql://ce49x@localhost:5432/conflict_monitoring
```

## Data Collection

1) Collect FIRMS detections (6+ months, 5000+ points total):

```bash
python "Final Project/scripts/collect_firms.py" --start 2025-01-01 --end 2025-06-30 --source VIIRS_SNPP_SP
```

2) Collect conflict news from GDELT:

```bash
python "Final Project/scripts/collect_news_gdelt.py" --start 2025-01-01 --end 2025-06-30 --target 1200
```

3) Collect conflict news from Google RSS (2nd source):

```bash
python "Final Project/scripts/collect_news_google_rss.py" --start 2025-01-01 --end 2025-06-30 --target 1200
```

4) Merge sources:

```bash
python "Final Project/scripts/merge_news_sources.py" --target 1400
```

5) Initialize database tables and load CSVs (strict PostgreSQL mode):

```bash
python "Final Project/scripts/setup_db.py" --firms "Final Project/data/firms_detections.csv" --news "Final Project/data/news_articles_merged.csv" --force-postgres
```

6) Verify required tables:

```bash
python "Final Project/scripts/verify_db_tables.py"
```

## Reproducibility Checklist

- [ ] Notebook runs top-to-bottom without errors
- [ ] FIRMS data period >= 6 months
- [ ] FIRMS detections >= 5000 records
- [ ] News articles >= 1000 records from at least 2 sources
- [ ] Required tables exist in PostgreSQL:
  - `firms_detections`
  - `news_articles`
  - `thermal_events`
  - `event_matches`
- [ ] Dashboard exported as `dashboard.png` at 300 DPI
- [ ] All data sources cited with URL + access date in notebook
