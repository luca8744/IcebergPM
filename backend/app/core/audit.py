from sqlalchemy.orm import Session
from ..models import models
from typing import Optional

def log_action(
    db: Session, 
    user_id: Optional[int], 
    username: str, 
    action: str, 
    entity_type: str, 
    entity_id: Optional[int] = None, 
    details: Optional[str] = None
):
    """
    Registra un'azione nel log di audit.
    """
    db_log = models.AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.add(db_log)
    db.commit()
