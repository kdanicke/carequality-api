from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from ...db import get_db
from ...models import Hospital

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/states")
def list_states(db: Session = Depends(get_db)):
    # DISTINCT state, excluding blanks
    stmt = (
        select(Hospital.state)
        .where(Hospital.state.is_not(None))
        .where(func.length(Hospital.state) > 0)
        .distinct()
        .order_by(Hospital.state)
    )
    states = [row[0] for row in db.execute(stmt).all()]
    return {"items": states, "total": len(states)}


@router.get("/counties")
def list_counties(
    state: str | None = Query(None, description="2-letter state code, e.g. MN"),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Hospital.county)
        .where(Hospital.county.is_not(None))
        .where(func.length(Hospital.county) > 0)
    )
    if state:
        stmt = stmt.where(Hospital.state == state.upper())

    stmt = stmt.distinct().order_by(Hospital.county)
    counties = [row[0] for row in db.execute(stmt).all()]
    return {"items": counties, "total": len(counties), "state": state.upper() if state else None}


@router.get("/cities")
def list_cities(
    state: str | None = Query(None, description="2-letter state code, e.g. MN"),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Hospital.city)
        .where(Hospital.city.is_not(None))
        .where(func.length(Hospital.city) > 0)
    )
    if state:
        stmt = stmt.where(Hospital.state == state.upper())

    stmt = stmt.distinct().order_by(Hospital.city)
    cities = [row[0] for row in db.execute(stmt).all()]
    return {"items": cities, "total": len(cities), "state": state.upper() if state else None}


@router.get("/hospital-types")
def list_hospital_types(db: Session = Depends(get_db)):
    stmt = (
        select(Hospital.hospital_type)
        .where(Hospital.hospital_type.is_not(None))
        .where(func.length(Hospital.hospital_type) > 0)
        .distinct()
        .order_by(Hospital.hospital_type)
    )
    types_ = [row[0] for row in db.execute(stmt).all()]
    return {"items": types_, "total": len(types_)}


@router.get("/ownerships")
def list_ownerships(db: Session = Depends(get_db)):
    stmt = (
        select(Hospital.ownership)
        .where(Hospital.ownership.is_not(None))
        .where(func.length(Hospital.ownership) > 0)
        .distinct()
        .order_by(Hospital.ownership)
    )
    ownerships = [row[0] for row in db.execute(stmt).all()]
    return {"items": ownerships, "total": len(ownerships)}