from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_active_user
from ..core.audit import log_action

router = APIRouter()

@router.post("/items/{item_id}/notes", response_model=schemas.ItemNoteResponse)
async def create_note(
    item_id: int,
    note: schemas.ItemNoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Check if item exists
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check permissions
    if current_user.role == models.UserRole.CLIENT:
        db_project = db.query(models.Project).filter(models.Project.id == db_item.project_id).first()
        if not db_project or db_project.client_id != current_user.client_id or db_item.is_private:
            raise HTTPException(status_code=403, detail="Not authorized to add notes to this item")

    db_note = models.ItemNote(
        item_id=item_id,
        user_id=current_user.id,
        content=note.content
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    log_action(db, current_user.id, current_user.username, "CREATE", "ITEM_NOTE", db_note.id, f"Note added to item {item_id}")
    
    return db_note

@router.patch("/notes/{note_id}", response_model=schemas.ItemNoteResponse)
async def update_note(
    note_id: int,
    note_update: schemas.ItemNoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_note = db.query(models.ItemNote).filter(models.ItemNote.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    # Check permissions: user can edit their own notes, or ADMIN/INTERNAL can edit any note
    if current_user.role == models.UserRole.CLIENT:
        if db_note.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this note")
    else:
        # Internal/Admin can edit their own, maybe admin can edit all? 
        # Let's say you can only edit your own notes unless you are an ADMIN
        if db_note.user_id != current_user.id and current_user.role != models.UserRole.ADMIN:
             raise HTTPException(status_code=403, detail="Not authorized to edit this note")

    db_note.content = note_update.content
    db.commit()
    db.refresh(db_note)
    
    log_action(db, current_user.id, current_user.username, "UPDATE", "ITEM_NOTE", db_note.id, f"Note {note_id} updated")
    
    return db_note

@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_note = db.query(models.ItemNote).filter(models.ItemNote.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    # Check permissions: user can delete their own notes, or ADMIN can delete any
    if current_user.role == models.UserRole.CLIENT:
        if db_note.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this note")
    else:
        if db_note.user_id != current_user.id and current_user.role != models.UserRole.ADMIN:
             raise HTTPException(status_code=403, detail="Not authorized to delete this note")

    db.delete(db_note)
    db.commit()
    
    log_action(db, current_user.id, current_user.username, "DELETE", "ITEM_NOTE", note_id, f"Note {note_id} deleted")
    
    return {"message": "Note deleted successfully"}
