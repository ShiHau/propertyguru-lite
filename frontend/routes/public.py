from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from frontend.backend_client import common, public
from frontend.routes.shared import base_context, redirect_logged_in_user, templates

router = APIRouter(tags=["frontend-public"])


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request):
    redirect = redirect_logged_in_user(request)
    if redirect:
        return redirect
    return templates.TemplateResponse(
        request, "public/home.html", base_context(request)
    )


@router.get("/listings", response_class=HTMLResponse, include_in_schema=False)
def listings(request: Request):
    redirect = redirect_logged_in_user(request)
    if redirect:
        return redirect

    context = base_context(request)
    context.update({"listings": [], "error_message": None})
    try:
        context["listings"] = public.get_listings(limit=50)
    except common.BackendClientError as exc:
        context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "public/listings.html", context)


@router.get(
    "/listings/{listing_id}", response_class=HTMLResponse, include_in_schema=False
)
def listing_detail(request: Request, listing_id: int):
    redirect = redirect_logged_in_user(request)
    if redirect:
        return redirect

    context = base_context(request)
    context.update({"listing": None, "listing_id": listing_id, "error_message": None})
    try:
        context["listing"] = public.get_listing(listing_id)
    except common.BackendClientError as exc:
        context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "public/listing_detail.html", context)


@router.get(
    "/listings/{listing_id}/inquiry",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def inquiry_form(request: Request, listing_id: int):
    redirect = redirect_logged_in_user(request)
    if redirect:
        return redirect

    context = base_context(request)
    context.update(
        {
            "listing": None,
            "listing_id": listing_id,
            "error_message": None,
            "success_message": None,
        }
    )
    try:
        context["listing"] = public.get_listing(listing_id)
    except common.BackendClientError as exc:
        context["error_message"] = str(exc)
    return templates.TemplateResponse(request, "public/inquiry.html", context)


@router.post(
    "/listings/{listing_id}/inquiry",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def inquiry_submit(
    request: Request,
    listing_id: int,
    client_name: str = Form(...),
    client_email: str = Form(...),
    client_phone: str = Form(...),
    message: str = Form(...),
):
    redirect = redirect_logged_in_user(request)
    if redirect:
        return redirect

    context = base_context(request)
    context.update(
        {
            "listing": None,
            "listing_id": listing_id,
            "error_message": None,
            "success_message": None,
        }
    )
    try:
        result = public.submit_inquiry(
            {
                "client_name": client_name,
                "client_email": client_email,
                "client_phone": client_phone,
                "listing_id": listing_id,
                "message": message,
            }
        )
        if result.get("status") == "rejected":
            context["error_message"] = result.get("reason", "Request rejected")
        else:
            context["success_message"] = "Inquiry submitted successfully."
    except common.BackendClientError as exc:
        context["error_message"] = str(exc)

    try:
        context["listing"] = public.get_listing(listing_id)
    except common.BackendClientError:
        if not context["error_message"]:
            context["error_message"] = "Failed to fetch listing details"
    return templates.TemplateResponse(request, "public/inquiry.html", context)
