from typing import Any

import httpx

from frontend.backend_client.common import BackendClientError, _auth_headers, _url


def get_inquiries(token: str, limit: int = 20) -> list[dict[str, Any]]:
    try:
        response = httpx.get(
            _url("/api/v1/agent/inquiries"),
            params={"skip": 0, "limit": limit},
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to fetch agent inquiries") from exc

    data = response.json()
    if isinstance(data, list):
        return data
    raise BackendClientError("Unexpected agent inquiries response")


def get_inquiry_detail(token: str, inquiry_id: int) -> dict[str, Any]:
    try:
        response = httpx.get(
            _url(f"/api/v1/agent/inquiries/{inquiry_id}"),
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


def update_inquiry(
    token: str,
    inquiry_id: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    try:
        response = httpx.patch(
            _url(f"/api/v1/agent/inquiries/{inquiry_id}"),
            json=payload,
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to update inquiry") from exc

    data = response.json()
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected update inquiry response")


def update_profile(token: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        response = httpx.patch(
            _url("/api/v1/agent/users/me"),
            json=payload,
            headers=_auth_headers(token),
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to update profile") from exc

    data = response.json()
    if isinstance(data, dict) and data.get("status") == "rejected":
        raise BackendClientError(data.get("reason", "Request rejected"))
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected update profile response")
