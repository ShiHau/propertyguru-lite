from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.security import require_agent_principal
from app.lib.auth import AuthenticationService
from app.models.lead import Lead
from app.models.user import Agent, UserRole
from app.lib.auth import Principal
from app.lib.validation import get_duplicate_user_reason
from app.schemas.common import RejectedResponse
from app.schemas.lead import (
    LeadResponse,
    LeadDetailResponse,
    LeadNoteCreate,
    LeadUpdate,
)
from app.schemas.user import AgentUserUpdate, UserResponse

router = APIRouter(
    prefix="/api/v1/agent",
    tags=["agent"],
)


def _validate_agent(user_id: int, db: Session) -> None:
    agent = db.query(Agent).filter(Agent.id == user_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/inquiries", response_model=list[LeadResponse])
def get_inquiries(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    """
    Agent endpoint: View inquiries assigned to this agent with optional filtering by status.
    """
    _validate_agent(principal.user_id, db)
    query = db.query(Lead).filter(Lead.assigned_agent_id == principal.user_id)

    inquiries = query.offset(skip).limit(limit).all()
    return inquiries


@router.get("/inquiries/{inquiry_id}", response_model=LeadDetailResponse)
def get_inquiry_detail(
    inquiry_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    """
    Agent endpoint: Get detailed information about an inquiry assigned to this agent.
    """
    _validate_agent(principal.user_id, db)
    inquiry = (
        db.query(Lead)
        .filter(Lead.id == inquiry_id, Lead.assigned_agent_id == principal.user_id)
        .first()
    )
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return inquiry


@router.patch("/users/me", response_model=UserResponse | RejectedResponse)
def update_my_profile(
    update_data: AgentUserUpdate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    """
    Agent endpoint: Update own user profile information.
    """
    _validate_agent(principal.user_id, db)
    user = db.query(Agent).filter(Agent.id == principal.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.email:
        duplicate_reason = get_duplicate_user_reason(
            db,
            update_data.email,
            exclude_user_id=user.id,
            exclude_role=UserRole.AGENT,
        )
        if duplicate_reason:
            return {
                "status": "rejected",
                "reason": duplicate_reason,
                "message": "Request rejected",
            }
        user.email = update_data.email

    if update_data.full_name:
        user.full_name = update_data.full_name
    if update_data.password:
        user.hashed_password = AuthenticationService.hash_password(update_data.password)
    if update_data.is_active is not None:
        user.is_active = 1 if update_data.is_active else 0

    db.commit()
    db.refresh(user)
    return user


@router.patch("/inquiries/{inquiry_id}", response_model=LeadResponse)
def update_inquiry(
    inquiry_id: int,
    update_data: LeadUpdate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    """
    Agent endpoint: Update inquiry status and/or notes.
    """
    inquiry = (
        db.query(Lead)
        .filter(Lead.id == inquiry_id, Lead.assigned_agent_id == principal.user_id)
        .first()
    )
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
def add_notes(
    inquiry_id: int,
    notes: LeadNoteCreate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    """
    Agent endpoint: Add notes to an inquiry.
    """
    inquiry = (
        db.query(Lead)
        .filter(Lead.id == inquiry_id, Lead.assigned_agent_id == principal.user_id)
        .first()
    )
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    inquiry.notes += "\n" + notes.note
    db.commit()
    db.refresh(inquiry)
    return {"message": "Notes added", "inquiry": inquiry}
