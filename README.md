# CareQuality API

A healthcare provider quality REST API built using FastAPI and public CMS hospital data.

This project demonstrates backend API design, dataset ingestion, filtering/search patterns, metadata discovery endpoints, and automated testing.

---

## Features

- RESTful resource-based API design
- Filtering, pagination, and sorting
- Free-text search (`q` parameter)
- Metadata discovery endpoints (`/meta`)
- Aggregation endpoints (`/stats`)
- SQLite persistence
- SQLAlchemy ORM
- Automated tests (pytest)
- Auto-generated OpenAPI documentation (Swagger)

---

## Dataset

This project uses the **CMS Hospital General Information** dataset from:

https://data.cms.gov/provider-data/

The dataset is:
- Public
- Non-sensitive
- Provider-level (not patient data)

The API ingests the CSV and normalizes key hospital attributes including:
- Provider ID
- Name
- Location (State, County, City)
- Ownership
- Hospital Type
- Emergency Services
- Birthing Friendly designation
- Overall Quality Rating

---

## What This Project Demonstrates

- Designing resource-based APIs
- Moving search into composable query parameters (`/hospitals?q=...`)
- Handling route conflicts in FastAPI
- Data normalization during CSV ingestion
- Query filtering using SQLAlchemy
- Metadata endpoints for discoverability
- Aggregation queries
- OpenAPI documentation exposure
- Automated API testing

---

## Project Structure

- `carequality-api/`
  - `app/`
    - `main.py`
    - `db.py`
    - `models.py`
    - `schemas.py`
    - `repository.py`
    - `api/`
      - `routes/`
        - `hospitals.py`
        - `meta.py`
  - `scripts/`
    - `load_hospitals_csv.py`
  - `tests/`
    - `test_hospitals.py`
  - `requirements.txt`
  - `README.md`

---

## Setup (Windows Example)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install Dependencies

```bash
pip install -r requirements.txt
```

3. Download the CMS Hospital General Information CSV from data.cms.gov. For this example, we used Hospital General Information
https://data.cms.gov/provider-data/dataset/xubh-q36u#data-table

4. Place it inside:
>data/Hospital_General_Information.csv

5. Load into SQLite:
```bash
python scripts/load_hospitals_csv.py data/Hospital_General_Information.csv
```

This will generate:
carequality.db

6. Start the app
```bash
uvicorn app.main:app --reload
```

7. Open in your browser:

Swagger UI:
http://127.0.0.1:8000/docs

OpenAPI JSON:
http://127.0.0.1:8000/openapi.json

#### Example API Calls

Search for Mayo Clinic hospitals in Minnesota
> GET /hospitals?q=mayo&state=MN

List hospitals in Arizona
> GET /hospitals?state=AZ&limit=10

Filter by birthing friendly hospitals
> GET /hospitals?state=AL&birthing_friendly=yes

Discover available states
> GET /meta/states

Discover counties in Minnesota
> GET /meta/counties?state=MN

Get rating statistics for a state
> GET /stats/ratings?state=AZ

#### Running Tests
pytest

Tests validate:
- Health endpoint
- List endpoint response structure
- Stats endpoint response structure