from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.listing import Listing
from app.models.lead import Lead
from app.business.validation import get_duplicate_listing_reason, get_duplicate_user_reason
from app.schemas.common import RejectedResponse
from app.schemas.user import UserCreate, UserResponse, AdminUserUpdate
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from app.schemas.lead import LeadResponse, LeadDetailResponse

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# =====================
# User Management
# =====================


@router.get("/users", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Admin endpoint: List all users (agents, admins).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/users", response_model=UserResponse | RejectedResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Admin endpoint: Create a new user (agent or admin).
    """
    duplicate_reason = get_duplicate_user_reason(db, user_data.email)
    if duplicate_reason:
        return {
            "status": "rejected",
            "reason": duplicate_reason,
            "message": "Request rejected",
        }

    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=user_data.password,  # Dev only: not hashed for simplicity
        role=user_data.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch("/users/{user_id}", response_model=UserResponse | RejectedResponse)
def update_user(user_id: int, update_data: AdminUserUpdate, db: Session = Depends(get_db)):
    """
    Admin endpoint: Update any user's information.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.email:
        duplicate_reason = get_duplicate_user_reason(
            db, update_data.email, exclude_user_id=user.id
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
        user.hashed_password = update_data.password  # Dev only
    if update_data.role is not None:
        user.role = update_data.role
    if update_data.is_active is not None:
        user.is_active = 1 if update_data.is_active else 0

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Admin endpoint: Deactivate a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = 0
    db.commit()
    return {"message": "User deactivated"}


# =====================
# Listing Management
# =====================


@router.get("/listings", response_model=list[ListingResponse])
def get_all_listings(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Admin endpoint: View all listings (including inactive).
    """
    listings = db.query(Listing).offset(skip).limit(limit).all()
    return listings


@router.post("/listings", response_model=ListingResponse | RejectedResponse)
def create_listing(listing_data: ListingCreate, db: Session = Depends(get_db)):
    """
    Admin endpoint: Create a new listing.
    """
    duplicate_reason = get_duplicate_listing_reason(db, listing_data.address)
    if duplicate_reason:
        return {
            "status": "rejected",
            "reason": duplicate_reason,
            "message": "Request rejected",
        }
    db_listing = Listing(**listing_data.model_dump())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


@router.patch("/listings/{listing_id}", response_model=ListingResponse | RejectedResponse)
def update_listing(
    listing_id: int, update_data: ListingUpdate, db: Session = Depends(get_db)
):
    """
    Admin endpoint: Update listing information.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if update_data.address:
        duplicate_reason = get_duplicate_listing_reason(
            db, update_data.address, exclude_listing_id=listing.id
        )
        if duplicate_reason:
            return {
                "status": "rejected",
                "reason": duplicate_reason,
                "message": "Request rejected",
            }

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(listing, key, value)

    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    """
    Admin endpoint: Deactivate a listing.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing.is_active = 0
    db.commit()
    return {"message": "Listing deactivated"}


# =====================
# Inquiry Management
# =====================


@router.get("/inquiries", response_model=list[LeadResponse])
def get_all_inquiries(
    status_filter: str | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Admin endpoint: View all inquiries with optional filtering by status.
    """
    query = db.query(Lead)

    if status_filter:
        query = query.filter(Lead.status == status_filter)

    inquiries = query.offset(skip).limit(limit).all()
    return inquiries


@router.get("/inquiries/{inquiry_id}", response_model=LeadDetailResponse)
def get_inquiry_detail(inquiry_id: int, db: Session = Depends(get_db)):
    """
    Admin endpoint: Get detailed information about any inquiry.
    """
    inquiry = db.query(Lead).filter(Lead.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return inquiry


# =====================
# Dashboard / Analytics
# =====================


@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Admin endpoint: Get basic dashboard statistics.
    """
    total_leads = db.query(Lead).count()
    total_listings = db.query(Listing).filter(Listing.is_active == 1).count()
    total_agents = db.query(User).filter(User.role == UserRole.AGENT).count()

    return {
        "total_leads": total_leads,
        "total_listings": total_listings,
        "total_agents": total_agents,
    }
