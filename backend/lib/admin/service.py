from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.lib.auth import AuthenticationService
from backend.lib.validation import (
    get_duplicate_listing_reason,
    get_duplicate_user_reason,
)
from backend.models.lead import Lead
from backend.models.listing import Listing
from backend.models.user import Admin, Agent, UserRole
from backend.api.schema.listings import ListingCreate, ListingUpdate
from backend.api.schema.users import AdminUserUpdate, UserCreate


def get_users(db: Session, skip: int = 0, limit: int = 10):
    agents = db.query(Agent).all()
    admins = db.query(Admin).all()
    users = agents + admins
    users.sort(key=lambda user: user.id)
    return users[skip : skip + limit]


def create_user(db: Session, user_data: UserCreate):
    duplicate_reason = get_duplicate_user_reason(db, user_data.email)
    if duplicate_reason:
        return {
            "status": "rejected",
            "reason": duplicate_reason,
            "message": "Request rejected",
        }

    if user_data.role == UserRole.AGENT:
        db_user = Agent(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=AuthenticationService.hash_password(user_data.password),
            role=UserRole.AGENT,
        )
    elif user_data.role == UserRole.ADMIN:
        db_user = Admin(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=AuthenticationService.hash_password(user_data.password),
            role=UserRole.ADMIN,
        )
    else:
        return {
            "status": "rejected",
            "reason": "Only agent and admin roles are supported",
            "message": "Request rejected",
        }

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, user_id: int, role: UserRole, update_data: AdminUserUpdate
):
    if role == UserRole.AGENT:
        user = db.query(Agent).filter(Agent.id == user_id).first()
    elif role == UserRole.ADMIN:
        user = db.query(Admin).filter(Admin.id == user_id).first()
    else:
        return {
            "status": "rejected",
            "reason": "Only agent and admin roles are supported",
            "message": "Request rejected",
        }

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.email:
        duplicate_reason = get_duplicate_user_reason(
            db,
            update_data.email,
            exclude_user_id=user.id,
            exclude_role=role,
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


def delete_user(db: Session, user_id: int, role: UserRole):
    if role == UserRole.AGENT:
        user = db.query(Agent).filter(Agent.id == user_id).first()
    elif role == UserRole.ADMIN:
        user = db.query(Admin).filter(Admin.id == user_id).first()
    else:
        return {
            "status": "rejected",
            "reason": "Only agent and admin roles are supported",
            "message": "Request rejected",
        }

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = 0
    db.commit()
    return {"message": "User deactivated"}


def get_all_listings(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Listing).offset(skip).limit(limit).all()


def create_listing(db: Session, listing_data: ListingCreate):
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


def update_listing(db: Session, listing_id: int, update_data: ListingUpdate):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if update_data.address:
        duplicate_reason = get_duplicate_listing_reason(
            db,
            update_data.address,
            exclude_listing_id=listing.id,
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


def delete_listing(db: Session, listing_id: int):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing.is_active = 0
    db.commit()
    return {"message": "Listing deactivated"}


def get_all_inquiries(
    db: Session,
    status_filter: str | None = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(Lead)
    if status_filter:
        query = query.filter(Lead.status == status_filter)
    return query.offset(skip).limit(limit).all()


def get_inquiry_detail(db: Session, inquiry_id: int):
    inquiry = db.query(Lead).filter(Lead.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return inquiry


def get_dashboard_stats(db: Session):
    total_leads = db.query(Lead).count()
    total_listings = db.query(Listing).filter(Listing.is_active == 1).count()
    total_agents = db.query(Agent).count()
    return {
        "total_leads": total_leads,
        "total_listings": total_listings,
        "total_agents": total_agents,
    }
