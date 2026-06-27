from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.schema.common import RejectedResponse
from backend.api.schema.leads import LeadDetailResponse, LeadResponse
from backend.api.schema.listings import ListingCreate, ListingResponse, ListingUpdate
from backend.api.schema.users import AdminUserUpdate, UserCreate, UserResponse
from backend.api.security import require_admin_principal
from backend.db import get_db
from backend.lib.admin import service as admin_service
from backend.models.user import UserRole

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_principal)],
)


@router.get("/users", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return admin_service.get_users(db, skip=skip, limit=limit)


@router.post("/users", response_model=UserResponse | RejectedResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return admin_service.create_user(db, user_data)


@router.patch("/users/{user_id}", response_model=UserResponse | RejectedResponse)
def update_user(
    user_id: int,
    update_data: AdminUserUpdate,
    role: UserRole,
    db: Session = Depends(get_db),
):
    return admin_service.update_user(db, user_id=user_id, role=role, update_data=update_data)


@router.delete("/users/{user_id}")
def delete_user(user_id: int, role: UserRole, db: Session = Depends(get_db)):
    return admin_service.delete_user(db, user_id=user_id, role=role)


@router.get("/listings", response_model=list[ListingResponse])
def get_all_listings(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return admin_service.get_all_listings(db, skip=skip, limit=limit)


@router.post("/listings", response_model=ListingResponse | RejectedResponse)
def create_listing(listing_data: ListingCreate, db: Session = Depends(get_db)):
    return admin_service.create_listing(db, listing_data)


@router.patch("/listings/{listing_id}", response_model=ListingResponse | RejectedResponse)
def update_listing(
    listing_id: int,
    update_data: ListingUpdate,
    db: Session = Depends(get_db),
):
    return admin_service.update_listing(db, listing_id=listing_id, update_data=update_data)


@router.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    return admin_service.delete_listing(db, listing_id=listing_id)


@router.get("/inquiries", response_model=list[LeadResponse])
def get_all_inquiries(
    status_filter: str | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return admin_service.get_all_inquiries(
        db,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )


@router.get("/inquiries/{inquiry_id}", response_model=LeadDetailResponse)
def get_inquiry_detail(inquiry_id: int, db: Session = Depends(get_db)):
    return admin_service.get_inquiry_detail(db, inquiry_id=inquiry_id)


@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return admin_service.get_dashboard_stats(db)
