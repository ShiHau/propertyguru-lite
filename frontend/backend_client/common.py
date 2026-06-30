from frontend.config import settings


class BackendClientError(Exception):
    pass


def _url(path: str) -> str:
    return f"{settings.frontend_backend_base_url.rstrip('/')}{path}"


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
