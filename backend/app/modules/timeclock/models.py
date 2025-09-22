"""
Timeclock models.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ...core.db import Base


class JobSite(Base):
    """Job site model for QR code generation."""
    
    __tablename__ = "timeclock_job_site"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(Text)
    latitude = Column(Numeric(10, 8))  # For geofencing
    longitude = Column(Numeric(11, 8))  # For geofencing
    radius_meters = Column(Integer, default=100)  # Geofence radius
    qr_code_data = Column(String(500), unique=True, nullable=False)  # QR code content
    is_active = Column(Boolean, default=True)
    created_by_id = Column(String, ForeignKey("auth_user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    time_entries = relationship("TimeEntry", back_populates="job_site")
    created_by = relationship("User", foreign_keys=[created_by_id])


class TimeEntry(Base):
    """Time entry model for clock in/out records."""
    
    __tablename__ = "timeclock_time_entry"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("auth_user.id"), nullable=False)
    job_site_id = Column(String, ForeignKey("timeclock_job_site.id"), nullable=False)
    clock_in_time = Column(DateTime, nullable=False)
    clock_out_time = Column(DateTime)
    break_start_time = Column(DateTime)
    break_end_time = Column(DateTime)
    total_hours = Column(Numeric(5, 2))  # Calculated field
    break_hours = Column(Numeric(5, 2))  # Calculated field
    notes = Column(Text)
    clock_in_location_lat = Column(Numeric(10, 8))
    clock_in_location_lng = Column(Numeric(11, 8))
    clock_out_location_lat = Column(Numeric(10, 8))
    clock_out_location_lng = Column(Numeric(11, 8))
    is_approved = Column(Boolean, default=False)
    approved_by_id = Column(String, ForeignKey("auth_user.id"))
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    job_site = relationship("JobSite", back_populates="time_entries")
    approved_by = relationship("User", foreign_keys=[approved_by_id])


class TimeEntryAudit(Base):
    """Audit log for time entry changes."""
    
    __tablename__ = "timeclock_time_entry_audit"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    time_entry_id = Column(String, ForeignKey("timeclock_time_entry.id"), nullable=False)
    action = Column(String(50), nullable=False)  # clock_in, clock_out, edit, approve
    old_values = Column(Text)  # JSON string of old values
    new_values = Column(Text)  # JSON string of new values
    performed_by_id = Column(String, ForeignKey("auth_user.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Relationships
    time_entry = relationship("TimeEntry")
    performed_by = relationship("User")
