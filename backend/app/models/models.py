from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float, Boolean, Text, Table
from sqlalchemy.orm import relationship
from ..database import Base
import enum
from datetime import datetime

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    INTERNAL = "INTERNAL"
    CLIENT = "CLIENT"

class ItemStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CLOSED = "CLOSED"

class ItemPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    reference_client = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    projects = relationship("Project", back_populates="client")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("User", back_populates="projects")
    items = relationship("Item", back_populates="project", cascade="all, delete-orphan")

    @property
    def items_count(self):
        return len(self.items)

# Association table for Many-to-Many relationship between Items and Tags
item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String, default="#3b82f6") # Default blue

    items = relationship("Item", secondary=item_tags, back_populates="tags")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.OPEN)
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Internal fields
    internal_notes = Column(Text, nullable=True)
    internal_priority = Column(Enum(ItemPriority), default=ItemPriority.MEDIUM)

    # Requirements & IDs
    is_private = Column(Boolean, default=False)
    hlr = Column(Text, nullable=True)
    srs = Column(Text, nullable=True)
    tp = Column(Text, nullable=True)
    external_id = Column(String, nullable=True)
    unique_id = Column(String, nullable=True)

    project = relationship("Project", back_populates="items")
    tags = relationship("Tag", secondary=item_tags, back_populates="items")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String) # Cache username
    action = Column(String) # CREATE, UPDATE, DELETE, etc.
    entity_type = Column(String) # USER, PROJECT, ITEM, TAG, DB
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)

    user = relationship("User")
