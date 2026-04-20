from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Union
from ..database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_active_user
from ..core.audit import log_action

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
    
    tag_ids = item.tag_ids
    db_item = models.Item(**item.model_dump(exclude={"tag_ids"}))
    if tag_ids:
        db_item.tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all()
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    log_action(db, current_user.id, current_user.username, "CREATE", "ITEM", db_item.id, f"Item: {db_item.title}")
    
    # Se unique_id non è impostato, lo popoliamo con l'ID incrementale
    if not db_item.unique_id:
        db_item.unique_id = str(db_item.id)
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
    if current_user.role == models.UserRole.CLIENT:
        if db_project.client_id != current_user.id or db_item.is_private:
            raise HTTPException(status_code=403, detail="Non autorizzato")

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
        
        # CLIENT can only update status, description and new fields (except ID) - FILTER the rest
        update_data = item_update.model_dump(exclude_unset=True)
        allowed_client_fields = [
            "status", "description", "tag_ids", "hlr", "srs", "tp", "external_id"
        ]
        update_data = {k: v for k, v in update_data.items() if k in allowed_client_fields}
    
    elif current_user.role not in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    else:
        # ADMIN / INTERNAL can update everything in the schema except ID
        update_data = item_update.model_dump(exclude_unset=True)
        if "unique_id" in update_data:
            del update_data["unique_id"]

    # Handle tag updates separately
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            db_item.tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all()

    # Perform update
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    
    log_action(db, current_user.id, current_user.username, "UPDATE", "ITEM", db_item.id, f"Updated: {db_item.title}")
    
    return db_item

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item non trovato")
    
    item_title = db_item.title
    db.delete(db_item)
    db.commit()
    
    log_action(db, current_user.id, current_user.username, "DELETE", "ITEM", item_id, f"Deleted: {item_title}")
    
    return {"message": "Item eliminato correttamente"}
