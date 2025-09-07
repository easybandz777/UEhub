"""
OSHA Safety Checklist schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class SafetyChecklistItemBase(BaseModel):
    """Base safety checklist item schema."""
    item_id: str = Field(..., min_length=1, max_length=10)
    category: str = Field(..., min_length=1, max_length=100)
    number: str = Field(..., min_length=1, max_length=10)
    text: str = Field(..., min_length=1)
    is_critical: bool = False
    status: Optional[str] = Field(None, pattern="^(pass|fail|na)$")
    notes: Optional[str] = None


class SafetyChecklistItemCreate(SafetyChecklistItemBase):
    """Safety checklist item creation schema."""
    pass


class SafetyChecklistItemUpdate(BaseModel):
    """Safety checklist item update schema."""
    status: Optional[str] = Field(None, pattern="^(pass|fail|na)$")
    notes: Optional[str] = None


class SafetyChecklistItemResponse(SafetyChecklistItemBase):
    """Safety checklist item response schema."""
    id: str
    checklist_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SafetyChecklistBase(BaseModel):
    """Base safety checklist schema."""
    project_name: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    inspection_date: datetime
    scaffold_type: str = Field(..., min_length=1, max_length=100)
    height: str = Field(..., min_length=1, max_length=50)
    contractor: Optional[str] = Field(None, max_length=200)
    permit_number: Optional[str] = Field(None, max_length=100)


class SafetyChecklistCreate(SafetyChecklistBase):
    """Safety checklist creation schema."""
    checklist_items: List[SafetyChecklistItemCreate] = []


class SafetyChecklistUpdate(BaseModel):
    """Safety checklist update schema."""
    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    inspection_date: Optional[datetime] = None
    scaffold_type: Optional[str] = Field(None, min_length=1, max_length=100)
    height: Optional[str] = Field(None, min_length=1, max_length=50)
    contractor: Optional[str] = Field(None, max_length=200)
    permit_number: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(draft|completed|approved)$")


class SafetyChecklistResponse(SafetyChecklistBase):
    """Safety checklist response schema."""
    id: str
    inspector_id: str
    status: str
    total_items: int
    passed_items: int
    failed_items: int
    na_items: int
    critical_failures: int
    approved_by_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    checklist_items: List[SafetyChecklistItemResponse] = []
    
    class Config:
        from_attributes = True


class SafetyChecklistListResponse(BaseModel):
    """Safety checklist list response schema."""
    items: List[SafetyChecklistResponse]
    total: int
    page: int
    per_page: int
    pages: int


class SafetyChecklistStats(BaseModel):
    """Safety checklist statistics schema."""
    total_checklists: int
    completed_checklists: int
    approved_checklists: int
    pending_approval: int
    critical_failures_count: int
    average_completion_rate: float
    checklists_this_month: int
    checklists_this_week: int


class SafetyTemplateBase(BaseModel):
    """Base safety template schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    version: str = Field(..., min_length=1, max_length=20)
    template_data: dict


class SafetyTemplateCreate(SafetyTemplateBase):
    """Safety template creation schema."""
    pass


class SafetyTemplateUpdate(BaseModel):
    """Safety template update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    version: Optional[str] = Field(None, min_length=1, max_length=20)
    template_data: Optional[dict] = None
    is_active: Optional[bool] = None


class SafetyTemplateResponse(SafetyTemplateBase):
    """Safety template response schema."""
    id: str
    is_active: bool
    created_by_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SafetyReportRequest(BaseModel):
    """Safety report request schema."""
    checklist_id: str
    format: str = Field(..., pattern="^(pdf|excel|json)$")
    include_photos: bool = False
    include_notes: bool = True


class SafetyReportResponse(BaseModel):
    """Safety report response schema."""
    report_id: str
    download_url: str
    expires_at: datetime
    format: str
    file_size: int


class SafetyDashboardData(BaseModel):
    """Safety dashboard data schema."""
    stats: SafetyChecklistStats
    recent_checklists: List[SafetyChecklistResponse]
    pending_approvals: List[SafetyChecklistResponse]
    critical_failures: List[SafetyChecklistResponse]
    completion_trend: List[dict]  # Time series data


class BulkItemUpdate(BaseModel):
    """Bulk checklist item update schema."""
    item_updates: List[dict] = Field(..., description="List of {item_id: str, status: str, notes: str}")


class ChecklistApproval(BaseModel):
    """Checklist approval schema."""
    approved: bool
    comments: Optional[str] = None
