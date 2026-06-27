from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.lib.auth import AuthenticationService, Principal
from backend.lib.validation import get_duplicate_user_reason
from backend.models.lead import Lead
from backend.models.user import Agent, UserRole
from backend.api.schema.leads import LeadNoteCreate, LeadUpdate
from backend.api.schema.users import AgentUserUpdate


def _validate_agent(user_id: int, db: Session) -> None:
    agent = db.query(Agent).filter(Agent.id == user_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")


def get_inquiries(db: Session, principal: Principal, skip: int = 0, limit: int = 10):
    _validate_agent(principal.user_id, db)
    query = db.query(Lead).filter(Lead.assigned_agent_id == principal.user_id)
    return query.offset(skip).limit(limit).all()


def get_inquiry_detail(db: Session, principal: Principal, inquiry_id: int):
    _validate_agent(principal.user_id, db)
    inquiry = (
        db.query(Lead)
        .filter(Lead.id == inquiry_id, Lead.assigned_agent_id == principal.user_id)
        .first()
    )
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return inquiry


def update_my_profile(db: Session, principal: Principal, update_data: AgentUserUpdate):
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


def update_inquiry(db: Session, principal: Principal, inquiry_id: int, update_data: LeadUpdate):
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


def add_notes(db: Session, principal: Principal, inquiry_id: int, notes: LeadNoteCreate):
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
