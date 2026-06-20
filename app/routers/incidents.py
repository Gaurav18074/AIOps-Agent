from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models import Incident
from app.schemas import IncidentOut
from app.agents.graph import run_pipeline_for_incident

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
def list_incidents(status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Incident).order_by(Incident.created_at.desc())
    if status:
        q = q.filter(Incident.status == status)
    return q.limit(100).all()


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    return inc


@router.post("/{incident_id}/replay", response_model=IncidentOut)
def replay(incident_id: int, background: BackgroundTasks, db: Session = Depends(get_db)):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    background.add_task(run_pipeline_for_incident, incident_id)
    return inc


@router.post("/{incident_id}/resolve", response_model=IncidentOut)
def resolve(incident_id: int, db: Session = Depends(get_db)):
    from datetime import datetime
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    inc.status = "resolved"
    inc.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(inc)
    return inc
