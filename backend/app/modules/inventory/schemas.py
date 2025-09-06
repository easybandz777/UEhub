"""
Inventory module schemas.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class InventoryItemBase(BaseModel):
    """Base inventory item schema."""
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=50)
    min_qty: int = Field(0, ge=0)


class InventoryItemCreate(InventoryItemBase):
    """Inventory item creation schema."""
    qty: int = Field(0, ge=0)


class InventoryItemUpdate(BaseModel):
    """Inventory item update schema."""
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=50)
    min_qty: Optional[int] = Field(None, ge=0)


class InventoryItemResponse(InventoryItemBase):
    """Inventory item response schema."""
    id: str
    qty: int
    is_low_stock: bool
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryEventBase(BaseModel):
    """Base inventory event schema."""
    delta: int = Field(..., description="Quantity change (positive for increase, negative for decrease)")
    reason: str = Field(..., min_length=1, max_length=200)
    meta_json: Optional[Dict[str, Any]] = Field(default_factory=dict)


class InventoryEventCreate(InventoryEventBase):
    """Inventory event creation schema."""
    pass


class InventoryEventResponse(InventoryEventBase):
    """Inventory event response schema."""
    id: str
    item_id: str
    actor_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class InventoryAdjustmentRequest(BaseModel):
    """Inventory adjustment request schema."""
    qty: int = Field(..., ge=0)
    reason: str = Field(..., min_length=1, max_length=200)
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)


class InventoryMovementRequest(BaseModel):
    """Inventory movement request schema."""
    delta: int = Field(..., ne=0, description="Quantity change (positive for add, negative for remove)")
    reason: str = Field(..., min_length=1, max_length=200)
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BarcodeSearchResponse(BaseModel):
    """Barcode search response schema."""
    item: Optional[InventoryItemResponse] = None
    found: bool


class LowStockAlert(BaseModel):
    """Low stock alert schema."""
    item: InventoryItemResponse
    current_qty: int
    min_qty: int
    shortage: int


class InventoryStats(BaseModel):
    """Inventory statistics schema."""
    total_items: int
    total_value: float
    low_stock_count: int
    out_of_stock_count: int
    recent_movements: int


class InventoryListResponse(BaseModel):
    """Inventory list response schema."""
    items: list[InventoryItemResponse]
    total: int
    page: int
    per_page: int
    pages: int
    stats: Optional[InventoryStats] = None


class InventoryEventListResponse(BaseModel):
    """Inventory event list response schema."""
    items: list[InventoryEventResponse]
    total: int
    page: int
    per_page: int
    pages: int


class BulkInventoryUpdate(BaseModel):
    """Bulk inventory update schema."""
    items: list[Dict[str, Any]] = Field(..., min_items=1, max_items=100)
    reason: str = Field(..., min_length=1, max_length=200)
    
    @validator("items")
    def validate_items(cls, v):
        for item in v:
            if "id" not in item and "sku" not in item:
                raise ValueError("Each item must have either 'id' or 'sku'")
            if "qty" not in item and "delta" not in item:
                raise ValueError("Each item must have either 'qty' or 'delta'")
        return v


class BulkInventoryResponse(BaseModel):
    """Bulk inventory update response schema."""
    updated_count: int
    failed_count: int
    errors: list[str] = []
