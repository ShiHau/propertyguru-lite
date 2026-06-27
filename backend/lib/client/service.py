from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.lib.assignment import get_next_assigned_agent_id
from backend.lib.validation import get_duplicate_lead_reason
from backend.models.lead import Lead
from backend.models.listing import Listing
from backend.api.schema.leads import LeadCreate


def submit_inquiry(db: Session, lead: LeadCreate):
    listing = (
        db.query(Listing)
        .filter(Listing.id == lead.listing_id, Listing.is_active == 1)
        .first()
    )
    if not listing:
        raise HTTPException(status_code=400, detail="Invalid listing_id")

    duplicate_reason = get_duplicate_lead_reason(
        db,
        lead.client_email,
        lead.client_phone,
        lead.listing_id,
    )
    if duplicate_reason:
        return {
            "status": "rejected",
            "reason": duplicate_reason,
            "message": "Request rejected",
        }

    assigned_agent_id = get_next_assigned_agent_id(db)

    db_lead = Lead(
        client_name=lead.client_name,
        client_email=lead.client_email,
        client_phone=lead.client_phone,
        listing_id=lead.listing_id,
        message=lead.message,
        assigned_agent_id=assigned_agent_id,
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def get_listings(
    db: Session,
    listing_type: str | None = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(Listing).filter(Listing.is_active == 1)
    if listing_type:
        query = query.filter(Listing.listing_type == listing_type)
    return query.offset(skip).limit(limit).all()


def get_listing(db: Session, listing_id: int):
    listing = (
        db.query(Listing)
        .filter(Listing.id == listing_id, Listing.is_active == 1)
        .first()
    )
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing
