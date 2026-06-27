from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.lib.auth import (
    AuthenticationService,
    AuthorizationService,
    Permission,
    Principal,
    TokenError,
)
from app.models.user import UserRole

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_principal(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Principal:
    token = credentials.credentials

    try:
        payload = AuthenticationService.decode_access_token(token)
    except TokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token") from exc

    principal = AuthenticationService.get_principal_by_subject(db, payload.subject)
    if not principal:
        raise HTTPException(status_code=401, detail="Authenticated user not found")

    return principal


def require_role(required_role: UserRole):
    def _role_guard(principal: Principal = Depends(get_current_principal)) -> Principal:
        if principal.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return principal

    return _role_guard


def require_permissions(required_permissions: set[Permission]):
    def _permission_guard(
        principal: Principal = Depends(get_current_principal),
    ) -> Principal:
        if not AuthorizationService.has_permissions(
            principal.role,
            required_permissions,
        ):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return principal

    return _permission_guard


def require_admin_principal(
    principal: Principal = Depends(get_current_principal),
) -> Principal:
    if principal.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return principal


def require_agent_principal(
    principal: Principal = Depends(get_current_principal),
) -> Principal:
    if principal.role != UserRole.AGENT:
        raise HTTPException(status_code=403, detail="Agent access required")
    return principal
