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
    # Check project ownership for CLIENT
    if current_user.role == models.UserRole.CLIENT:
        db_project = db.query(models.Project).filter(models.Project.id == item.project_id).first()
        if not db_project or db_project.client_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to create items for this project")
    
    elif current_user.role not in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
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

    # Check ownership for CLIENT
    if current_user.role == models.UserRole.CLIENT:
        db_project = db.query(models.Project).filter(models.Project.id == db_item.project_id).first()
        if not db_project or db_project.client_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # CLIENT can only update status and description - FILTER the rest
        update_data = item_update.model_dump(exclude_unset=True)
        update_data = {k: v for k, v in update_data.items() if k in ["status", "description"]}
    
    elif current_user.role not in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    else:
        # ADMIN / INTERNAL can update everything in the schema
        update_data = item_update.model_dump(exclude_unset=True)

    # Perform update
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item
