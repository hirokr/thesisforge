from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings

bearer_scheme = HTTPBearer(auto_error=False)
ASYMMETRIC_ALGORITHMS = {"ES256", "RS256"}


@dataclass(frozen=True)
class AuthenticatedUser:
    auth_user_id: str
    email: str | None = None
    claims: dict[str, Any] | None = None


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _authentication_not_configured() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Authentication is not configured.",
    )


@lru_cache(maxsize=8)
def _get_jwks_client(jwks_url: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(jwks_url)


def verify_supabase_jwt(token: str, settings: Settings) -> AuthenticatedUser:
    try:
        algorithm = jwt.get_unverified_header(token).get("alg")

        if algorithm == "HS256":
            if not settings.supabase_jwt_secret:
                raise _authentication_not_configured()
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience=settings.supabase_jwt_audience,
            )
        elif algorithm in ASYMMETRIC_ALGORITHMS:
            if not settings.supabase_url:
                raise _authentication_not_configured()
            supabase_url = settings.supabase_url.rstrip("/")
            jwks_client = _get_jwks_client(f"{supabase_url}/auth/v1/.well-known/jwks.json")
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=[algorithm],
                audience=settings.supabase_jwt_audience,
                issuer=f"{supabase_url}/auth/v1",
            )
        else:
            raise _unauthorized()
    except jwt.PyJWTError as exc:
        raise _unauthorized() from exc

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject:
        raise _unauthorized()

    email = payload.get("email")

    return AuthenticatedUser(
        auth_user_id=subject,
        email=email if isinstance(email, str) else None,
        claims=payload,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    return verify_supabase_jwt(credentials.credentials, settings)
