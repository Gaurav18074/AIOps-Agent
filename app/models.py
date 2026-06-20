from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    check_interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    checks: Mapped[list["Check"]] = relationship(back_populates="site", cascade="all, delete-orphan")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="site", cascade="all, delete-orphan")


class Check(Base):
    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    site: Mapped["Site"] = relationship(back_populates="checks")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="warning")  # info, warning, critical
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, acknowledged, resolved
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    site: Mapped["Site"] = relationship(back_populates="incidents")
