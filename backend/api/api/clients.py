from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.schema.common import RejectedResponse
from backend.api.schema.leads import LeadCreate, LeadResponse
from backend.api.schema.listings import ListingResponse
from backend.db import get_db
from backend.lib.client import service as client_service

router = APIRouter(prefix="/api/v1/client", tags=["client"])


@router.post("/inquiries", response_model=LeadResponse | RejectedResponse)
def submit_inquiry(lead: LeadCreate, db: Session = Depends(get_db)):
    return client_service.submit_inquiry(db, lead)


@router.get("/listings", response_model=list[ListingResponse])
def get_listings(
    listing_type: str | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return client_service.get_listings(
        db,
        listing_type=listing_type,
        skip=skip,
        limit=limit,
    )


@router.get("/listings/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    return client_service.get_listing(db, listing_id=listing_id)
