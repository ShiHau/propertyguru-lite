from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.schema.common import RejectedResponse
from backend.api.schema.leads import LeadDetailResponse, LeadNoteCreate, LeadResponse, LeadUpdate
from backend.api.schema.users import AgentUserUpdate, UserResponse
from backend.api.security import require_agent_principal
from backend.db import get_db
from backend.lib.agent import service as agent_service
from backend.lib.auth import Principal

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


@router.get("/inquiries", response_model=list[LeadResponse])
def get_inquiries(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    return agent_service.get_inquiries(db, principal=principal, skip=skip, limit=limit)


@router.get("/inquiries/{inquiry_id}", response_model=LeadDetailResponse)
def get_inquiry_detail(
    inquiry_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    return agent_service.get_inquiry_detail(db, principal=principal, inquiry_id=inquiry_id)


@router.patch("/users/me", response_model=UserResponse | RejectedResponse)
def update_my_profile(
    update_data: AgentUserUpdate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    return agent_service.update_my_profile(db, principal=principal, update_data=update_data)


@router.patch("/inquiries/{inquiry_id}", response_model=LeadResponse)
def update_inquiry(
    inquiry_id: int,
    update_data: LeadUpdate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    return agent_service.update_inquiry(
        db,
        principal=principal,
        inquiry_id=inquiry_id,
        update_data=update_data,
    )


@router.post("/inquiries/{inquiry_id}/notes")
def add_notes(
    inquiry_id: int,
    notes: LeadNoteCreate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_agent_principal),
):
    return agent_service.add_notes(db, principal=principal, inquiry_id=inquiry_id, notes=notes)
