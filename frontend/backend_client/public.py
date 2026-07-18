from typing import Any

import httpx

from frontend.backend_client.common import BackendClientError, _url


def get_listings(limit: int = 50) -> list[dict[str, Any]]:
    try:
        response = httpx.get(
            _url("/api/v1/client/listings"),
            params={"limit": limit, "skip": 0},
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to fetch listings") from exc

    data = response.json()
    if isinstance(data, list):
        return data
    raise BackendClientError("Unexpected listings response")


def get_listing(listing_id: int) -> dict[str, Any]:
    try:
        response = httpx.get(
            _url(f"/api/v1/client/listings/{listing_id}"), timeout=10.0
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise BackendClientError("Listing not found") from exc
        raise BackendClientError("Failed to fetch listing details") from exc
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to fetch listing details") from exc

    data = response.json()
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected listing detail response")


def submit_inquiry(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        response = httpx.post(
            _url("/api/v1/client/inquiries"),
            json=payload,
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 400:
            return {"status": "rejected", "reason": "Invalid listing_id"}
        raise BackendClientError("Backend rejected inquiry") from exc
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to submit inquiry") from exc

    data = response.json()
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected inquiry response")
