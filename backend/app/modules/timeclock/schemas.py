"""
Timeclock schemas.
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, validator


class JobSiteBase(BaseModel):
    """Base job site schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    radius_meters: int = Field(100, ge=10, le=1000)


class JobSiteCreate(JobSiteBase):
    """Schema for creating a job site."""
    pass


class JobSiteUpdate(BaseModel):
    """Schema for updating a job site."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    radius_meters: Optional[int] = Field(None, ge=10, le=1000)
    is_active: Optional[bool] = None


class JobSite(JobSiteBase):
    """Job site response schema."""
    id: str
    qr_code_data: str
    is_active: bool
    created_by_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobSiteWithQR(JobSite):
    """Job site with QR code image data."""
    qr_code_image: str  # Base64 encoded QR code image


class TimeEntryBase(BaseModel):
    """Base time entry schema."""
    notes: Optional[str] = None


class ClockInRequest(BaseModel):
    """Schema for clocking in."""
    qr_code_data: str = Field(..., min_length=1)
    location_lat: Optional[Decimal] = Field(None, ge=-90, le=90)
    location_lng: Optional[Decimal] = Field(None, ge=-180, le=180)
    notes: Optional[str] = None


class ClockOutRequest(BaseModel):
    """Schema for clocking out."""
    time_entry_id: str
    location_lat: Optional[Decimal] = Field(None, ge=-90, le=90)
    location_lng: Optional[Decimal] = Field(None, ge=-180, le=180)
    notes: Optional[str] = None


class BreakRequest(BaseModel):
    """Schema for break start/end."""
    time_entry_id: str
    action: str = Field(..., pattern="^(start|end)$")


class TimeEntry(TimeEntryBase):
    """Time entry response schema."""
    id: str
    user_id: str
    job_site_id: str
    clock_in_time: datetime
    clock_out_time: Optional[datetime] = None
    break_start_time: Optional[datetime] = None
    break_end_time: Optional[datetime] = None
    total_hours: Optional[Decimal] = None
    break_hours: Optional[Decimal] = None
    clock_in_location_lat: Optional[Decimal] = None
    clock_in_location_lng: Optional[Decimal] = None
    clock_out_location_lat: Optional[Decimal] = None
    clock_out_location_lng: Optional[Decimal] = None
    is_approved: bool
    approved_by_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimeEntryWithDetails(TimeEntry):
    """Time entry with related data."""
    job_site: JobSite
    user_name: str
    approved_by_name: Optional[str] = None


class TimeEntryApproval(BaseModel):
    """Schema for approving time entries."""
    approved: bool
    notes: Optional[str] = None


class TimeclockStats(BaseModel):
    """Timeclock statistics."""
    total_employees_clocked_in: int
    total_active_job_sites: int
    total_hours_today: Decimal
    total_hours_this_week: Decimal
    pending_approvals: int


class QRCodeScanResult(BaseModel):
    """Result of QR code scan."""
    job_site: JobSite
    can_clock_in: bool
    can_clock_out: bool
    active_time_entry_id: Optional[str] = None
    message: str
