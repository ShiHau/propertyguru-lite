from typing import Any

import httpx

from frontend.backend_client.common import BackendClientError, _auth_headers, _url


def get_dashboard_stats(token: str) -> dict[str, Any]:
    try:
        response = httpx.get(
            _url("/api/v1/admin/dashboard/stats"),
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to fetch admin dashboard stats") from exc

    data = response.json()
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected admin dashboard response")


def get_users(token: str, limit: int = 20) -> list[dict[str, Any]]:
    try:
        response = httpx.get(
            _url("/api/v1/admin/users"),
            params={"skip": 0, "limit": limit},
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to fetch admin users") from exc

    data = response.json()
    if isinstance(data, list):
        return data
    raise BackendClientError("Unexpected admin users response")


def get_inquiries(token: str, limit: int = 20) -> list[dict[str, Any]]:
    try:
        response = httpx.get(
            _url("/api/v1/admin/inquiries"),
            params={"skip": 0, "limit": limit},
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to fetch admin inquiries") from exc

    data = response.json()
    if isinstance(data, list):
        return data
    raise BackendClientError("Unexpected admin inquiries response")


def get_inquiry_detail(token: str, inquiry_id: int) -> dict[str, Any]:
    try:
        response = httpx.get(
            _url(f"/api/v1/admin/inquiries/{inquiry_id}"),
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to fetch inquiry details") from exc

    data = response.json()
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected inquiry details response")


def get_listings(token: str, limit: int = 20) -> list[dict[str, Any]]:
    try:
        response = httpx.get(
            _url("/api/v1/admin/listings"),
            params={"skip": 0, "limit": limit},
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to fetch admin listings") from exc

    data = response.json()
    if isinstance(data, list):
        return data
    raise BackendClientError("Unexpected admin listings response")


def update_user(
    token: str,
    user_id: int,
    role: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    try:
        response = httpx.patch(
            _url(f"/api/v1/admin/users/{user_id}"),
            params={"role": role},
            json=payload,
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to update user") from exc

    data = response.json()
    if isinstance(data, dict) and data.get("status") == "rejected":
        raise BackendClientError(data.get("reason", "Request rejected"))
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected update user response")


def deactivate_user(token: str, user_id: int, role: str) -> dict[str, Any]:
    try:
        response = httpx.delete(
            _url(f"/api/v1/admin/users/{user_id}"),
            params={"role": role},
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to deactivate user") from exc

    data = response.json()
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected deactivate user response")


def create_listing(token: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        response = httpx.post(
            _url("/api/v1/admin/listings"),
            json=payload,
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to create listing") from exc

    data = response.json()
    if isinstance(data, dict) and data.get("status") == "rejected":
        raise BackendClientError(data.get("reason", "Request rejected"))
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected create listing response")


def update_listing(
    token: str,
    listing_id: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    try:
        response = httpx.patch(
            _url(f"/api/v1/admin/listings/{listing_id}"),
            json=payload,
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to update listing") from exc

    data = response.json()
    if isinstance(data, dict) and data.get("status") == "rejected":
        raise BackendClientError(data.get("reason", "Request rejected"))
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected update listing response")