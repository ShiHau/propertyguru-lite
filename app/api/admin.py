from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.listing import Listing
from app.models.lead import Lead
from app.schemas.user import UserCreate, UserResponse
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse

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


@router.post("/users", response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Admin endpoint: Create a new user (agent or admin).
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

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


@router.post("/listings", response_model=ListingResponse)
def create_listing(listing_data: ListingCreate, db: Session = Depends(get_db)):
    """
    Admin endpoint: Create a new listing.
    """
    db_listing = Listing(**listing_data.model_dump())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


@router.patch("/listings/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: int, update_data: ListingUpdate, db: Session = Depends(get_db)
):
    """
    Admin endpoint: Update listing information.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

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
