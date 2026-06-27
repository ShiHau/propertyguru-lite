from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ListingCreate(BaseModel):
    title: str
    description: str
    address: str
    price: float
    bedrooms: int
    bathrooms: int
    square_feet: Optional[float] = None
    listing_type: str


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    square_feet: Optional[float] = None
    listing_type: Optional[str] = None
    is_active: Optional[bool] = None


class ListingResponse(BaseModel):
    id: int
    title: str
    description: str
    address: str
    price: float
    bedrooms: int
    bathrooms: int
    square_feet: Optional[float]
    listing_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
