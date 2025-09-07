"""
OSHA Safety Checklist service.
"""

import math
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import HTTPException, status

from ...core.events import EventBus
from ...core.interfaces import MailService, PDFService
from ...core.security import CurrentUser, can_access_checklist, can_approve_checklist
from .repository import SafetyRepository
from .schemas import (
    SafetyChecklistCreate,
    SafetyChecklistResponse,
    SafetyChecklistUpdate,
    SafetyChecklistListResponse,
    SafetyChecklistStats,
    SafetyChecklistItemUpdate,
    SafetyChecklistItemResponse,
    SafetyTemplateCreate,
    SafetyTemplateResponse,
    SafetyTemplateUpdate,
    SafetyDashboardData,
    BulkItemUpdate,
    ChecklistApproval,
)


class SafetyService:
    """Safety checklist service."""
    
    def __init__(
        self,
        repository: SafetyRepository,
        event_bus: EventBus,
        mail_service: MailService,
        pdf_service: Optional[PDFService] = None
    ):
        self.repository = repository
        self.event_bus = event_bus
        self.mail_service = mail_service
        self.pdf_service = pdf_service
    
    # Checklist operations
    async def create_checklist(
        self,
        checklist_data: SafetyChecklistCreate,
        current_user: CurrentUser
    ) -> SafetyChecklistResponse:
        """Create a new safety checklist."""
        # Add inspector ID from current user
        create_data = checklist_data.dict()
        create_data["inspector_id"] = current_user.id
        
        # Set initial stats
        create_data.update({
            "status": "draft",
            "total_items": len(create_data.get("checklist_items", [])),
            "passed_items": 0,
            "failed_items": 0,
            "na_items": 0,
            "critical_failures": 0
        })
        
        checklist = await self.repository.create_checklist(create_data)
        
        # Publish event
        await self.event_bus.publish({
            "type": "checklist_created",
            "checklist_id": str(checklist.id),
            "inspector_id": current_user.id,
            "project_name": checklist.project_name
        })
        
        return SafetyChecklistResponse.from_orm(checklist)
    
    async def get_checklist(
        self,
        checklist_id: str,
        current_user: CurrentUser
    ) -> Optional[SafetyChecklistResponse]:
        """Get a checklist by ID."""
        checklist = await self.repository.get_checklist(checklist_id)
        if not checklist:
            return None
        
        # Check access permissions
        if not can_access_checklist(current_user, str(checklist.inspector_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this checklist"
            )
        
        return SafetyChecklistResponse.from_orm(checklist)
    
    async def list_checklists(
        self,
        current_user: CurrentUser,
        page: int = 1,
        per_page: int = 50,
        project_name: Optional[str] = None,
        location: Optional[str] = None,
        status_filter: Optional[str] = None,
        inspector_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        critical_failures_only: bool = False
    ) -> SafetyChecklistListResponse:
        """List checklists with filtering."""
        if per_page > 100:
            per_page = 100
        
        skip = (page - 1) * per_page
        
        # Build filters
        filters = {}
        if project_name:
            filters["project_name"] = project_name
        if location:
            filters["location"] = location
        if status_filter:
            filters["status"] = status_filter
        if inspector_id:
            filters["inspector_id"] = inspector_id
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        if critical_failures_only:
            filters["critical_failures_only"] = True
        
        # For employees, only show their own checklists
        user_id_filter = None
        if current_user.role == "employee":
            user_id_filter = current_user.id
        
        checklists = await self.repository.list_checklists(
            skip=skip,
            limit=per_page,
            filters=filters,
            user_id=user_id_filter
        )
        
        total = await self.repository.count_checklists(
            filters=filters,
            user_id=user_id_filter
        )
        
        return SafetyChecklistListResponse(
            items=[SafetyChecklistResponse.from_orm(checklist) for checklist in checklists],
            total=total,
            page=page,
            per_page=per_page,
            pages=math.ceil(total / per_page)
        )
    
    async def update_checklist(
        self,
        checklist_id: str,
        update_data: SafetyChecklistUpdate,
        current_user: CurrentUser
    ) -> Optional[SafetyChecklistResponse]:
        """Update a checklist."""
        # Check if checklist exists and user has access
        existing = await self.repository.get_checklist(checklist_id)
        if not existing:
            return None
        
        if not can_access_checklist(current_user, str(existing.inspector_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this checklist"
            )
        
        # Don't allow status changes by employees
        if current_user.role == "employee" and update_data.status:
            update_data.status = None
        
        checklist = await self.repository.update_checklist(
            checklist_id,
            update_data.dict(exclude_unset=True)
        )
        
        if checklist:
            # Publish event
            await self.event_bus.publish({
                "type": "checklist_updated",
                "checklist_id": checklist_id,
                "updated_by": current_user.id
            })
        
        return SafetyChecklistResponse.from_orm(checklist) if checklist else None
    
    async def delete_checklist(
        self,
        checklist_id: str,
        current_user: CurrentUser
    ) -> bool:
        """Delete a checklist."""
        # Check if checklist exists and user has access
        existing = await self.repository.get_checklist(checklist_id)
        if not existing:
            return False
        
        if not can_access_checklist(current_user, str(existing.inspector_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this checklist"
            )
        
        success = await self.repository.delete_checklist(checklist_id)
        
        if success:
            # Publish event
            await self.event_bus.publish({
                "type": "checklist_deleted",
                "checklist_id": checklist_id,
                "deleted_by": current_user.id
            })
        
        return success
    
    async def approve_checklist(
        self,
        checklist_id: str,
        approval_data: ChecklistApproval,
        current_user: CurrentUser
    ) -> Optional[SafetyChecklistResponse]:
        """Approve or reject a checklist."""
        if not can_approve_checklist(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve checklists"
            )
        
        # Check if checklist exists
        existing = await self.repository.get_checklist(checklist_id)
        if not existing:
            return None
        
        if existing.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only completed checklists can be approved"
            )
        
        if approval_data.approved:
            checklist = await self.repository.approve_checklist(checklist_id, current_user.id)
            event_type = "checklist_approved"
        else:
            # Reject - set back to draft
            checklist = await self.repository.update_checklist(
                checklist_id,
                {"status": "draft"}
            )
            event_type = "checklist_rejected"
        
        if checklist:
            # Publish event
            await self.event_bus.publish({
                "type": event_type,
                "checklist_id": checklist_id,
                "approved_by": current_user.id,
                "comments": approval_data.comments
            })
            
            # Send notification email to inspector
            try:
                await self.mail_service.send_template(
                    to=existing.inspector.email,
                    template="checklist_approval",
                    data={
                        "project_name": existing.project_name,
                        "approved": approval_data.approved,
                        "approver_name": current_user.name,
                        "comments": approval_data.comments
                    }
                )
            except Exception as e:
                # Log error but don't fail the approval
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send approval email: {e}")
        
        return SafetyChecklistResponse.from_orm(checklist) if checklist else None
    
    # Checklist item operations
    async def update_checklist_item(
        self,
        checklist_id: str,
        item_id: str,
        update_data: SafetyChecklistItemUpdate,
        current_user: CurrentUser
    ) -> Optional[SafetyChecklistItemResponse]:
        """Update a checklist item."""
        # Check access
        existing = await self.repository.get_checklist(checklist_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist not found"
            )
        
        if not can_access_checklist(current_user, str(existing.inspector_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this checklist"
            )
        
        item = await self.repository.update_checklist_item(
            checklist_id,
            item_id,
            update_data.dict(exclude_unset=True)
        )
        
        return SafetyChecklistItemResponse.from_orm(item) if item else None
    
    async def bulk_update_checklist_items(
        self,
        checklist_id: str,
        bulk_update: BulkItemUpdate,
        current_user: CurrentUser
    ) -> bool:
        """Bulk update checklist items."""
        # Check access
        existing = await self.repository.get_checklist(checklist_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist not found"
            )
        
        if not can_access_checklist(current_user, str(existing.inspector_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this checklist"
            )
        
        success = await self.repository.bulk_update_checklist_items(
            checklist_id,
            bulk_update.item_updates
        )
        
        if success:
            # Publish event
            await self.event_bus.publish({
                "type": "checklist_items_updated",
                "checklist_id": checklist_id,
                "updated_by": current_user.id,
                "item_count": len(bulk_update.item_updates)
            })
        
        return success
    
    # Template operations
    async def create_template(
        self,
        template_data: SafetyTemplateCreate,
        current_user: CurrentUser
    ) -> SafetyTemplateResponse:
        """Create a new safety template."""
        create_data = template_data.dict()
        create_data["created_by_id"] = current_user.id
        
        template = await self.repository.create_template(create_data)
        return SafetyTemplateResponse.from_orm(template)
    
    async def get_template(self, template_id: str) -> Optional[SafetyTemplateResponse]:
        """Get a template by ID."""
        template = await self.repository.get_template(template_id)
        return SafetyTemplateResponse.from_orm(template) if template else None
    
    async def list_templates(
        self,
        page: int = 1,
        per_page: int = 50,
        active_only: bool = True
    ) -> List[SafetyTemplateResponse]:
        """List templates."""
        if per_page > 100:
            per_page = 100
        
        skip = (page - 1) * per_page
        
        templates = await self.repository.list_templates(
            skip=skip,
            limit=per_page,
            active_only=active_only
        )
        
        return [SafetyTemplateResponse.from_orm(template) for template in templates]
    
    async def update_template(
        self,
        template_id: str,
        update_data: SafetyTemplateUpdate,
        current_user: CurrentUser
    ) -> Optional[SafetyTemplateResponse]:
        """Update a template."""
        template = await self.repository.update_template(
            template_id,
            update_data.dict(exclude_unset=True)
        )
        return SafetyTemplateResponse.from_orm(template) if template else None
    
    async def delete_template(
        self,
        template_id: str,
        current_user: CurrentUser
    ) -> bool:
        """Delete (deactivate) a template."""
        return await self.repository.delete_template(template_id)
    
    # Statistics and dashboard
    async def get_checklist_stats(self, current_user: CurrentUser) -> SafetyChecklistStats:
        """Get checklist statistics."""
        # For employees, only show their own stats
        user_id = current_user.id if current_user.role == "employee" else None
        
        stats_data = await self.repository.get_checklist_stats(user_id)
        return SafetyChecklistStats(**stats_data)
    
    async def get_dashboard_data(self, current_user: CurrentUser) -> SafetyDashboardData:
        """Get dashboard data."""
        # For employees, only show their own data
        user_id = current_user.id if current_user.role == "employee" else None
        
        # Get stats
        stats_data = await self.repository.get_checklist_stats(user_id)
        stats = SafetyChecklistStats(**stats_data)
        
        # Get recent checklists
        recent_checklists_data = await self.repository.get_recent_checklists(
            limit=5,
            user_id=user_id
        )
        recent_checklists = [
            SafetyChecklistResponse.from_orm(checklist)
            for checklist in recent_checklists_data
        ]
        
        # Get pending approvals (admin/superadmin only)
        pending_approvals = []
        if current_user.role in ["admin", "superadmin"]:
            pending_approvals_data = await self.repository.get_pending_approvals(limit=5)
            pending_approvals = [
                SafetyChecklistResponse.from_orm(checklist)
                for checklist in pending_approvals_data
            ]
        
        # Get critical failures
        critical_failures_data = await self.repository.get_critical_failures(
            limit=5,
            user_id=user_id
        )
        critical_failures = [
            SafetyChecklistResponse.from_orm(checklist)
            for checklist in critical_failures_data
        ]
        
        # Completion trend (simplified - last 7 days)
        completion_trend = []  # TODO: Implement time series data
        
        return SafetyDashboardData(
            stats=stats,
            recent_checklists=recent_checklists,
            pending_approvals=pending_approvals,
            critical_failures=critical_failures,
            completion_trend=completion_trend
        )
    
    # Default OSHA template
    async def get_default_osha_template(self) -> dict:
        """Get the default OSHA scaffolding checklist template."""
        return {
            "name": "OSHA Scaffolding Safety Checklist",
            "description": "Comprehensive OSHA scaffolding safety inspection checklist based on 29 CFR 1926.451-454",
            "version": "1.0",
            "template_data": {
                "categories": [
                    {
                        "name": "Foundation & Support",
                        "items": [
                            {
                                "id": "1.1",
                                "number": "1.1",
                                "text": "Foundation is level, sound, rigid, and capable of supporting 4x intended load (minimum 25 psf)",
                                "critical": True
                            },
                            {
                                "id": "1.2",
                                "number": "1.2",
                                "text": "Base plates and mud sills properly installed under each leg",
                                "critical": True
                            },
                            {
                                "id": "1.3",
                                "number": "1.3",
                                "text": "Scaffold is plumb, level, and square within tolerance (±1/4 inch per 10 feet)",
                                "critical": True
                            },
                            {
                                "id": "1.4",
                                "number": "1.4",
                                "text": "Footings are adequate for soil conditions and load requirements",
                                "critical": True
                            },
                            {
                                "id": "1.5",
                                "number": "1.5",
                                "text": "Drainage provided to prevent water accumulation under scaffold",
                                "critical": False
                            }
                        ]
                    },
                    {
                        "name": "Platform & Planking",
                        "items": [
                            {
                                "id": "2.1",
                                "number": "2.1",
                                "text": "Platforms fully planked or decked between front uprights and guardrail supports",
                                "critical": True
                            },
                            {
                                "id": "2.2",
                                "number": "2.2",
                                "text": "Platform width is minimum 18 inches (46 cm) for work platforms",
                                "critical": True
                            },
                            {
                                "id": "2.3",
                                "number": "2.3",
                                "text": "Platforms/planks overlap supports by minimum 6 inches and maximum 12 inches",
                                "critical": True
                            },
                            {
                                "id": "2.4",
                                "number": "2.4",
                                "text": "Platform planks are scaffold grade or equivalent (minimum 1500 psi fiber stress)",
                                "critical": True
                            },
                            {
                                "id": "2.5",
                                "number": "2.5",
                                "text": "Platforms secured to prevent movement or uplift",
                                "critical": True
                            },
                            {
                                "id": "2.6",
                                "number": "2.6",
                                "text": "Maximum gap between planks is 1 inch, except at uprights where gap cannot exceed 9.5 inches",
                                "critical": False
                            }
                        ]
                    }
                    # ... (other categories would be included here)
                ]
            }
        }
