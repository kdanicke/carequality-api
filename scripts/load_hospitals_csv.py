from __future__ import annotations
import csv
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# allow running as script: python scripts/load_hospitals_csv.py data/hospitals.csv
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal, engine, Base
from app.models import Hospital

Base.metadata.create_all(bind=engine)

# Map multiple possible source column names -> our normalized fields
COLMAP = {
    "provider_id": ["Facility ID", "Provider ID", "Provider Id", "provider_id", "CMS Certification Number (CCN)", "CCN"],
    "name": ["Facility Name", "Hospital Name", "name"],
    "address": ["Address", "Street Address", "address"],
    "city": ["City/Town", "City", "city"],
    "county": ["County/Parish", "County", "county"],
    "state": ["State", "state"],
    "zip": ["ZIP Code", "Zip Code", "ZIP", "zip"],
    "phone": ["Telephone Number", "Phone Number", "phone"],
    "hospital_type": ["Hospital Type", "Facility Type", "hospital_type"],
    "ownership": ["Hospital Ownership", "Ownership", "ownership"],
    "overall_rating": ["Hospital overall rating", "Overall Rating", "overall_rating"],
    "emergency_services": ["Emergency Services", "emergency_services"],
    "birthing_friendly": ["Meets criteria for birthing friendly designation", "birthing_friendly"],
    "lat": ["Location", "Latitude", "lat"],  # your file doesn't include lat/lon; safe to keep
    "lon": ["Longitude", "lon"],
}

def pick(row: dict, keys: list[str]) -> str | None:
    for k in keys:
        if k in row and row[k] is not None and str(row[k]).strip() != "":
            return str(row[k]).strip()
    return None

def parse_rating(val: str | None) -> int | None:
    if not val:
        return None
    v = val.strip()
    if v.lower() in {"not available", "n/a", "na", ""}:
        return None
    try:
        i = int(float(v))
        return i if 1 <= i <= 5 else None
    except ValueError:
        return None

def parse_bool(val: str | None) -> bool | None:
    if val is None:
        return None
    v = val.strip().lower()
    if v in {"y", "yes", "true", "1"}:
        return True
    if v in {"n", "no", "false", "0"}:
        return False
    return None

def main(csv_path: str):
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    db: Session = SessionLocal()
    try:
        upserts = 0
        for row in rows:
            provider_id = pick(row, COLMAP["provider_id"])
            name = pick(row, COLMAP["name"])
            if not provider_id or not name:
                continue

            h = db.get(Hospital, provider_id) or Hospital(provider_id=provider_id, name=name)

            h.name = name
            h.address = pick(row, COLMAP["address"]) or ""
            h.city = pick(row, COLMAP["city"]) or ""
            st = pick(row, COLMAP["state"]) or ""
            h.state = st.upper()[:2]
            h.county = pick(row, COLMAP["county"]) or ""
            h.zip = pick(row, COLMAP["zip"]) or ""
            h.phone = pick(row, COLMAP["phone"]) or ""
            h.hospital_type = pick(row, COLMAP["hospital_type"]) or ""
            h.ownership = pick(row, COLMAP["ownership"]) or ""
            h.overall_rating = parse_rating(pick(row, COLMAP["overall_rating"]))
            h.emergency_services = parse_bool(pick(row, COLMAP["emergency_services"]))
            h.birthing_friendly = parse_bool(pick(row, COLMAP["birthing_friendly"]))

            # lat/lon are optional; many CMS CSVs store combined "Location" like "(lat, lon)"
            loc = pick(row, COLMAP["lat"])
            if loc and loc.startswith("(") and "," in loc:
                try:
                    loc = loc.strip("()")
                    lat_s, lon_s = [x.strip() for x in loc.split(",", 1)]
                    h.lat = float(lat_s)
                    h.lon = float(lon_s)
                except Exception:
                    pass
            else:
                # try separate columns
                try:
                    if loc:
                        h.lat = float(loc)
                    lon = pick(row, COLMAP["lon"])
                    if lon:
                        h.lon = float(lon)
                except Exception:
                    pass

            db.merge(h)
            upserts += 1

        db.commit()
        print(f"Loaded/updated {upserts} hospitals into carequality.db")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/load_hospitals_csv.py path/to/hospitals.csv")
        sys.exit(1)
    main(sys.argv[1])