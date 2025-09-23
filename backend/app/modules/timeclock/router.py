"""
Timeclock router.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db import get_db
from ...core.security import get_current_user, require_role, CurrentUser
from ..auth.models import User
from .repository import TimeclockRepository
from .service import TimeclockService
from .schemas import (
    JobSiteCreate, JobSiteUpdate, JobSite, JobSiteWithQR,
    ClockInRequest, ClockOutRequest, BreakRequest, TimeEntry, TimeEntryWithDetails,
    TimeEntryApproval, TimeclockStats, QRCodeScanResult
)

router = APIRouter()


async def get_timeclock_repository(db: AsyncSession = Depends(get_db)) -> TimeclockRepository:
    """Get timeclock repository."""
    return TimeclockRepository(db)


async def get_timeclock_service(
    repository: TimeclockRepository = Depends(get_timeclock_repository)
) -> TimeclockService:
    """Get timeclock service."""
    from ...core.container import get_event_bus
    return TimeclockService(repository, get_event_bus())


# Job Site Management (Admin only)
@router.post("/job-sites", response_model=JobSiteWithQR, status_code=status.HTTP_201_CREATED)
async def create_job_site(
    job_site_data: JobSiteCreate,
    current_user: User = Depends(require_role(["admin", "superadmin"])),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Create a new job site with QR code."""
    try:
        return await service.create_job_site(job_site_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/job-sites", response_model=List[JobSite])
async def get_job_sites(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: CurrentUser = Depends(get_current_user),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Get all job sites."""
    return service.get_job_sites(skip, limit, active_only)


@router.get("/job-sites/{job_site_id}", response_model=JobSite)
async def get_job_site(
    job_site_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Get job site by ID."""
    job_site = service.get_job_site(job_site_id)
    if not job_site:
        raise HTTPException(status_code=404, detail="Job site not found")
    return job_site


@router.get("/job-sites/{job_site_id}/qr", response_model=JobSiteWithQR)
async def get_job_site_with_qr(
    job_site_id: str,
    current_user: User = Depends(require_role(["admin", "superadmin"])),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Get job site with QR code image (admin only)."""
    job_site = service.get_job_site_with_qr(job_site_id)
    if not job_site:
        raise HTTPException(status_code=404, detail="Job site not found")
    return job_site


@router.put("/job-sites/{job_site_id}", response_model=JobSite)
async def update_job_site(
    job_site_id: str,
    job_site_data: JobSiteUpdate,
    current_user: User = Depends(require_role(["admin", "superadmin"])),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Update job site."""
    job_site = await service.update_job_site(job_site_id, job_site_data, current_user.id)
    if not job_site:
        raise HTTPException(status_code=404, detail="Job site not found")
    return job_site


@router.delete("/job-sites/{job_site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_site(
    job_site_id: str,
    current_user: User = Depends(require_role(["admin", "superadmin"])),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Delete job site."""
    success = await service.delete_job_site(job_site_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Job site not found")


# QR Code Scanning
@router.post("/scan", response_model=QRCodeScanResult)
async def scan_qr_code(
    qr_code_data: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Scan QR code and get available actions."""
    return await service.scan_qr_code(qr_code_data, current_user.id)


# Time Tracking
@router.post("/clock-in", response_model=dict)
async def clock_in(
    request: ClockInRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TimeclockService = Depends(get_timeclock_service),
    http_request: Request = None
):
    """Clock in at job site."""
    try:
        ip_address = http_request.client.host if http_request else None
        time_entry, message = await service.clock_in(request, current_user.id, ip_address)
        return {
            "time_entry": time_entry,
            "message": message
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clock-out", response_model=dict)
async def clock_out(
    request: ClockOutRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TimeclockService = Depends(get_timeclock_service),
    http_request: Request = None
):
    """Clock out from job site."""
    try:
        ip_address = http_request.client.host if http_request else None
        time_entry, message = await service.clock_out(request, current_user.id, ip_address)
        return {
            "time_entry": time_entry,
            "message": message
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/break", response_model=dict)
async def manage_break(
    request: BreakRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Start or end break."""
    try:
        if request.action == "start":
            time_entry, message = await service.start_break(request, current_user.id)
        else:
            time_entry, message = await service.end_break(request, current_user.id)
        
        return {
            "time_entry": time_entry,
            "message": message
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Time Entry Management
@router.get("/time-entries", response_model=List[TimeEntryWithDetails])
async def get_time_entries(
    user_id: Optional[str] = None,
    job_site_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Get time entries. Regular users can only see their own entries."""
    # Regular users can only see their own entries
    if current_user.role == "employee":
        user_id = current_user.id
    
    return service.get_time_entries(user_id, job_site_id, start_date, end_date, skip, limit)


@router.get("/time-entries/active", response_model=Optional[TimeEntry])
async def get_active_time_entry(
    current_user: CurrentUser = Depends(get_current_user),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Get current user's active time entry."""
    return await service.get_user_active_time_entry(current_user.id)


@router.post("/time-entries/{time_entry_id}/approve", response_model=TimeEntry)
async def approve_time_entry(
    time_entry_id: str,
    approval: TimeEntryApproval,
    current_user: User = Depends(require_role(["admin", "superadmin"])),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Approve or reject time entry."""
    time_entry = await service.approve_time_entry(time_entry_id, approval.approved, current_user.id)
    if not time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return time_entry


# Statistics and Reports
@router.get("/stats", response_model=TimeclockStats)
async def get_timeclock_stats(
    current_user: User = Depends(require_role(["admin", "superadmin"])),
    service: TimeclockService = Depends(get_timeclock_service)
):
    """Get timeclock statistics."""
    return service.get_timeclock_stats()


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "module": "timeclock"}
