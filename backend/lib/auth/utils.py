from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.lib.auth.models import Principal
from backend.models.user import Admin, Agent, UserRole


def get_user_by_role_and_id(db: Session, role: UserRole, user_id: int):
    if role == UserRole.ADMIN:
        return db.query(Admin).filter(Admin.id == user_id).first()
    if role == UserRole.AGENT:
        return db.query(Agent).filter(Agent.id == user_id).first()
    return None


def get_user_by_email(db: Session, email: str):
    normalized_email = email.strip().lower()

    admin = db.query(Admin).filter(func.lower(Admin.email) == normalized_email).first()
    if admin:
        return admin

    agent = db.query(Agent).filter(func.lower(Agent.email) == normalized_email).first()
    if agent:
        return agent

    return None


def as_principal(user) -> Principal:
    return Principal(
        user_id=user.id,
        role=user.role,
        email=user.email,
        full_name=user.full_name,
        is_active=bool(user.is_active),
    )
