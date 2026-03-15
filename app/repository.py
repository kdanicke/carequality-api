from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, asc, desc
from .models import Hospital


ALLOWED_SORT_FIELDS = {
    "name": Hospital.name,
    "state": Hospital.state,
    "city": Hospital.city,
    "overall_rating": Hospital.overall_rating,
}


def list_hospitals(
    db: Session,
    limit: int,
    offset: int,
    q: str | None = None,
    state: str | None = None,
    city: str | None = None,
    county: str | None = None,
    ownership: str | None = None,
    hospital_type: str | None = None,
    emergency_services: bool | None = None,
    birthing_friendly: str | None = None,
    min_rating: int | None = None,
    sort: str = "name",
    order: str = "asc",
):

    stmt = select(Hospital)
    count_stmt = select(func.count()).select_from(Hospital)

    filters = []
    if q:
        pattern = f"%{q}%"
        filters.append(
            or_(
                Hospital.name.ilike(pattern),
                Hospital.city.ilike(pattern),
            )
        )
    if state:
        filters.append(Hospital.state == state.upper())
    if city:
        filters.append(Hospital.city.ilike(city))
    if county:
        filters.append(Hospital.county.ilike(county))
    if ownership:
        filters.append(Hospital.ownership.ilike(ownership))
    if hospital_type:
        filters.append(Hospital.hospital_type.ilike(hospital_type))
    if emergency_services is not None:
        filters.append(Hospital.emergency_services == emergency_services)
    if birthing_friendly == "yes":
        filters.append(Hospital.birthing_friendly.is_(True))
    elif birthing_friendly == "unknown":
        filters.append(Hospital.birthing_friendly.is_(None))
    if min_rating is not None:
        filters.append(Hospital.overall_rating.is_not(None))
        filters.append(Hospital.overall_rating >= min_rating)

    for f in filters:
        stmt = stmt.where(f)
        count_stmt = count_stmt.where(f)

    sort_col = ALLOWED_SORT_FIELDS.get(sort, Hospital.name)
    stmt = stmt.order_by(desc(sort_col) if order.lower() == "desc" else asc(sort_col))

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    return items, total


def get_hospital(db: Session, provider_id: str) -> Hospital | None:
    return db.get(Hospital, provider_id)


def search_hospitals(db: Session, q: str, state: str | None, limit: int, offset: int):
    stmt = select(Hospital)
    count_stmt = select(func.count()).select_from(Hospital)

    # Simple "contains" search on name/city
    pattern = f"%{q}%"
    search_filter = or_(Hospital.name.ilike(pattern), Hospital.city.ilike(pattern))
    stmt = stmt.where(search_filter)
    count_stmt = count_stmt.where(search_filter)

    if state:
        st = state.upper()
        stmt = stmt.where(Hospital.state == st)
        count_stmt = count_stmt.where(Hospital.state == st)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(stmt.order_by(asc(Hospital.name)).limit(limit).offset(offset)).scalars().all()
    return items, total


def rating_stats(db: Session, state: str | None = None):
    stmt = select(Hospital.overall_rating, func.count()).group_by(Hospital.overall_rating)
    total_stmt = select(func.count()).select_from(Hospital)
    avg_stmt = select(func.avg(Hospital.overall_rating)).where(Hospital.overall_rating.is_not(None))

    if state:
        st = state.upper()
        stmt = stmt.where(Hospital.state == st)
        total_stmt = total_stmt.where(Hospital.state == st)
        avg_stmt = avg_stmt.where(Hospital.state == st)

    total = db.execute(total_stmt).scalar_one()
    avg = db.execute(avg_stmt).scalar_one()

    rows = db.execute(stmt).all()
    counts: dict[str, int] = {str(i): 0 for i in range(1, 6)}
    counts["null"] = 0
    for rating, cnt in rows:
        if rating is None:
            counts["null"] += cnt
        else:
            counts[str(int(rating))] = cnt

    return total, (float(avg) if avg is not None else None), counts