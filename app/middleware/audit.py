from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.auth import verify_token
from app.core.database import AsyncSessionLocal
from app.services.audit import AuditService

ANONYMOUS = "anonymous"


def _identity_from_request(request: Request) -> tuple[str, str | None]:
    """Return (actor_id, impersonator_id) from a verified access token only (rule 8).

    Client-supplied identity headers are ignored. Impersonation is a signed
    ``imp`` claim set by the server when it issues an impersonation token.
    """
    auth = request.headers.get("Authorization", "")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return ANONYMOUS, None
    payload = verify_token(token.strip(), expected_type="access")
    if not payload or not payload.get("sub"):
        return ANONYMOUS, None
    imp = payload.get("imp")
    return str(payload["sub"]), str(imp) if imp else None


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        actor_id, impersonator_id = _identity_from_request(request)

        response = await call_next(request)

        async with AsyncSessionLocal() as db:
            await AuditService.log_action(
                db=db,
                action=f"{request.method} {request.url.path}",
                user_id=actor_id,
                resource=request.url.path,
                status=str(response.status_code),
                actor_id=actor_id,
                impersonator_id=impersonator_id,
                detalle={},
                filas_afectadas=0,
                ip=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent"),
            )

        return response
