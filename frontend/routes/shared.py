from pathlib import Path
from urllib.parse import urlencode

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from frontend.backend_client import auth, common
from frontend.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

TOKEN_COOKIE_NAME = "pg_access_token"
STATUS_OPTIONS = ["new", "contacted", "qualified", "negotiating", "closed", "lost"]


def to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return False


def get_session_principal(request: Request) -> tuple[str | None, dict | None]:
    token = request.cookies.get(TOKEN_COOKIE_NAME)
    if not token:
        return None, None
    try:
        principal = auth.get_current_user(token)
    except common.BackendClientError:
        return None, None
    return token, principal


def base_context(request: Request) -> dict:
    _, principal = get_session_principal(request)
    role = principal.get("role") if principal else None
    role_home_url = "/portal/admin" if role == "admin" else "/portal/agent" if role == "agent" else None
    return {
        "request": request,
        "app_name": settings.frontend_app_name,
        "backend_base_url": settings.frontend_backend_base_url,
        "current_principal": principal,
        "role_home_url": role_home_url,
    }


def redirect_with_message(path: str, *, success: str | None = None, error: str | None = None):
    query = {}
    if success:
        query["success"] = success
    if error:
        query["error"] = error
    url = f"{path}?{urlencode(query)}" if query else path
    return RedirectResponse(url=url, status_code=303)


def require_login(request: Request) -> tuple[str, dict] | RedirectResponse:
    token, principal = get_session_principal(request)
    if not token or not principal:
        return RedirectResponse(url="/login", status_code=303)
    return token, principal


def require_role(request: Request, allowed_roles: set[str]) -> tuple[str, dict] | RedirectResponse:
    auth = require_login(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, principal = auth
    role = principal.get("role")
    if role not in allowed_roles:
        return RedirectResponse(url="/portal", status_code=303)
    return token, principal


def redirect_logged_in_user(request: Request) -> RedirectResponse | None:
    auth = require_login(request)
    if isinstance(auth, RedirectResponse):
        return None
    _, principal = auth
    if principal.get("role") == "admin":
        return RedirectResponse(url="/portal/admin", status_code=303)
    if principal.get("role") == "agent":
        return RedirectResponse(url="/portal/agent", status_code=303)
    return None
