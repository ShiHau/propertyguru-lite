from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from frontend.backend_client import auth, common
from frontend.routes.shared import (
    TOKEN_COOKIE_NAME,
    base_context,
    require_login,
    templates,
)

router = APIRouter(tags=["frontend-auth"])


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_form(request: Request):
    auth = require_login(request)
    if not isinstance(auth, RedirectResponse):
        return RedirectResponse(url="/portal", status_code=303)
    context = base_context(request)
    context.update({"error_message": None})
    return templates.TemplateResponse(request, "auth/login.html", context)


@router.post("/login", response_class=HTMLResponse, include_in_schema=False)
def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    context = base_context(request)
    context.update({"error_message": None})
    try:
        token = auth.login(email, password)
        principal = auth.get_current_user(token)
        if principal.get("role") not in {"admin", "agent"}:
            raise common.BackendClientError("Unsupported role")
        response = RedirectResponse(url="/portal", status_code=303)
        response.set_cookie(TOKEN_COOKIE_NAME, token, httponly=True, samesite="lax")
        return response
    except common.BackendClientError as exc:
        context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "auth/login.html", context)


@router.post("/logout", include_in_schema=False)
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(TOKEN_COOKIE_NAME)
    return response


@router.get("/portal", response_class=HTMLResponse, include_in_schema=False)
def portal_entry(request: Request):
    auth = require_login(request)
    if isinstance(auth, RedirectResponse):
        return auth
    _, principal = auth
    if principal.get("role") == "admin":
        return RedirectResponse(url="/portal/admin", status_code=303)
    if principal.get("role") == "agent":
        return RedirectResponse(url="/portal/agent", status_code=303)
    return RedirectResponse(url="/login", status_code=303)
