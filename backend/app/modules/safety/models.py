"""
OSHA Safety Checklist models.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...core.db import Base


class SafetyChecklist(Base):
    """Safety checklist model."""
    
    __tablename__ = "safety_checklists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Project Information
    project_name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    inspector_id = Column(String, ForeignKey("auth_user.id"), nullable=False)
    inspection_date = Column(DateTime, nullable=False)
    scaffold_type = Column(String(100), nullable=False)
    height = Column(String(50), nullable=False)
    contractor = Column(String(200), nullable=True)
    permit_number = Column(String(100), nullable=True)
    
    # Status and metadata
    status = Column(String(20), nullable=False, default="draft")  # draft, completed, approved
    total_items = Column(Integer, nullable=False, default=0)
    passed_items = Column(Integer, nullable=False, default=0)
    failed_items = Column(Integer, nullable=False, default=0)
    na_items = Column(Integer, nullable=False, default=0)
    critical_failures = Column(Integer, nullable=False, default=0)
    
    # Approval workflow
    approved_by_id = Column(String, ForeignKey("auth_user.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    inspector = relationship("User", foreign_keys=[inspector_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    checklist_items = relationship("SafetyChecklistItem", back_populates="checklist", cascade="all, delete-orphan")


class SafetyChecklistItem(Base):
    """Safety checklist item model."""
    
    __tablename__ = "safety_checklist_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    checklist_id = Column(UUID(as_uuid=True), ForeignKey("safety_checklists.id"), nullable=False)
    
    # Item identification
    item_id = Column(String(10), nullable=False)  # e.g., "1.1", "2.3"
    category = Column(String(100), nullable=False)
    number = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)
    is_critical = Column(Boolean, nullable=False, default=False)
    
    # Inspection results
    status = Column(String(10), nullable=True)  # pass, fail, na, null for pending
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    checklist = relationship("SafetyChecklist", back_populates="checklist_items")


class SafetyTemplate(Base):
    """Safety checklist template model."""
    
    __tablename__ = "safety_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), nullable=False, default="1.0")
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Template data (JSON structure of checklist items)
    template_data = Column(JSON, nullable=False)
    
    # Metadata
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    created_by = relationship("User", back_populates="created_templates")


# Add relationships to User model (this would be added to the User model in auth module)
# We'll need to update the User model to include these relationships:
# inspected_checklists = relationship("SafetyChecklist", foreign_keys="SafetyChecklist.inspector_id", back_populates="inspector")
# approved_checklists = relationship("SafetyChecklist", foreign_keys="SafetyChecklist.approved_by_id", back_populates="approved_by")
# created_templates = relationship("SafetyTemplate", back_populates="created_by")