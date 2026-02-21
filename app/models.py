from __future__ import annotations
from sqlalchemy import String, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    provider_id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(256), index=True)

    address: Mapped[str] = mapped_column(String(256), default="")
    city: Mapped[str] = mapped_column(String(128), index=True, default="")
    county: Mapped[str] = mapped_column(String(128), index=True, default="")
    state: Mapped[str] = mapped_column(String(2), index=True, default="")
    zip: Mapped[str] = mapped_column(String(16), index=True, default="")
    phone: Mapped[str] = mapped_column(String(32), default="")

    hospital_type: Mapped[str] = mapped_column(String(128), index=True, default="")
    ownership: Mapped[str] = mapped_column(String(128), index=True, default="")

    overall_rating: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    emergency_services: Mapped[bool | None] = mapped_column(Boolean, nullable=True, index=True)

    birthing_friendly: Mapped[bool | None] = mapped_column(Boolean, nullable=True, index=True)

    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)