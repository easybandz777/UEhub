"""
Inventory service implementation.
"""

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from .models import InventoryItem, InventoryEvent
from .schemas import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryListResponse,
    InventoryMovementRequest,
    InventoryAdjustmentRequest,
    BarcodeSearchResponse,
    InventoryStats
)


class InventoryService:
    """Inventory service for managing inventory items and events."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_items(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None,
        location: Optional[str] = None,
        low_stock_only: bool = False,
        out_of_stock_only: bool = False
    ) -> InventoryListResponse:
        """List inventory items with filtering and pagination."""
        
        # Build query
        query = select(InventoryItem)
        
        # Apply filters
        conditions = []
        
        if search:
            search_term = f"%{search}%"
            conditions.append(
                or_(
                    InventoryItem.name.ilike(search_term),
                    InventoryItem.sku.ilike(search_term),
                    InventoryItem.location.ilike(search_term),
                    InventoryItem.barcode.ilike(search_term)
                )
            )
        
        if location:
            conditions.append(InventoryItem.location.ilike(f"%{location}%"))
        
        if low_stock_only:
            conditions.append(InventoryItem.qty <= InventoryItem.min_qty)
        
        if out_of_stock_only:
            conditions.append(InventoryItem.qty == 0)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        query = query.order_by(InventoryItem.name)
        
        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        # Convert to response models
        item_responses = [
            InventoryItemResponse(
                id=str(item.id),
                sku=item.sku,
                name=item.name,
                location=item.location,
                barcode=item.barcode,
                qty=item.qty,
                min_qty=item.min_qty,
                is_low_stock=item.qty <= item.min_qty,
                updated_at=item.updated_at
            )
            for item in items
        ]
        
        # Get stats
        stats = await self.get_stats()
        
        return InventoryListResponse(
            items=item_responses,
            total=total,
            page=page,
            per_page=per_page,
            pages=(total + per_page - 1) // per_page,
            stats=stats
        )
    
    async def get_stats(self) -> InventoryStats:
        """Get inventory statistics."""
        
        # Total items
        total_items_result = await self.db.execute(
            select(func.count(InventoryItem.id))
        )
        total_items = total_items_result.scalar() or 0
        
        # Low stock count
        low_stock_result = await self.db.execute(
            select(func.count(InventoryItem.id)).where(
                and_(
                    InventoryItem.qty <= InventoryItem.min_qty,
                    InventoryItem.qty > 0
                )
            )
        )
        low_stock_count = low_stock_result.scalar() or 0
        
        # Out of stock count
        out_of_stock_result = await self.db.execute(
            select(func.count(InventoryItem.id)).where(InventoryItem.qty == 0)
        )
        out_of_stock_count = out_of_stock_result.scalar() or 0
        
        # Recent movements (last 7 days)
        seven_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_movements_result = await self.db.execute(
            select(func.count(InventoryEvent.id)).where(
                InventoryEvent.created_at >= seven_days_ago
            )
        )
        recent_movements = recent_movements_result.scalar() or 0
        
        return InventoryStats(
            total_items=total_items,
            total_value=0.0,  # We'll add pricing later
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            recent_movements=recent_movements
        )
    
    async def get_item(self, item_id: UUID) -> Optional[InventoryItemResponse]:
        """Get a specific inventory item."""
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            return None
        
        return InventoryItemResponse(
            id=str(item.id),
            sku=item.sku,
            name=item.name,
            location=item.location,
            barcode=item.barcode,
            qty=item.qty,
            min_qty=item.min_qty,
            is_low_stock=item.qty <= item.min_qty,
            updated_at=item.updated_at
        )
    
    async def create_item(self, item_data: InventoryItemCreate, actor_id: UUID) -> InventoryItemResponse:
        """Create a new inventory item."""
        
        # Create the item
        item = InventoryItem(
            id=uuid4(),
            sku=item_data.sku,
            name=item_data.name,
            location=item_data.location,
            barcode=item_data.barcode,
            qty=item_data.qty,
            min_qty=item_data.min_qty,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(item)
        
        # Create initial inventory event
        if item_data.qty > 0:
            event = InventoryEvent(
                id=uuid4(),
                item_id=item.id,
                actor_id=actor_id,
                delta=item_data.qty,
                reason="Initial inventory",
                meta_json={},
                created_at=datetime.utcnow()
            )
            self.db.add(event)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return InventoryItemResponse(
            id=str(item.id),
            sku=item.sku,
            name=item.name,
            location=item.location,
            barcode=item.barcode,
            qty=item.qty,
            min_qty=item.min_qty,
            is_low_stock=item.qty <= item.min_qty,
            updated_at=item.updated_at
        )
    
    async def update_item(self, item_id: UUID, item_data: InventoryItemUpdate, actor_id: UUID) -> Optional[InventoryItemResponse]:
        """Update an inventory item."""
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            return None
        
        # Update fields
        update_data = item_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        item.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return InventoryItemResponse(
            id=str(item.id),
            sku=item.sku,
            name=item.name,
            location=item.location,
            barcode=item.barcode,
            qty=item.qty,
            min_qty=item.min_qty,
            is_low_stock=item.qty <= item.min_qty,
            updated_at=item.updated_at
        )
    
    async def delete_item(self, item_id: UUID, actor_id: UUID) -> bool:
        """Delete an inventory item."""
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.commit()
        
        return True
    
    async def adjust_quantity(self, item_id: UUID, adjustment: InventoryAdjustmentRequest, actor_id: UUID) -> Optional[InventoryItemResponse]:
        """Adjust inventory quantity to a specific amount."""
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            return None
        
        old_qty = item.qty
        item.qty = adjustment.qty
        item.updated_at = datetime.utcnow()
        
        # Create event for the adjustment
        delta = adjustment.qty - old_qty
        if delta != 0:
            event = InventoryEvent(
                id=uuid4(),
                item_id=item.id,
                actor_id=actor_id,
                delta=delta,
                reason=adjustment.reason,
                meta_json=adjustment.meta,
                created_at=datetime.utcnow()
            )
            self.db.add(event)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return InventoryItemResponse(
            id=str(item.id),
            sku=item.sku,
            name=item.name,
            location=item.location,
            barcode=item.barcode,
            qty=item.qty,
            min_qty=item.min_qty,
            is_low_stock=item.qty <= item.min_qty,
            updated_at=item.updated_at
        )
    
    async def move_quantity(self, item_id: UUID, movement: InventoryMovementRequest, actor_id: UUID) -> Optional[InventoryItemResponse]:
        """Move inventory (add or remove quantity)."""
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            return None
        
        # Update quantity
        new_qty = max(0, item.qty + movement.delta)  # Don't allow negative quantities
        item.qty = new_qty
        item.updated_at = datetime.utcnow()
        
        # Create event
        event = InventoryEvent(
            id=uuid4(),
            item_id=item.id,
            actor_id=actor_id,
            delta=movement.delta,
            reason=movement.reason,
            meta_json=movement.meta,
            created_at=datetime.utcnow()
        )
        self.db.add(event)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return InventoryItemResponse(
            id=str(item.id),
            sku=item.sku,
            name=item.name,
            location=item.location,
            barcode=item.barcode,
            qty=item.qty,
            min_qty=item.min_qty,
            is_low_stock=item.qty <= item.min_qty,
            updated_at=item.updated_at
        )
    
    async def search_by_barcode(self, barcode: str) -> BarcodeSearchResponse:
        """Search for an inventory item by barcode."""
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.barcode == barcode)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            return BarcodeSearchResponse(item=None, found=False)
        
        item_response = InventoryItemResponse(
            id=str(item.id),
            sku=item.sku,
            name=item.name,
            location=item.location,
            barcode=item.barcode,
            qty=item.qty,
            min_qty=item.min_qty,
            is_low_stock=item.qty <= item.min_qty,
            updated_at=item.updated_at
        )
        
        return BarcodeSearchResponse(item=item_response, found=True)
