"""
Inventory module database models.
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from ...core.db import Base


class InventoryItem(Base):
    """Inventory item model."""
    
    __tablename__ = "inventory_items"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    location = Column(String(100), nullable=False, index=True)
    barcode = Column(String(50), nullable=True, index=True)
    qty = Column(Integer, nullable=False, default=0)
    min_qty = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = relationship("InventoryEvent", back_populates="item", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InventoryItem(id={self.id}, sku='{self.sku}', name='{self.name}')>"


class InventoryEvent(Base):
    """Inventory event model for tracking changes."""
    
    __tablename__ = "inventory_events"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    item_id = Column(PostgresUUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False, index=True)
    actor_id = Column(String, nullable=True, index=True)  # Remove FK constraint for now
    delta = Column(Integer, nullable=False)  # Positive for add, negative for remove
    reason = Column(String(200), nullable=False)
    meta_json = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    item = relationship("InventoryItem", back_populates="events")
    # actor = relationship("User")  # Commented out for now
    
    def __repr__(self):
        return f"<InventoryEvent(id={self.id}, item_id={self.item_id}, delta={self.delta})>"
