from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.lead import LeadCreate, LeadResponse
from app.models.lead import Lead
from app.schemas.listing import ListingResponse
from app.models.listing import Listing

router = APIRouter(prefix="/api/v1/client", tags=["client"])


@router.post("/inquiries", response_model=LeadResponse)
def submit_inquiry(lead: LeadCreate, db: Session = Depends(get_db)):
    """
    Public endpoint: Client submits an inquiry (no authentication required).
    Anyone can submit a lead form.
    """
    listing = (
        db.query(Listing)
        .filter(Listing.id == lead.listing_id, Listing.is_active == 1)
        .first()
    )
    if not listing:
        raise HTTPException(status_code=400, detail="Invalid listing_id")

    db_lead = Lead(
        client_name=lead.client_name,
        client_email=lead.client_email,
        client_phone=lead.client_phone,
        listing_id=lead.listing_id,
        message=lead.message,
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("/listings", response_model=list[ListingResponse])
def get_listings(
    listing_type: str | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Public endpoint: View available listings.
    """
    query = db.query(Listing).filter(Listing.is_active == 1)

    if listing_type:
        query = query.filter(Listing.listing_type == listing_type)

    listings = query.offset(skip).limit(limit).all()
    return listings


@router.get("/listings/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """
    Public endpoint: Get details of a specific listing.
    """
    listing = (
        db.query(Listing)
        .filter(Listing.id == listing_id, Listing.is_active == 1)
        .first()
    )
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing
