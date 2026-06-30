from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from frontend.backend_client import admin, common
from frontend.routes.shared import base_context, redirect_with_message, require_role, templates

router = APIRouter(tags=["frontend-admin"])


@router.get("/portal/admin", response_class=HTMLResponse, include_in_schema=False)
def admin_dashboard(request: Request):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    context = base_context(request)
    context.update({"error_message": request.query_params.get("error"), "stats": {}})
    try:
        context["stats"] = admin.get_dashboard_stats(token)
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "admin/portal_admin_dashboard.html", context)


@router.get("/portal/admin/agents", response_class=HTMLResponse, include_in_schema=False)
def admin_agents_list(request: Request):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    context = base_context(request)
    context.update(
        {
            "error_message": request.query_params.get("error"),
            "success_message": request.query_params.get("success"),
            "agents": [],
        }
    )
    try:
        users = admin.get_users(token, limit=200)
        context["agents"] = [user for user in users if user.get("role") == "agent"]
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "admin/portal_admin_agents.html", context)


@router.get("/portal/admin/agents/{user_id}", response_class=HTMLResponse, include_in_schema=False)
def admin_agent_detail(request: Request, user_id: int):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    context = base_context(request)
    context.update(
        {
            "error_message": request.query_params.get("error"),
            "success_message": request.query_params.get("success"),
            "agent": None,
        }
    )
    try:
        users = admin.get_users(token, limit=300)
        context["agent"] = next(
            (user for user in users if user.get("role") == "agent" and user.get("id") == user_id),
            None,
        )
        if not context["agent"] and not context["error_message"]:
            context["error_message"] = "Agent not found"
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "admin/portal_admin_agent_detail.html", context)


@router.post("/portal/admin/agents/{user_id}/update", include_in_schema=False)
def admin_update_agent(
    request: Request,
    user_id: int,
    email: str | None = Form(None),
    full_name: str | None = Form(None),
    password: str | None = Form(None),
    is_active_action: str = Form("keep"),
):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    payload: dict[str, object] = {}
    if email and email.strip():
        payload["email"] = email.strip()
    if full_name and full_name.strip():
        payload["full_name"] = full_name.strip()
    if password and password.strip():
        payload["password"] = password.strip()
    if is_active_action in {"true", "false"}:
        payload["is_active"] = is_active_action == "true"

    if not payload:
        return redirect_with_message(f"/portal/admin/agents/{user_id}", error="No update values provided")

    try:
        admin.update_user(token, user_id=user_id, role="agent", payload=payload)
        return redirect_with_message(f"/portal/admin/agents/{user_id}", success="Agent updated")
    except common.BackendClientError as exc:
        return redirect_with_message(f"/portal/admin/agents/{user_id}", error=str(exc))


@router.post("/portal/admin/agents/{user_id}/toggle-active", include_in_schema=False)
def admin_toggle_agent_active(request: Request, user_id: int):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    try:
        users = admin.get_users(token, limit=300)
        agent = next(
            (user for user in users if user.get("role") == "agent" and user.get("id") == user_id),
            None,
        )
        if not agent:
            return redirect_with_message(f"/portal/admin/agents/{user_id}", error="Agent not found")

        new_state = not bool(agent.get("is_active"))
        admin.update_user(token, user_id=user_id, role="agent", payload={"is_active": new_state})
        status_text = "active" if new_state else "inactive"
        return redirect_with_message(f"/portal/admin/agents/{user_id}", success=f"Agent set to {status_text}")
    except common.BackendClientError as exc:
        return redirect_with_message(f"/portal/admin/agents/{user_id}", error=str(exc))


@router.post("/portal/admin/agents/{user_id}/deactivate", include_in_schema=False)
def admin_deactivate_agent(request: Request, user_id: int):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth
    try:
        admin.deactivate_user(token, user_id=user_id, role="agent")
        return redirect_with_message(f"/portal/admin/agents/{user_id}", success="Agent deactivated")
    except common.BackendClientError as exc:
        return redirect_with_message(f"/portal/admin/agents/{user_id}", error=str(exc))


@router.get("/portal/admin/inquiries", response_class=HTMLResponse, include_in_schema=False)
def admin_inquiries_list(request: Request):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    context = base_context(request)
    context.update({"error_message": request.query_params.get("error"), "inquiries": []})
    try:
        inquiries = admin.get_inquiries(token, limit=100)
        listings = admin.get_listings(token, limit=500)
        users = admin.get_users(token, limit=500)

        listing_names = {
            listing.get("id"): listing.get("title")
            for listing in listings
            if isinstance(listing.get("id"), int)
        }
        agent_names = {
            user.get("id"): user.get("full_name")
            for user in users
            if isinstance(user.get("id"), int) and user.get("role") == "agent"
        }

        for inquiry in inquiries:
            listing_id = inquiry.get("listing_id")
            agent_id = inquiry.get("assigned_agent_id")
            inquiry["listing_name"] = listing_names.get(listing_id) or listing_id
            inquiry["agent_name"] = agent_names.get(agent_id) or "Unassigned"

        context["inquiries"] = inquiries
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "admin/portal_admin_inquiries.html", context)


