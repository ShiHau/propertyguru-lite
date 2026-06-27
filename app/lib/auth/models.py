from dataclasses import dataclass
from enum import StrEnum

from app.models.user import UserRole


@dataclass(frozen=True)
class Principal:
    user_id: int
    role: UserRole
    email: str
    full_name: str
    is_active: bool


@dataclass(frozen=True)
class TokenPayload:
    subject: str
    role: UserRole
    user_id: int


class Permission(StrEnum):
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    LISTINGS_READ = "listings:read"
    LISTINGS_WRITE = "listings:write"
    INQUIRIES_READ_ALL = "inquiries:read_all"
    INQUIRIES_READ_OWN = "inquiries:read_own"
    INQUIRIES_WRITE = "inquiries:write"
    DASHBOARD_READ = "dashboard:read"
    PROFILE_WRITE_OWN = "profile:write_own"


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.ADMIN: {
        Permission.USERS_READ,
        Permission.USERS_WRITE,
        Permission.LISTINGS_READ,
        Permission.LISTINGS_WRITE,
        Permission.INQUIRIES_READ_ALL,
        Permission.DASHBOARD_READ,
    },
    UserRole.AGENT: {
        Permission.INQUIRIES_READ_OWN,
        Permission.INQUIRIES_WRITE,
        Permission.PROFILE_WRITE_OWN,
    },
}
