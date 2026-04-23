from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from ..models.models import UserRole, ItemStatus, ItemPriority

# --- Tag Schemas ---
class TagBase(BaseModel):
    name: str
    color: str = "#3b82f6"

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Client Schemas ---
class ClientBase(BaseModel):
    name: str
    description: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    role: UserRole
    client_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    client: Optional[ClientResponse] = None
    model_config = ConfigDict(from_attributes=True)

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: UserRole

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

# --- Item Schemas ---
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: ItemStatus = ItemStatus.OPEN
    hlr: Optional[str] = None
    srs: Optional[str] = None
    tp: Optional[str] = None
    external_id: Optional[str] = None
    unique_id: Optional[str] = None
    rev_finding: Optional[str] = None
    rev_released: Optional[str] = None
    submodule: Optional[str] = None
    is_private: bool = False

class ItemCreate(ItemBase):
    project_id: int
    internal_notes: Optional[str] = None
    internal_priority: ItemPriority = ItemPriority.MEDIUM
    tag_ids: Optional[List[int]] = []

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ItemStatus] = None
    internal_notes: Optional[Optional[str]] = None
    internal_priority: Optional[ItemPriority] = None
    tag_ids: Optional[List[int]] = None
    hlr: Optional[str] = None
    srs: Optional[str] = None
    tp: Optional[str] = None
    external_id: Optional[str] = None
    unique_id: Optional[str] = None
    rev_finding: Optional[str] = None
    rev_released: Optional[str] = None
    submodule: Optional[str] = None
    is_private: Optional[bool] = None

# Public view for Client
class ItemPublic(ItemBase):
    id: int
    project_id: int
    internal_priority: Optional[ItemPriority] = ItemPriority.MEDIUM
    tags: List[TagResponse] = []
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# Full view for Internal/Admin
class ItemInternal(ItemPublic):
    internal_notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    client_id: int

class ProjectResponse(ProjectBase):
    id: int
    client_id: Optional[int] = None
    created_at: datetime
    items_count: int = 0
    model_config = ConfigDict(from_attributes=True)

class ProjectWithItemsPublic(ProjectResponse):
    items: List[ItemPublic]

class ProjectWithItemsInternal(ProjectResponse):
    items: List[ItemInternal]

# --- Audit Log Schemas ---
class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    user_id: Optional[int]
    username: str
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: Optional[str]
    model_config = ConfigDict(from_attributes=True)
