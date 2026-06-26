from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.listing import Listing
from app.models.user import User


def _normalize_text(value: str) -> str:
    return value.strip().lower()


def get_duplicate_user_reason(
    db: Session, email: str, exclude_user_id: int | None = None
) -> str | None:
    normalized_email = _normalize_text(email)
    query = db.query(User).filter(func.lower(User.email) == normalized_email)
    # Prevents user getting flagged when updating their own email
    if exclude_user_id is not None:
        query = query.filter(User.id != exclude_user_id)
    existing_user = query.first()

    if existing_user:
        return "User with this email already exists"
    return None


def get_duplicate_listing_reason(
    db: Session, address: str, exclude_listing_id: int | None = None
) -> str | None:
    normalized_address = _normalize_text(address)
    query = db.query(Listing).filter(func.lower(Listing.address) == normalized_address)
    # Prevents listing getting flagged when updating its own address
    if exclude_listing_id is not None:
        query = query.filter(Listing.id != exclude_listing_id)
    existing_listing = query.first()

    if existing_listing:
        return "Listing with this address already exists"
    return None


def get_duplicate_lead_reason(
    db: Session, client_email: str, client_phone: str, listing_id: int
) -> str | None:
    normalized_email = _normalize_text(client_email)
    normalized_phone = client_phone.strip()
    existing_lead = (
        db.query(Lead)
        .filter(
            func.lower(Lead.client_email) == normalized_email,
            Lead.client_phone == normalized_phone,
            Lead.listing_id == listing_id,
        )
        .first()
    )

    if existing_lead:
        return "Duplicate lead is not allowed for this client and listing"
    return None