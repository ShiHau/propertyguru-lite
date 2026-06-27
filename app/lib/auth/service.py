from datetime import datetime, timezone
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.lib.auth.models import Permission, Principal, ROLE_PERMISSIONS, TokenPayload
from app.lib.auth.utils import as_principal, get_user_by_email, get_user_by_role_and_id
from app.models.user import UserRole


class TokenError(ValueError):
    """Raised when token creation or validation fails."""


_password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthenticationService:

    @staticmethod
    def hash_password(password: str) -> str:
        return _password_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return _password_context.verify(password, hashed_password)

    @staticmethod
    def build_subject(role: UserRole, user_id: int) -> str:
        return f"{role.value}:{user_id}"

    @staticmethod
    def parse_subject(subject: str) -> tuple[UserRole, int]:
        role_value, user_id = subject.split(":", maxsplit=1)
        return UserRole(role_value), int(user_id)

    @classmethod
    def create_access_token(
        cls,
        user_id: int,
        role: UserRole,
    ) -> str:
        payload = {
            "sub": cls.build_subject(role=role, user_id=user_id),
            "role": role.value,
            "jti": str(uuid4()),
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @classmethod
    def decode_access_token(cls, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError as exc:
            raise TokenError("Invalid token") from exc

        if payload.get("type") != "access":
            raise TokenError("Unsupported token type")

        subject = payload.get("sub")
        role_value = payload.get("role")
        jti = payload.get("jti")
        if not subject or not role_value or not jti:
            raise TokenError("Token payload missing required claims")

        try:
            role, user_id = cls.parse_subject(subject)
        except (ValueError, TypeError) as exc:
            raise TokenError("Invalid token subject") from exc

        if role.value != role_value:
            raise TokenError("Role claim does not match token subject")

        return TokenPayload(subject=subject, role=role, user_id=user_id)

    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str) -> Principal | None:
        user = get_user_by_email(db, email)
        if not user:
            return None

        if not cls.verify_password(password, user.hashed_password):
            return None

        return as_principal(user)

    @classmethod
    def get_principal_by_subject(cls, db: Session, subject: str) -> Principal | None:
        try:
            role, user_id = cls.parse_subject(subject)
        except (ValueError, TypeError):
            return None

        user = get_user_by_role_and_id(db, role, user_id)
        if not user:
            return None

        return as_principal(user)


class AuthorizationService:

    Permission = Permission
    ROLE_PERMISSIONS = ROLE_PERMISSIONS

    @staticmethod
    def has_permissions(role: UserRole, required: set[Permission]) -> bool:
        granted = ROLE_PERMISSIONS.get(role, set())
        return required.issubset(granted)
