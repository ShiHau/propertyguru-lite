from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.schema.auth import CurrentUserResponse, LoginRequest, TokenResponse
from backend.api.security import get_current_principal
from backend.db import get_db
from backend.lib.auth import AuthenticationService, Principal

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    principal = AuthenticationService.authenticate_user(db, payload.email, payload.password)
    if not principal:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not principal.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    token = AuthenticationService.create_access_token(
        user_id=principal.user_id,
        role=principal.role,
    )

    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUserResponse)
def me(principal: Principal = Depends(get_current_principal)):
    return CurrentUserResponse(
        user_id=principal.user_id,
        email=principal.email,
        full_name=principal.full_name,
        role=principal.role,
        is_active=principal.is_active,
    )
