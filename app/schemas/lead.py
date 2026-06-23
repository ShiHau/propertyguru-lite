from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.lead import LeadStatus
from datetime import datetime


class LeadCreate(BaseModel):
    """Public: Client submitting inquiry"""

    client_name: str
    client_email: EmailStr
    client_phone: str
    listing_id: int
    message: str


class LeadUpdate(BaseModel):
    """Agent: Update lead status and notes"""

    status: Optional[LeadStatus] = None
    notes: Optional[str] = None
    assigned_agent_id: Optional[int] = None


class LeadNoteCreate(BaseModel):
    note: str


class LeadResponse(BaseModel):
    id: int
    client_name: str
    client_email: str
    client_phone: str
    listing_id: int
    status: LeadStatus
    assigned_agent_id: Optional[int]
    notes: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadDetailResponse(LeadResponse):
    """Full lead details including message"""

    message: str
