from typing import Any

import httpx

from frontend.backend_client.common import BackendClientError, _url


def login(email: str, password: str) -> str:
    try:
        response = httpx.post(
            _url("/api/v1/auth/login"),
            json={"email": email, "password": password},
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise BackendClientError("Invalid email or password") from exc
        if exc.response.status_code == 403:
            raise BackendClientError("User is inactive") from exc
        raise BackendClientError("Login failed") from exc
    except httpx.HTTPError as exc:
        raise BackendClientError("Login failed") from exc

    data = response.json()
    token = data.get("access_token") if isinstance(data, dict) else None
    if isinstance(token, str) and token:
        return token
    raise BackendClientError("Unexpected login response")


def get_current_user(token: str) -> dict[str, Any]:
    try:
        response = httpx.get(
            _url("/api/v1/auth/me"),
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise BackendClientError("Failed to fetch current user") from exc

    data = response.json()
    if isinstance(data, dict):
        return data
    raise BackendClientError("Unexpected current user response")
