from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models import Site
from app.schemas import SiteCreate, SiteOut

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=list[SiteOut])
def list_sites(db: Session = Depends(get_db)):
    return db.query(Site).order_by(Site.id).all()


@router.post("", response_model=SiteOut, status_code=201)
def create_site(payload: SiteCreate, db: Session = Depends(get_db)):
    site = Site(**payload.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}", status_code=204)
def delete_site(site_id: int, db: Session = Depends(get_db)):
    site = db.get(Site, site_id)
    if not site:
        raise HTTPException(404, "Site not found")
    db.delete(site)
    db.commit()
