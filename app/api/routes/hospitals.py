from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...db import get_db
from ... import repository
from ...schemas import HospitalOut, ListResponse, ErrorResponse, RatingStatsOut

router = APIRouter(prefix="/hospitals", tags=["hospitals"])

@router.get("", response_model=ListResponse[HospitalOut])
def list_hospitals(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None, min_length=2, description="Free-text search on hospital name or city"),
    state: str | None = None,
    city: str | None = None,
    county: str | None = None,
    ownership: str | None = None,
    hospital_type: str | None = None,
    emergency_services: bool | None = None,
    birthing_friendly: str | None = Query(None, pattern="^(yes|unknown)$"),
    min_rating: int | None = Query(None, ge=1, le=5),
    sort: str = Query("name", pattern="^(name|state|city|overall_rating)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    items, total = repository.list_hospitals(
        db=db,
        limit=limit,
        offset=offset,
        q=q,
        state=state,
        city=city,
        county=county,
        ownership=ownership,
        hospital_type=hospital_type,
        emergency_services=emergency_services,
        birthing_friendly=birthing_friendly,
        min_rating=min_rating,
        sort=sort,
        order=order,
    )
    return {"items": items, "limit": limit, "offset": offset, "total": total}


from fastapi import HTTPException

@router.get("/{provider_id}", response_model=HospitalOut, responses={404: {"model": ErrorResponse}})
def get_hospital(provider_id: str, db: Session = Depends(get_db)):
    h = repository.get_hospital(db, provider_id)
    if not h:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": f"Hospital {provider_id} not found"}},
        )
    return h

stats_router = APIRouter(prefix="/stats", tags=["stats"])

@stats_router.get("/ratings", response_model=RatingStatsOut)
def ratings(state: str | None = None, db: Session = Depends(get_db)):
    total, avg, counts = repository.rating_stats(db, state=state)
    return {
        "state": state.upper() if state else None,
        "total_hospitals": total,
        "avg_rating": avg,
        "rating_counts": counts,
    }