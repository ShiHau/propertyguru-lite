from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from backend.models.lead import LeadStatus


class LeadCreate(BaseModel):
    client_name: str
    client_email: EmailStr
    client_phone: str
    listing_id: int
    message: str


class LeadUpdate(BaseModel):
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
    message: str
