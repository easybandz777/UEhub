"""
OSHA Safety Checklist router.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.container import get_event_bus_dep, get_mail_service
from ...core.db import get_db
from ...core.interfaces import EventBus, MailService
from ...core.security import (
    CurrentUser,
    require_authenticated,
    require_admin_or_superadmin,
    require_permission,
    Permission,
)
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
from .service import SafetyService

router = APIRouter()


def get_safety_service(
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus_dep),
    mail_service: MailService = Depends(get_mail_service)
) -> SafetyService:
    """Get safety service with dependencies."""
    repository = SafetyRepository(db)
    return SafetyService(repository, event_bus, mail_service)


# Dashboard and statistics
@router.get("/dashboard", response_model=SafetyDashboardData)
async def get_dashboard(
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Get safety dashboard data."""
    return await safety_service.get_dashboard_data(current_user)


@router.get("/stats", response_model=SafetyChecklistStats)
async def get_stats(
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Get safety checklist statistics."""
    return await safety_service.get_checklist_stats(current_user)


# Checklist operations
@router.post("/checklists", response_model=SafetyChecklistResponse)
async def create_checklist(
    checklist_data: SafetyChecklistCreate,
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Create a new safety checklist."""
    return await safety_service.create_checklist(checklist_data, current_user)


@router.get("/checklists", response_model=SafetyChecklistListResponse)
async def list_checklists(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    project_name: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    inspector_id: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    critical_failures_only: bool = Query(False),
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """List safety checklists with filtering."""
    return await safety_service.list_checklists(
        page=page,
        per_page=per_page,
        current_user=current_user,
        project_name=project_name,
        location=location,
        status_filter=status,
        inspector_id=inspector_id,
        date_from=date_from,
        date_to=date_to,
        critical_failures_only=critical_failures_only
    )


@router.get("/checklists/{checklist_id}", response_model=SafetyChecklistResponse)
async def get_checklist(
    checklist_id: str,
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Get a safety checklist by ID."""
    checklist = await safety_service.get_checklist(checklist_id, current_user)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found"
        )
    return checklist


@router.put("/checklists/{checklist_id}", response_model=SafetyChecklistResponse)
async def update_checklist(
    checklist_id: str,
    update_data: SafetyChecklistUpdate,
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Update a safety checklist."""
    checklist = await safety_service.update_checklist(checklist_id, update_data, current_user)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found"
        )
    return checklist


@router.delete("/checklists/{checklist_id}")
async def delete_checklist(
    checklist_id: str,
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Delete a safety checklist."""
    success = await safety_service.delete_checklist(checklist_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found"
        )
    return {"message": "Checklist deleted successfully"}


@router.post("/checklists/{checklist_id}/approve", response_model=SafetyChecklistResponse)
async def approve_checklist(
    checklist_id: str,
    approval_data: ChecklistApproval,
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Approve or reject a safety checklist."""
    checklist = await safety_service.approve_checklist(checklist_id, approval_data, current_user)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found"
        )
    return checklist


# Checklist item operations
@router.put("/checklists/{checklist_id}/items/{item_id}", response_model=SafetyChecklistItemResponse)
async def update_checklist_item(
    checklist_id: str,
    item_id: str,
    update_data: SafetyChecklistItemUpdate,
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Update a checklist item."""
    item = await safety_service.update_checklist_item(
        checklist_id, item_id, update_data, current_user
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist item not found"
        )
    return item


@router.post("/checklists/{checklist_id}/items/bulk-update")
async def bulk_update_checklist_items(
    checklist_id: str,
    bulk_update: BulkItemUpdate,
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Bulk update checklist items."""
    success = await safety_service.bulk_update_checklist_items(
        checklist_id, bulk_update, current_user
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update checklist items"
        )
    return {"message": "Checklist items updated successfully"}


# Template operations
@router.post("/templates", response_model=SafetyTemplateResponse)
async def create_template(
    template_data: SafetyTemplateCreate,
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Create a new safety template."""
    return await safety_service.create_template(template_data, current_user)


@router.get("/templates", response_model=list[SafetyTemplateResponse])
async def list_templates(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    active_only: bool = Query(True),
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """List safety templates."""
    return await safety_service.list_templates(
        page=page,
        per_page=per_page,
        active_only=active_only
    )


@router.get("/templates/{template_id}", response_model=SafetyTemplateResponse)
async def get_template(
    template_id: str,
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Get a safety template by ID."""
    template = await safety_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return template


@router.put("/templates/{template_id}", response_model=SafetyTemplateResponse)
async def update_template(
    template_id: str,
    update_data: SafetyTemplateUpdate,
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Update a safety template."""
    template = await safety_service.update_template(template_id, update_data, current_user)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return template


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Delete (deactivate) a safety template."""
    success = await safety_service.delete_template(template_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return {"message": "Template deleted successfully"}


@router.get("/templates/default/osha")
async def get_default_osha_template(
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Get the default OSHA scaffolding checklist template."""
    return await safety_service.get_default_osha_template()


# Reporting endpoints
@router.get("/checklists/{checklist_id}/report")
async def generate_checklist_report(
    checklist_id: str,
    format: str = Query("pdf", regex="^(pdf|excel|json)$"),
    current_user: CurrentUser = Depends(require_authenticated),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Generate a checklist report."""
    # Check if checklist exists and user has access
    checklist = await safety_service.get_checklist(checklist_id, current_user)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found"
        )
    
    # TODO: Implement report generation
    return {
        "message": "Report generation not yet implemented",
        "checklist_id": checklist_id,
        "format": format
    }


# Bulk operations
@router.post("/checklists/bulk-approve")
async def bulk_approve_checklists(
    checklist_ids: list[str],
    approval_data: ChecklistApproval,
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Bulk approve multiple checklists."""
    results = []
    for checklist_id in checklist_ids:
        try:
            checklist = await safety_service.approve_checklist(
                checklist_id, approval_data, current_user
            )
            if checklist:
                results.append({"checklist_id": checklist_id, "status": "approved"})
            else:
                results.append({"checklist_id": checklist_id, "status": "not_found"})
        except Exception as e:
            results.append({"checklist_id": checklist_id, "status": "error", "error": str(e)})
    
    return {"results": results}


# Analytics endpoints
@router.get("/analytics/completion-trends")
async def get_completion_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Get checklist completion trends."""
    # TODO: Implement analytics
    return {
        "message": "Analytics not yet implemented",
        "days": days
    }


@router.get("/analytics/critical-failures")
async def get_critical_failure_analysis(
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    safety_service: SafetyService = Depends(get_safety_service)
):
    """Get critical failure analysis."""
    # TODO: Implement critical failure analysis
    return {
        "message": "Critical failure analysis not yet implemented"
    }
