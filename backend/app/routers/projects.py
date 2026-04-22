from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_active_user
from ..core.audit import log_action

router = APIRouter()

@router.get("/", response_model=List[schemas.ProjectResponse])
async def read_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
        return db.query(models.Project).all()
    
    # Client only sees projects of their associated Client entity
    if not current_user.client_id:
        return []
        
    return db.query(models.Project).filter(models.Project.client_id == current_user.client_id).all()

@router.post("/", response_model=schemas.ProjectResponse)
async def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    log_action(db, current_user.id, current_user.username, "CREATE", "PROJECT", db_project.id, f"Project: {db_project.name}")
    
    return db_project

@router.get("/{project_id}")
async def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Check permission
    if current_user.role == models.UserRole.CLIENT and db_project.client_id != current_user.client_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # INTERNAL / ADMIN view (all fields)
    if current_user.role in [models.UserRole.ADMIN, models.UserRole.INTERNAL]:
        return schemas.ProjectWithItemsInternal.model_validate(db_project)
    
    # CLIENT view (limited fields & NO private items)
    public_items = [i for i in db_project.items if not i.is_private]
    return schemas.ProjectWithItemsPublic(
        id=db_project.id,
        name=db_project.name,
        description=db_project.description,
        client_id=db_project.client_id,
        created_at=db_project.created_at,
        items_count=len(public_items),
        items=public_items
    )
