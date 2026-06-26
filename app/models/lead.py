from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum as SQLEnum,
    DateTime,
    ForeignKey,
    func,
)
from enum import Enum
from app.database import Base


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    NEGOTIATING = "negotiating"
    CLOSED = "closed"
    LOST = "lost"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, index=True)
    client_email = Column(String, index=True)
    client_phone = Column(String)
    listing_id = Column(Integer, ForeignKey("listings.id"), index=True)
    message = Column(Text)
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, index=True)
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
