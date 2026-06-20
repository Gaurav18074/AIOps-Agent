from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict


class SiteCreate(BaseModel):
    name: str
    url: str
    check_interval_seconds: int = 60


class SiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    url: str
    check_interval_seconds: int
    enabled: bool
    created_at: datetime


class CheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    site_id: int
    status_code: int | None
    response_time_ms: float | None
    success: bool
    error: str | None
    checked_at: datetime


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    site_id: int
    severity: str
    title: str
    summary: str
    root_cause: str | None
    suggested_fix: str | None
    confidence: float | None
    status: str
    created_at: datetime
    resolved_at: datetime | None
