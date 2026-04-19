from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Union
from ..database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.ItemInternal)
async def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Only Internal/Admin can create items
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{item_id}")
async def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if client has access to this project
    db_project = db.query(models.Project).filter(models.Project.id == db_item.project_id).first()
    if current_user.role == models.UserRole.CLIENT and db_project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if current_user.role in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
        return schemas.ItemInternal.model_validate(db_item)
    
    return schemas.ItemPublic.model_validate(db_item)

@router.patch("/{item_id}")
async def update_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Roles logic: 
    # - ADMIN/INTERNAL can change everything.
    # - CLIENT can only change status (if we allow it) or add comments (not yet implemented).
    # For now, let's limit updates to internal users.
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
        # Exception: Maybe client can set status to "DONE" or similar?
        # For now, let's keep it strict.
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item
