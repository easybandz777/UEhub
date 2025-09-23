"""
Timeclock repository - Fully async implementation.
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import JobSite, TimeEntry, TimeEntryAudit
from .schemas import JobSiteCreate, JobSiteUpdate, TimeclockStats


class TimeclockRepository:
    """Repository for timeclock operations - Fully async."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Job Site methods
    async def create_job_site(self, job_site_data: JobSiteCreate, created_by_id: str, qr_code_data: str) -> JobSite:
        """Create a new job site."""
        job_site = JobSite(
            **job_site_data.dict(),
            created_by_id=created_by_id,
            qr_code_data=qr_code_data
        )
        self.db.add(job_site)
        await self.db.commit()
        await self.db.refresh(job_site)
        return job_site

    async def get_job_site(self, job_site_id: str) -> Optional[JobSite]:
        """Get job site by ID."""
        result = await self.db.execute(select(JobSite).where(JobSite.id == job_site_id))
        return result.scalar_one_or_none()

    async def get_job_site_by_qr_code(self, qr_code_data: str) -> Optional[JobSite]:
        """Get job site by QR code data."""
        result = await self.db.execute(
            select(JobSite).where(
                and_(JobSite.qr_code_data == qr_code_data, JobSite.is_active == True)
            )
        )
        return result.scalar_one_or_none()

    async def get_job_sites(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[JobSite]:
        """Get all job sites."""
        query = select(JobSite)
        if active_only:
            query = query.where(JobSite.is_active == True)
        result = await self.db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update_job_site(self, job_site_id: str, job_site_data: JobSiteUpdate) -> Optional[JobSite]:
        """Update job site."""
        job_site = await self.get_job_site(job_site_id)
        if not job_site:
            return None
        
        update_data = job_site_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job_site, field, value)
        
        job_site.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(job_site)
        return job_site

    async def delete_job_site(self, job_site_id: str) -> bool:
        """Soft delete job site."""
        job_site = await self.get_job_site(job_site_id)
        if not job_site:
            return False
        
        job_site.is_active = False
        job_site.updated_at = datetime.utcnow()
        await self.db.commit()
        return True

    # Time Entry methods
    async def create_time_entry(self, user_id: str, job_site_id: str, clock_in_time: datetime,
                         location_lat: Optional[Decimal] = None, location_lng: Optional[Decimal] = None,
                         notes: Optional[str] = None) -> TimeEntry:
        """Create a new time entry (clock in)."""
        time_entry = TimeEntry(
            user_id=user_id,
            job_site_id=job_site_id,
            clock_in_time=clock_in_time,
            clock_in_location_lat=location_lat,
            clock_in_location_lng=location_lng,
            notes=notes
        )
        self.db.add(time_entry)
        await self.db.commit()
        await self.db.refresh(time_entry)
        return time_entry

    async def get_time_entry(self, time_entry_id: str) -> Optional[TimeEntry]:
        """Get time entry by ID."""
        result = await self.db.execute(select(TimeEntry).where(TimeEntry.id == time_entry_id))
        return result.scalar_one_or_none()

    async def get_active_time_entry(self, user_id: str) -> Optional[TimeEntry]:
        """Get user's active time entry (clocked in but not out)."""
        result = await self.db.execute(
            select(TimeEntry).where(
                and_(
                    TimeEntry.user_id == user_id,
                    TimeEntry.clock_out_time.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def clock_out(self, time_entry_id: str, clock_out_time: datetime,
                  location_lat: Optional[Decimal] = None, location_lng: Optional[Decimal] = None,
                  notes: Optional[str] = None) -> Optional[TimeEntry]:
        """Clock out a time entry."""
        time_entry = await self.get_time_entry(time_entry_id)
        if not time_entry or time_entry.clock_out_time:
            return None
        
        time_entry.clock_out_time = clock_out_time
        time_entry.clock_out_location_lat = location_lat
        time_entry.clock_out_location_lng = location_lng
        if notes:
            time_entry.notes = notes
        
        # Calculate total hours
        total_seconds = (clock_out_time - time_entry.clock_in_time).total_seconds()
        
        # Subtract break time if any
        break_seconds = 0
        if time_entry.break_start_time and time_entry.break_end_time:
            break_seconds = (time_entry.break_end_time - time_entry.break_start_time).total_seconds()
        
        time_entry.total_hours = Decimal(str((total_seconds - break_seconds) / 3600))
        time_entry.break_hours = Decimal(str(break_seconds / 3600)) if break_seconds > 0 else None
        time_entry.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(time_entry)
        return time_entry

    async def start_break(self, time_entry_id: str) -> Optional[TimeEntry]:
        """Start break for a time entry."""
        time_entry = await self.get_time_entry(time_entry_id)
        if not time_entry or time_entry.clock_out_time or time_entry.break_start_time:
            return None
        
        time_entry.break_start_time = datetime.utcnow()
        time_entry.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(time_entry)
        return time_entry

    async def end_break(self, time_entry_id: str) -> Optional[TimeEntry]:
        """End break for a time entry."""
        time_entry = await self.get_time_entry(time_entry_id)
        if not time_entry or time_entry.clock_out_time or not time_entry.break_start_time or time_entry.break_end_time:
            return None
        
        time_entry.break_end_time = datetime.utcnow()
        time_entry.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(time_entry)
        return time_entry

    async def get_time_entries(self, user_id: Optional[str] = None, job_site_id: Optional[str] = None,
                        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                        skip: int = 0, limit: int = 100) -> List[TimeEntry]:
        """Get time entries with filters."""
        query = select(TimeEntry).options(
            selectinload(TimeEntry.job_site),
            selectinload(TimeEntry.user)
        )
        
        if user_id:
            query = query.where(TimeEntry.user_id == user_id)
        if job_site_id:
            query = query.where(TimeEntry.job_site_id == job_site_id)
        if start_date:
            query = query.where(TimeEntry.clock_in_time >= start_date)
        if end_date:
            query = query.where(TimeEntry.clock_in_time <= end_date)
        
        result = await self.db.execute(query.order_by(desc(TimeEntry.clock_in_time)).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def approve_time_entry(self, time_entry_id: str, approved_by_id: str, approved: bool) -> Optional[TimeEntry]:
        """Approve or reject a time entry."""
        time_entry = await self.get_time_entry(time_entry_id)
        if not time_entry:
            return None
        
        time_entry.is_approved = approved
        time_entry.approved_by_id = approved_by_id
        time_entry.approved_at = datetime.utcnow()
        time_entry.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(time_entry)
        return time_entry

    async def get_timeclock_stats(self) -> TimeclockStats:
        """Get timeclock statistics."""
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Count employees currently clocked in
        result = await self.db.execute(
            select(func.count(TimeEntry.id)).where(TimeEntry.clock_out_time.is_(None))
        )
        clocked_in_count = result.scalar() or 0
        
        # Count active job sites
        result = await self.db.execute(
            select(func.count(JobSite.id)).where(JobSite.is_active == True)
        )
        active_job_sites = result.scalar() or 0
        
        # Total hours today
        result = await self.db.execute(
            select(func.sum(TimeEntry.total_hours)).where(
                and_(
                    TimeEntry.clock_in_time >= datetime.combine(today, datetime.min.time()),
                    TimeEntry.clock_in_time < datetime.combine(today + timedelta(days=1), datetime.min.time()),
                    TimeEntry.total_hours.isnot(None)
                )
            )
        )
        today_hours = result.scalar() or Decimal('0')
        
        # Total hours this week
        result = await self.db.execute(
            select(func.sum(TimeEntry.total_hours)).where(
                and_(
                    TimeEntry.clock_in_time >= datetime.combine(week_start, datetime.min.time()),
                    TimeEntry.total_hours.isnot(None)
                )
            )
        )
        week_hours = result.scalar() or Decimal('0')
        
        # Pending approvals
        result = await self.db.execute(
            select(func.count(TimeEntry.id)).where(
                and_(
                    TimeEntry.clock_out_time.isnot(None),
                    TimeEntry.is_approved == False
                )
            )
        )
        pending_approvals = result.scalar() or 0
        
        return TimeclockStats(
            total_employees_clocked_in=clocked_in_count,
            total_active_job_sites=active_job_sites,
            total_hours_today=today_hours,
            total_hours_this_week=week_hours,
            pending_approvals=pending_approvals
        )

    # Audit methods
    async def create_audit_log(self, time_entry_id: str, action: str, old_values: dict, new_values: dict,
                        performed_by_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Create audit log entry."""
        audit = TimeEntryAudit(
            time_entry_id=time_entry_id,
            action=action,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            performed_by_id=performed_by_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(audit)
        await self.db.commit()
