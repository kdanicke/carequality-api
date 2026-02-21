from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HospitalOut(BaseModel):
    provider_id: str
    name: str
    address: str = ""
    city: str = ""
    county: str = ""
    state: str = ""
    zip: str = ""
    phone: str = ""
    hospital_type: str = ""
    ownership: str = ""
    overall_rating: int | None = None
    emergency_services: bool | None = None
    birthing_friendly: bool | None = None
    lat: float | None = None
    lon: float | None = None

    class Config:
        from_attributes = True


class ListResponse(BaseModel, Generic[T]):
    items: List[T]
    limit: int = Field(ge=1, le=200)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class RatingStatsOut(BaseModel):
    state: str | None = None
    total_hospitals: int
    avg_rating: float | None = None
    rating_counts: dict[str, int]  # keys "1".."5" + "null"