from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func
from app.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    address = Column(String, index=True)
    price = Column(Float)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    square_feet = Column(Float, nullable=True)
    listing_type = Column(String)  # "rent" or "sale"
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
