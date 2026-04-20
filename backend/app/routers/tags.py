from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[schemas.TagResponse])
async def list_tags(db: Session = Depends(get_db)):
    return db.query(models.Tag).all()

@router.post("/", response_model=schemas.TagResponse)
async def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono gestire i tag")
    
    db_tag = db.query(models.Tag).filter(models.Tag.name == tag.name).first()
    if db_tag:
        raise HTTPException(status_code=400, detail="Tag già esistente")
    
    db_tag = models.Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono gestire i tag")
    
    db_tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag non trovato")
    
    db.delete(db_tag)
    db.commit()
    return {"message": "Tag eliminato correttamente"}
