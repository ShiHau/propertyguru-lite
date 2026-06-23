from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import (
    LeadResponse,
    LeadDetailResponse,
    LeadNoteCreate,
    LeadUpdate,
)

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


@router.get("/inquiries", response_model=list[LeadResponse])
def get_inquiries(
    status_filter: str | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Agent endpoint: View all inquiries with optional filtering by status.
    """
    query = db.query(Lead)

    if status_filter:
        query = query.filter(Lead.status == status_filter)

    inquiries = query.offset(skip).limit(limit).all()
    return inquiries


@router.get("/inquiries/{inquiry_id}", response_model=LeadDetailResponse)
def get_inquiry_detail(inquiry_id: int, db: Session = Depends(get_db)):
    """
    Agent endpoint: Get detailed information about an inquiry.
    """
    inquiry = db.query(Lead).filter(Lead.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return inquiry


@router.patch("/inquiries/{inquiry_id}", response_model=LeadResponse)
def update_inquiry(
    inquiry_id: int, update_data: LeadUpdate, db: Session = Depends(get_db)
):
    """
    Agent endpoint: Update inquiry status and/or notes.
    """
    inquiry = db.query(Lead).filter(Lead.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    if update_data.status:
        inquiry.status = update_data.status
    if update_data.notes:
        inquiry.notes = update_data.notes
    if update_data.assigned_agent_id:
        inquiry.assigned_agent_id = update_data.assigned_agent_id

    db.commit()
    db.refresh(inquiry)
    return inquiry


@router.post("/inquiries/{inquiry_id}/notes")
def add_notes(inquiry_id: int, notes: LeadNoteCreate, db: Session = Depends(get_db)):
    """
    Agent endpoint: Add notes to an inquiry.
    """
    inquiry = db.query(Lead).filter(Lead.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    inquiry.notes += "\n" + notes.note
    db.commit()
    db.refresh(inquiry)
    return {"message": "Notes added", "inquiry": inquiry}