@router.get("/portal/admin/inquiries/{inquiry_id}", response_class=HTMLResponse, include_in_schema=False)
def admin_inquiry_detail(request: Request, inquiry_id: int):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    context = base_context(request)
    context.update({"error_message": request.query_params.get("error"), "inquiry": None})
    try:
        inquiry = admin.get_inquiry_detail(token, inquiry_id)
        listing_id = inquiry.get("listing_id")
        agent_id = inquiry.get("assigned_agent_id")

        inquiry["listing_name"] = str(listing_id)
        inquiry["agent_name"] = "Unassigned"

        if isinstance(listing_id, int):
            try:
                listings = admin.get_listings(token, limit=500)
                listing = next((item for item in listings if item.get("id") == listing_id), None)
                if listing and listing.get("title"):
                    inquiry["listing_name"] = listing.get("title")
            except common.BackendClientError:
                pass

        if isinstance(agent_id, int):
            try:
                users = admin.get_users(token, limit=500)
                agent = next((item for item in users if item.get("id") == agent_id and item.get("role") == "agent"), None)
                if agent and agent.get("full_name"):
                    inquiry["agent_name"] = agent.get("full_name")
                else:
                    inquiry["agent_name"] = str(agent_id)
            except common.BackendClientError:
                inquiry["agent_name"] = str(agent_id)

        context["inquiry"] = inquiry
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "admin/portal_admin_inquiry_detail.html", context)


@router.get("/portal/admin/listings", response_class=HTMLResponse, include_in_schema=False)
def admin_listings_list(request: Request):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    context = base_context(request)
    context.update(
        {
            "error_message": request.query_params.get("error"),
            "success_message": request.query_params.get("success"),
            "listings": [],
        }
    )
    try:
        context["listings"] = admin.get_listings(token, limit=200)
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "admin/portal_admin_listings.html", context)


@router.get("/portal/admin/listings/new", response_class=HTMLResponse, include_in_schema=False)
def admin_listing_create_form(request: Request):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    context = base_context(request)
    context.update({"error_message": request.query_params.get("error")})
    return templates.TemplateResponse(request, "admin/portal_admin_listing_new.html", context)


@router.post("/portal/admin/listings/new", include_in_schema=False)
def admin_listing_create(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    price: float = Form(...),
    bedrooms: int = Form(...),
    bathrooms: int = Form(...),
    listing_type: str = Form(...),
    square_feet: str | None = Form(None),
):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    payload: dict[str, object] = {
        "title": title,
        "description": description,
        "address": address,
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "listing_type": listing_type,
    }
    if square_feet and square_feet.strip():
        payload["square_feet"] = float(square_feet)

    try:
        admin.create_listing(token, payload)
        return redirect_with_message("/portal/admin/listings", success="Listing created")
    except (common.BackendClientError, ValueError) as exc:
        return redirect_with_message("/portal/admin/listings/new", error=str(exc))


@router.get("/portal/admin/listings/{listing_id}", response_class=HTMLResponse, include_in_schema=False)
def admin_listing_detail(request: Request, listing_id: int):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    context = base_context(request)
    context.update(
        {
            "error_message": request.query_params.get("error"),
            "success_message": request.query_params.get("success"),
            "listing": None,
        }
    )
    try:
        listings = admin.get_listings(token, limit=300)
        context["listing"] = next((listing for listing in listings if listing.get("id") == listing_id), None)
        if not context["listing"] and not context["error_message"]:
            context["error_message"] = "Listing not found"
    except common.BackendClientError as exc:
        if not context["error_message"]:
            context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "admin/portal_admin_listing_detail.html", context)


@router.post("/portal/admin/listings/{listing_id}/update", include_in_schema=False)
def admin_listing_update(
    request: Request,
    listing_id: int,
    title: str | None = Form(None),
    description: str | None = Form(None),
    address: str | None = Form(None),
    price: str | None = Form(None),
    bedrooms: str | None = Form(None),
    bathrooms: str | None = Form(None),
    square_feet: str | None = Form(None),
    listing_type: str | None = Form(None),
    is_active_action: str = Form("keep"),
):
    auth = require_role(request, {"admin"})
    if isinstance(auth, RedirectResponse):
        return auth
    token, _ = auth

    payload: dict[str, object] = {}
    if title and title.strip():
        payload["title"] = title.strip()
    if description and description.strip():
        payload["description"] = description.strip()
    if address and address.strip():
        payload["address"] = address.strip()
    if listing_type and listing_type.strip():
        payload["listing_type"] = listing_type.strip()
    if price and price.strip():
        payload["price"] = float(price)
    if bedrooms and bedrooms.strip():
        payload["bedrooms"] = int(bedrooms)
    if bathrooms and bathrooms.strip():
        payload["bathrooms"] = int(bathrooms)
    if square_feet and square_feet.strip():
        payload["square_feet"] = float(square_feet)
    if is_active_action in {"true", "false"}:
        payload["is_active"] = is_active_action == "true"

    if not payload:
        return redirect_with_message(f"/portal/admin/listings/{listing_id}", error="No update values provided")

    try:
        admin.update_listing(token, listing_id, payload)
        return redirect_with_message(f"/portal/admin/listings/{listing_id}", success="Listing updated")
    except (common.BackendClientError, ValueError) as exc:
        return redirect_with_message(f"/portal/admin/listings/{listing_id}", error=str(exc))
