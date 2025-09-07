"""
OSHA Safety Checklist repository.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.security import get_password_hash
from .models import SafetyChecklist, SafetyChecklistItem, SafetyTemplate


class SafetyRepository:
    """Safety checklist repository."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Checklist operations
    async def create_checklist(self, checklist_data: dict) -> SafetyChecklist:
        """Create a new safety checklist."""
        # Extract checklist items
        items_data = checklist_data.pop("checklist_items", [])
        
        # Create checklist
        checklist = SafetyChecklist(**checklist_data)
        self.db.add(checklist)
        await self.db.flush()  # Get the ID
        
        # Create checklist items
        for item_data in items_data:
            item = SafetyChecklistItem(
                checklist_id=checklist.id,
                **item_data
            )
            self.db.add(item)
        
        await self.db.commit()
        await self.db.refresh(checklist)
        return checklist
    
    async def get_checklist(self, checklist_id: str) -> Optional[SafetyChecklist]:
        """Get a checklist by ID with items."""
        query = (
            select(SafetyChecklist)
            .options(selectinload(SafetyChecklist.checklist_items))
            .where(SafetyChecklist.id == checklist_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_checklists(
        self,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> List[SafetyChecklist]:
        """List checklists with filtering."""
        query = select(SafetyChecklist).options(selectinload(SafetyChecklist.checklist_items))
        
        # Apply user filter for employees (they can only see their own)
        if user_id:
            query = query.where(SafetyChecklist.inspector_id == user_id)
        
        # Apply filters
        if filters:
            if filters.get("status"):
                query = query.where(SafetyChecklist.status == filters["status"])
            
            if filters.get("project_name"):
                query = query.where(
                    SafetyChecklist.project_name.ilike(f"%{filters['project_name']}%")
                )
            
            if filters.get("location"):
                query = query.where(
                    SafetyChecklist.location.ilike(f"%{filters['location']}%")
                )
            
            if filters.get("inspector_id"):
                query = query.where(SafetyChecklist.inspector_id == filters["inspector_id"])
            
            if filters.get("date_from"):
                query = query.where(SafetyChecklist.inspection_date >= filters["date_from"])
            
            if filters.get("date_to"):
                query = query.where(SafetyChecklist.inspection_date <= filters["date_to"])
            
            if filters.get("critical_failures_only"):
                query = query.where(SafetyChecklist.critical_failures > 0)
        
        # Apply ordering
        query = query.order_by(desc(SafetyChecklist.created_at))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count_checklists(
        self,
        filters: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> int:
        """Count checklists with filtering."""
        query = select(func.count(SafetyChecklist.id))
        
        # Apply user filter for employees
        if user_id:
            query = query.where(SafetyChecklist.inspector_id == user_id)
        
        # Apply filters (same as list_checklists)
        if filters:
            if filters.get("status"):
                query = query.where(SafetyChecklist.status == filters["status"])
            
            if filters.get("project_name"):
                query = query.where(
                    SafetyChecklist.project_name.ilike(f"%{filters['project_name']}%")
                )
            
            if filters.get("location"):
                query = query.where(
                    SafetyChecklist.location.ilike(f"%{filters['location']}%")
                )
            
            if filters.get("inspector_id"):
                query = query.where(SafetyChecklist.inspector_id == filters["inspector_id"])
            
            if filters.get("date_from"):
                query = query.where(SafetyChecklist.inspection_date >= filters["date_from"])
            
            if filters.get("date_to"):
                query = query.where(SafetyChecklist.inspection_date <= filters["date_to"])
            
            if filters.get("critical_failures_only"):
                query = query.where(SafetyChecklist.critical_failures > 0)
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def update_checklist(self, checklist_id: str, update_data: dict) -> Optional[SafetyChecklist]:
        """Update a checklist."""
        query = select(SafetyChecklist).where(SafetyChecklist.id == checklist_id)
        result = await self.db.execute(query)
        checklist = result.scalar_one_or_none()
        
        if not checklist:
            return None
        
        for key, value in update_data.items():
            if hasattr(checklist, key):
                setattr(checklist, key, value)
        
        await self.db.commit()
        await self.db.refresh(checklist)
        return checklist
    
    async def delete_checklist(self, checklist_id: str) -> bool:
        """Delete a checklist."""
        query = select(SafetyChecklist).where(SafetyChecklist.id == checklist_id)
        result = await self.db.execute(query)
        checklist = result.scalar_one_or_none()
        
        if not checklist:
            return False
        
        await self.db.delete(checklist)
        await self.db.commit()
        return True
    
    async def approve_checklist(self, checklist_id: str, approved_by_id: str) -> Optional[SafetyChecklist]:
        """Approve a checklist."""
        update_data = {
            "status": "approved",
            "approved_by_id": approved_by_id,
            "approved_at": datetime.utcnow()
        }
        return await self.update_checklist(checklist_id, update_data)
    
    # Checklist item operations
    async def update_checklist_item(
        self,
        checklist_id: str,
        item_id: str,
        update_data: dict
    ) -> Optional[SafetyChecklistItem]:
        """Update a checklist item."""
        query = (
            select(SafetyChecklistItem)
            .where(
                and_(
                    SafetyChecklistItem.checklist_id == checklist_id,
                    SafetyChecklistItem.item_id == item_id
                )
            )
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            return None
        
        for key, value in update_data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        await self.db.commit()
        
        # Update checklist stats
        await self._update_checklist_stats(checklist_id)
        
        await self.db.refresh(item)
        return item
    
    async def bulk_update_checklist_items(
        self,
        checklist_id: str,
        item_updates: List[dict]
    ) -> bool:
        """Bulk update checklist items."""
        try:
            for update in item_updates:
                item_id = update.get("item_id")
                if not item_id:
                    continue
                
                update_data = {k: v for k, v in update.items() if k != "item_id"}
                await self.update_checklist_item(checklist_id, item_id, update_data)
            
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def _update_checklist_stats(self, checklist_id: str):
        """Update checklist statistics."""
        # Get all items for this checklist
        query = (
            select(SafetyChecklistItem)
            .where(SafetyChecklistItem.checklist_id == checklist_id)
        )
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        # Calculate stats
        total_items = len(items)
        passed_items = len([item for item in items if item.status == "pass"])
        failed_items = len([item for item in items if item.status == "fail"])
        na_items = len([item for item in items if item.status == "na"])
        critical_failures = len([
            item for item in items 
            if item.status == "fail" and item.is_critical
        ])
        
        # Update checklist
        checklist_query = select(SafetyChecklist).where(SafetyChecklist.id == checklist_id)
        checklist_result = await self.db.execute(checklist_query)
        checklist = checklist_result.scalar_one_or_none()
        
        if checklist:
            checklist.total_items = total_items
            checklist.passed_items = passed_items
            checklist.failed_items = failed_items
            checklist.na_items = na_items
            checklist.critical_failures = critical_failures
            
            # Auto-complete if all items are filled
            pending_items = total_items - passed_items - failed_items - na_items
            if pending_items == 0 and checklist.status == "draft":
                checklist.status = "completed"
            
            await self.db.commit()
    
    # Template operations
    async def create_template(self, template_data: dict) -> SafetyTemplate:
        """Create a new safety template."""
        template = SafetyTemplate(**template_data)
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template
    
    async def get_template(self, template_id: str) -> Optional[SafetyTemplate]:
        """Get a template by ID."""
        query = select(SafetyTemplate).where(SafetyTemplate.id == template_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_templates(
        self,
        skip: int = 0,
        limit: int = 50,
        active_only: bool = True
    ) -> List[SafetyTemplate]:
        """List templates."""
        query = select(SafetyTemplate)
        
        if active_only:
            query = query.where(SafetyTemplate.is_active == True)
        
        query = query.order_by(desc(SafetyTemplate.created_at))
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_template(self, template_id: str, update_data: dict) -> Optional[SafetyTemplate]:
        """Update a template."""
        query = select(SafetyTemplate).where(SafetyTemplate.id == template_id)
        result = await self.db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            return None
        
        for key, value in update_data.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        await self.db.commit()
        await self.db.refresh(template)
        return template
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete (deactivate) a template."""
        return await self.update_template(template_id, {"is_active": False}) is not None
    
    # Statistics and reporting
    async def get_checklist_stats(self, user_id: Optional[str] = None) -> dict:
        """Get checklist statistics."""
        base_query = select(SafetyChecklist)
        
        if user_id:
            base_query = base_query.where(SafetyChecklist.inspector_id == user_id)
        
        # Total checklists
        total_result = await self.db.execute(select(func.count()).select_from(base_query.subquery()))
        total_checklists = total_result.scalar()
        
        # Completed checklists
        completed_query = base_query.where(SafetyChecklist.status == "completed")
        completed_result = await self.db.execute(select(func.count()).select_from(completed_query.subquery()))
        completed_checklists = completed_result.scalar()
        
        # Approved checklists
        approved_query = base_query.where(SafetyChecklist.status == "approved")
        approved_result = await self.db.execute(select(func.count()).select_from(approved_query.subquery()))
        approved_checklists = approved_result.scalar()
        
        # Pending approval
        pending_query = base_query.where(SafetyChecklist.status == "completed")
        pending_result = await self.db.execute(select(func.count()).select_from(pending_query.subquery()))
        pending_approval = pending_result.scalar()
        
        # Critical failures
        critical_query = base_query.where(SafetyChecklist.critical_failures > 0)
        critical_result = await self.db.execute(select(func.count()).select_from(critical_query.subquery()))
        critical_failures_count = critical_result.scalar()
        
        # This month
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_query = base_query.where(SafetyChecklist.created_at >= month_start)
        month_result = await self.db.execute(select(func.count()).select_from(month_query.subquery()))
        checklists_this_month = month_result.scalar()
        
        # This week
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_query = base_query.where(SafetyChecklist.created_at >= week_start)
        week_result = await self.db.execute(select(func.count()).select_from(week_query.subquery()))
        checklists_this_week = week_result.scalar()
        
        # Average completion rate
        if total_checklists > 0:
            avg_query = base_query.where(SafetyChecklist.total_items > 0)
            avg_result = await self.db.execute(
                select(func.avg(
                    (SafetyChecklist.passed_items + SafetyChecklist.na_items) * 100.0 / SafetyChecklist.total_items
                )).select_from(avg_query.subquery())
            )
            average_completion_rate = avg_result.scalar() or 0.0
        else:
            average_completion_rate = 0.0
        
        return {
            "total_checklists": total_checklists,
            "completed_checklists": completed_checklists,
            "approved_checklists": approved_checklists,
            "pending_approval": pending_approval,
            "critical_failures_count": critical_failures_count,
            "average_completion_rate": round(average_completion_rate, 2),
            "checklists_this_month": checklists_this_month,
            "checklists_this_week": checklists_this_week
        }
    
    async def get_recent_checklists(self, limit: int = 10, user_id: Optional[str] = None) -> List[SafetyChecklist]:
        """Get recent checklists."""
        query = select(SafetyChecklist).options(selectinload(SafetyChecklist.checklist_items))
        
        if user_id:
            query = query.where(SafetyChecklist.inspector_id == user_id)
        
        query = query.order_by(desc(SafetyChecklist.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_pending_approvals(self, limit: int = 10) -> List[SafetyChecklist]:
        """Get checklists pending approval."""
        query = (
            select(SafetyChecklist)
            .options(selectinload(SafetyChecklist.checklist_items))
            .where(SafetyChecklist.status == "completed")
            .order_by(SafetyChecklist.created_at)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_critical_failures(self, limit: int = 10, user_id: Optional[str] = None) -> List[SafetyChecklist]:
        """Get checklists with critical failures."""
        query = (
            select(SafetyChecklist)
            .options(selectinload(SafetyChecklist.checklist_items))
            .where(SafetyChecklist.critical_failures > 0)
        )
        
        if user_id:
            query = query.where(SafetyChecklist.inspector_id == user_id)
        
        query = query.order_by(desc(SafetyChecklist.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
