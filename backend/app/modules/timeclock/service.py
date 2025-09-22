"""
Timeclock service.
"""

import base64
import hashlib
import io
from datetime import datetime
from typing import List, Optional, Tuple
from decimal import Decimal

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SquareGradiantColorMask

from ...core.interfaces import EventBus
from .repository import TimeclockRepository
from .schemas import (
    JobSiteCreate, JobSiteUpdate, JobSite, JobSiteWithQR,
    ClockInRequest, ClockOutRequest, BreakRequest, TimeEntry, TimeEntryWithDetails,
    TimeclockStats, QRCodeScanResult
)


class TimeclockService:
    """Service for timeclock operations."""

    def __init__(self, repository: TimeclockRepository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    def _generate_qr_code_data(self, job_site_name: str, job_site_id: str) -> str:
        """Generate unique QR code data for job site."""
        # Create a unique identifier combining job site info with timestamp
        timestamp = datetime.utcnow().isoformat()
        raw_data = f"UE_HUB_JOBSITE:{job_site_id}:{job_site_name}:{timestamp}"
        
        # Create a hash for security and uniqueness
        hash_object = hashlib.sha256(raw_data.encode())
        hash_hex = hash_object.hexdigest()[:16]  # Use first 16 chars
        
        return f"UEHUB-{job_site_id}-{hash_hex}"

    def _generate_qr_code_image(self, qr_data: str) -> str:
        """Generate QR code image as base64 string."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create styled QR code
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SquareGradiantColorMask(
                back_color=(255, 255, 255),
                center_color=(0, 100, 200),
                edge_color=(0, 50, 150)
            )
        )

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    def _calculate_distance(self, lat1: Decimal, lng1: Decimal, lat2: Decimal, lng2: Decimal) -> float:
        """Calculate distance between two coordinates in meters using Haversine formula."""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to float for calculation
        lat1, lng1, lat2, lng2 = float(lat1), float(lng1), float(lat2), float(lng2)
        
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Radius of earth in meters
        return c * r

    # Job Site methods
    async def create_job_site(self, job_site_data: JobSiteCreate, created_by_id: str) -> JobSiteWithQR:
        """Create a new job site with QR code."""
        # Generate QR code data
        temp_id = "temp"  # We'll update this after creation
        qr_code_data = self._generate_qr_code_data(job_site_data.name, temp_id)
        
        # Create job site
        job_site = self.repository.create_job_site(job_site_data, created_by_id, qr_code_data)
        
        # Update QR code data with actual ID
        actual_qr_data = self._generate_qr_code_data(job_site_data.name, job_site.id)
        job_site.qr_code_data = actual_qr_data
        self.repository.db.commit()
        
        # Generate QR code image
        qr_code_image = self._generate_qr_code_image(actual_qr_data)
        
        # Publish event
        await self.event_bus.publish("timeclock.job_site.created", {
            "job_site_id": job_site.id,
            "name": job_site.name,
            "created_by_id": created_by_id
        })
        
        return JobSiteWithQR(
            **job_site.__dict__,
            qr_code_image=qr_code_image
        )

    def get_job_site(self, job_site_id: str) -> Optional[JobSite]:
        """Get job site by ID."""
        job_site = self.repository.get_job_site(job_site_id)
        return JobSite.from_orm(job_site) if job_site else None

    def get_job_site_with_qr(self, job_site_id: str) -> Optional[JobSiteWithQR]:
        """Get job site with QR code image."""
        job_site = self.repository.get_job_site(job_site_id)
        if not job_site:
            return None
        
        qr_code_image = self._generate_qr_code_image(job_site.qr_code_data)
        return JobSiteWithQR(
            **job_site.__dict__,
            qr_code_image=qr_code_image
        )

    def get_job_sites(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[JobSite]:
        """Get all job sites."""
        job_sites = self.repository.get_job_sites(skip, limit, active_only)
        return [JobSite.from_orm(js) for js in job_sites]

    async def update_job_site(self, job_site_id: str, job_site_data: JobSiteUpdate, updated_by_id: str) -> Optional[JobSite]:
        """Update job site."""
        job_site = self.repository.update_job_site(job_site_id, job_site_data)
        if not job_site:
            return None
        
        # Publish event
        await self.event_bus.publish("timeclock.job_site.updated", {
            "job_site_id": job_site.id,
            "updated_by_id": updated_by_id,
            "changes": job_site_data.dict(exclude_unset=True)
        })
        
        return JobSite.from_orm(job_site)

    async def delete_job_site(self, job_site_id: str, deleted_by_id: str) -> bool:
        """Delete job site."""
        success = self.repository.delete_job_site(job_site_id)
        if success:
            await self.event_bus.publish("timeclock.job_site.deleted", {
                "job_site_id": job_site_id,
                "deleted_by_id": deleted_by_id
            })
        return success

    # QR Code scanning and validation
    async def scan_qr_code(self, qr_code_data: str, user_id: str) -> QRCodeScanResult:
        """Process QR code scan and return available actions."""
        # Find job site by QR code
        job_site = self.repository.get_job_site_by_qr_code(qr_code_data)
        if not job_site:
            return QRCodeScanResult(
                job_site=None,
                can_clock_in=False,
                can_clock_out=False,
                message="Invalid QR code. Please scan a valid job site QR code."
            )
        
        # Check if user has active time entry
        active_entry = self.repository.get_active_time_entry(user_id)
        
        if active_entry:
            # User is clocked in
            if active_entry.job_site_id == job_site.id:
                # Same job site - can clock out
                return QRCodeScanResult(
                    job_site=JobSite.from_orm(job_site),
                    can_clock_in=False,
                    can_clock_out=True,
                    active_time_entry_id=active_entry.id,
                    message=f"You are clocked in at {job_site.name}. You can clock out or take a break."
                )
            else:
                # Different job site - need to clock out first
                return QRCodeScanResult(
                    job_site=JobSite.from_orm(job_site),
                    can_clock_in=False,
                    can_clock_out=False,
                    active_time_entry_id=active_entry.id,
                    message=f"You are already clocked in at another job site. Please clock out first."
                )
        else:
            # User is not clocked in - can clock in
            return QRCodeScanResult(
                job_site=JobSite.from_orm(job_site),
                can_clock_in=True,
                can_clock_out=False,
                message=f"Ready to clock in at {job_site.name}."
            )

    # Time tracking methods
    async def clock_in(self, request: ClockInRequest, user_id: str, ip_address: Optional[str] = None) -> Tuple[TimeEntry, str]:
        """Clock in user at job site."""
        # Validate QR code and get job site
        job_site = self.repository.get_job_site_by_qr_code(request.qr_code_data)
        if not job_site:
            raise ValueError("Invalid QR code")
        
        # Check if user is already clocked in
        active_entry = self.repository.get_active_time_entry(user_id)
        if active_entry:
            raise ValueError("You are already clocked in. Please clock out first.")
        
        # Validate geofencing if coordinates provided
        if (request.location_lat and request.location_lng and 
            job_site.latitude and job_site.longitude):
            distance = self._calculate_distance(
                request.location_lat, request.location_lng,
                job_site.latitude, job_site.longitude
            )
            if distance > job_site.radius_meters:
                raise ValueError(f"You are too far from the job site. Please move within {job_site.radius_meters} meters.")
        
        # Create time entry
        clock_in_time = datetime.utcnow()
        time_entry = self.repository.create_time_entry(
            user_id=user_id,
            job_site_id=job_site.id,
            clock_in_time=clock_in_time,
            location_lat=request.location_lat,
            location_lng=request.location_lng,
            notes=request.notes
        )
        
        # Create audit log
        self.repository.create_audit_log(
            time_entry_id=time_entry.id,
            action="clock_in",
            old_values={},
            new_values={"clock_in_time": clock_in_time.isoformat()},
            performed_by_id=user_id,
            ip_address=ip_address
        )
        
        # Publish event
        await self.event_bus.publish("timeclock.clocked_in", {
            "time_entry_id": time_entry.id,
            "user_id": user_id,
            "job_site_id": job_site.id,
            "job_site_name": job_site.name,
            "clock_in_time": clock_in_time.isoformat()
        })
        
        return TimeEntry.from_orm(time_entry), f"Successfully clocked in at {job_site.name}"

    async def clock_out(self, request: ClockOutRequest, user_id: str, ip_address: Optional[str] = None) -> Tuple[TimeEntry, str]:
        """Clock out user."""
        # Get time entry
        time_entry = self.repository.get_time_entry(request.time_entry_id)
        if not time_entry:
            raise ValueError("Time entry not found")
        
        if time_entry.user_id != user_id:
            raise ValueError("You can only clock out your own time entries")
        
        if time_entry.clock_out_time:
            raise ValueError("You are already clocked out")
        
        # Validate geofencing if coordinates provided
        job_site = time_entry.job_site
        if (request.location_lat and request.location_lng and 
            job_site.latitude and job_site.longitude):
            distance = self._calculate_distance(
                request.location_lat, request.location_lng,
                job_site.latitude, job_site.longitude
            )
            if distance > job_site.radius_meters:
                raise ValueError(f"You are too far from the job site. Please move within {job_site.radius_meters} meters.")
        
        # Clock out
        clock_out_time = datetime.utcnow()
        updated_entry = self.repository.clock_out(
            time_entry_id=request.time_entry_id,
            clock_out_time=clock_out_time,
            location_lat=request.location_lat,
            location_lng=request.location_lng,
            notes=request.notes
        )
        
        # Create audit log
        self.repository.create_audit_log(
            time_entry_id=time_entry.id,
            action="clock_out",
            old_values={"clock_out_time": None},
            new_values={"clock_out_time": clock_out_time.isoformat(), "total_hours": str(updated_entry.total_hours)},
            performed_by_id=user_id,
            ip_address=ip_address
        )
        
        # Publish event
        await self.event_bus.publish("timeclock.clocked_out", {
            "time_entry_id": updated_entry.id,
            "user_id": user_id,
            "job_site_id": job_site.id,
            "job_site_name": job_site.name,
            "clock_out_time": clock_out_time.isoformat(),
            "total_hours": str(updated_entry.total_hours)
        })
        
        return TimeEntry.from_orm(updated_entry), f"Successfully clocked out from {job_site.name}. Total hours: {updated_entry.total_hours}"

    async def start_break(self, request: BreakRequest, user_id: str) -> Tuple[TimeEntry, str]:
        """Start break."""
        time_entry = self.repository.get_time_entry(request.time_entry_id)
        if not time_entry or time_entry.user_id != user_id:
            raise ValueError("Time entry not found or access denied")
        
        updated_entry = self.repository.start_break(request.time_entry_id)
        if not updated_entry:
            raise ValueError("Cannot start break. You may already be on break or clocked out.")
        
        await self.event_bus.publish("timeclock.break_started", {
            "time_entry_id": updated_entry.id,
            "user_id": user_id,
            "break_start_time": updated_entry.break_start_time.isoformat()
        })
        
        return TimeEntry.from_orm(updated_entry), "Break started"

    async def end_break(self, request: BreakRequest, user_id: str) -> Tuple[TimeEntry, str]:
        """End break."""
        time_entry = self.repository.get_time_entry(request.time_entry_id)
        if not time_entry or time_entry.user_id != user_id:
            raise ValueError("Time entry not found or access denied")
        
        updated_entry = self.repository.end_break(request.time_entry_id)
        if not updated_entry:
            raise ValueError("Cannot end break. You may not be on break.")
        
        await self.event_bus.publish("timeclock.break_ended", {
            "time_entry_id": updated_entry.id,
            "user_id": user_id,
            "break_end_time": updated_entry.break_end_time.isoformat()
        })
        
        return TimeEntry.from_orm(updated_entry), "Break ended"

    # Admin methods
    def get_time_entries(self, user_id: Optional[str] = None, job_site_id: Optional[str] = None,
                        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                        skip: int = 0, limit: int = 100) -> List[TimeEntryWithDetails]:
        """Get time entries with details."""
        entries = self.repository.get_time_entries(user_id, job_site_id, start_date, end_date, skip, limit)
        
        result = []
        for entry in entries:
            result.append(TimeEntryWithDetails(
                **entry.__dict__,
                job_site=JobSite.from_orm(entry.job_site),
                user_name=entry.user.name,
                approved_by_name=entry.approved_by.name if entry.approved_by else None
            ))
        
        return result

    async def approve_time_entry(self, time_entry_id: str, approved: bool, approved_by_id: str) -> Optional[TimeEntry]:
        """Approve or reject time entry."""
        time_entry = self.repository.approve_time_entry(time_entry_id, approved_by_id, approved)
        if not time_entry:
            return None
        
        # Create audit log
        self.repository.create_audit_log(
            time_entry_id=time_entry_id,
            action="approve" if approved else "reject",
            old_values={"is_approved": not approved},
            new_values={"is_approved": approved},
            performed_by_id=approved_by_id
        )
        
        # Publish event
        await self.event_bus.publish("timeclock.time_entry.approved" if approved else "timeclock.time_entry.rejected", {
            "time_entry_id": time_entry_id,
            "approved_by_id": approved_by_id,
            "user_id": time_entry.user_id
        })
        
        return TimeEntry.from_orm(time_entry)

    def get_timeclock_stats(self) -> TimeclockStats:
        """Get timeclock statistics."""
        return self.repository.get_timeclock_stats()

    def get_user_active_time_entry(self, user_id: str) -> Optional[TimeEntry]:
        """Get user's current active time entry."""
        entry = self.repository.get_active_time_entry(user_id)
        return TimeEntry.from_orm(entry) if entry else None
