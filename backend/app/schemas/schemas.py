from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from ..models.models import UserRole, ItemStatus, ItemPriority

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
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

class ItemCreate(ItemBase):
    project_id: int
    internal_notes: Optional[str] = None
    estimated_hours: Optional[float] = None
    internal_priority: ItemPriority = ItemPriority.MEDIUM

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ItemStatus] = None
    internal_notes: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    internal_priority: Optional[ItemPriority] = None

# Public view for Client
class ItemPublic(ItemBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Full view for Internal/Admin
class ItemInternal(ItemPublic):
    internal_notes: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    internal_priority: ItemPriority
    model_config = ConfigDict(from_attributes=True)

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    client_id: int

class ProjectResponse(ProjectBase):
    id: int
    client_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProjectWithItemsPublic(ProjectResponse):
    items: List[ItemPublic]

class ProjectWithItemsInternal(ProjectResponse):
    items: List[ItemInternal]
