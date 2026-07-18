from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from frontend.backend_client import agent, common, public
from frontend.routes.shared import (
    STATUS_OPTIONS,
    base_context,
    redirect_with_message,
    require_role,
    templates,
    to_bool,
)

router = APIRouter(tags=["frontend-agent"])


@router.get("/portal/agent", response_class=HTMLResponse, include_in_schema=False)
def agent_portal(request: Request):
    auth = require_role(request, {"agent"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, principal = auth

    context = base_context(request)
    context.update(
        {
            "error_message": request.query_params.get("error"),
            "success_message": request.query_params.get("success"),
            "inquiries": [],
            "is_active": to_bool(principal.get("is_active")),
        }
    )

    try:
        inquiries = agent.get_inquiries(token, limit=100)
        listing_cache: dict[int, str] = {}
        for inquiry in inquiries:
            listing_id = (
                inquiry.get("listing_id") if isinstance(inquiry, dict) else None
            )
            if not isinstance(listing_id, int):
                continue
            if listing_id not in listing_cache:
                try:
                    listing = public.get_listing(listing_id)
                    listing_cache[listing_id] = str(listing.get("title") or listing_id)
                except common.BackendClientError:
                    listing_cache[listing_id] = str(listing_id)
            inquiry["listing_title"] = listing_cache[listing_id]
        context["inquiries"] = inquiries
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "agent/portal_agent.html", context)


@router.get(
    "/portal/agent/listings/{listing_id}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def agent_listing_detail(request: Request, listing_id: int):
    auth = require_role(request, {"agent"})
    if isinstance(auth, RedirectResponse):
        return auth
    _, principal = auth

    context = base_context(request)
    context.update(
        {
            "error_message": request.query_params.get("error"),
            "listing": None,
            "is_active": to_bool(principal.get("is_active")),
        }
    )
    try:
        context["listing"] = public.get_listing(listing_id)
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(
        request, "agent/portal_agent_listing_detail.html", context
    )


@router.post("/portal/agent/toggle-active", include_in_schema=False)
def agent_toggle_active(request: Request):
    auth = require_role(request, {"agent"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, principal = auth
    current = to_bool(principal.get("is_active"))
    try:
        agent.update_profile(token, {"is_active": (not current)})
        state = "active" if not current else "inactive"
        return redirect_with_message("/portal/agent", success=f"Status set to {state}")
    except common.BackendClientError as exc:
        return redirect_with_message("/portal/agent", error=str(exc))


@router.get(
    "/portal/agent/inquiries/{inquiry_id}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def agent_inquiry_detail(request: Request, inquiry_id: int):
    auth = require_role(request, {"agent"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, principal = auth

    context = base_context(request)
    context.update(
        {
            "error_message": request.query_params.get("error"),
            "success_message": request.query_params.get("success"),
            "status_options": STATUS_OPTIONS,
            "inquiry": None,
            "listing": None,
            "is_active": to_bool(principal.get("is_active")),
        }
    )
    try:
        context["inquiry"] = agent.get_inquiry_detail(token, inquiry_id)
        listing_id = (
            context["inquiry"].get("listing_id")
            if isinstance(context["inquiry"], dict)
            else None
        )
        if isinstance(listing_id, int):
            try:
                context["listing"] = public.get_listing(listing_id)
            except common.BackendClientError:
                context["listing"] = None
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(
        request, "agent/portal_agent_inquiry_detail.html", context
    )


@router.post("/portal/agent/inquiries/{inquiry_id}/update", include_in_schema=False)
def agent_update_inquiry_action(
    request: Request,
    inquiry_id: int,
    status: str = Form(...),
    notes: str = Form(""),
):
    auth = require_role(request, {"agent"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    payload: dict[str, object] = {
        "status": status,
        "notes": notes.strip(),
    }

    try:
        agent.update_inquiry(token, inquiry_id=inquiry_id, payload=payload)
        return redirect_with_message(
            f"/portal/agent/inquiries/{inquiry_id}", success="Inquiry updated"
        )
    except common.BackendClientError as exc:
        return redirect_with_message(
            f"/portal/agent/inquiries/{inquiry_id}", error=str(exc)
        )
