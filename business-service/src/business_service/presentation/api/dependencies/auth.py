from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from business_service.infrastructure.config.settings import get_settings
from business_service.infrastructure.security.jwt_verifier import (
    AuthenticatedUser,
    InvalidTokenError,
    JwtVerifier,
)

bearer_scheme = HTTPBearer(auto_error=False, description="Access token issued by the auth service")


@lru_cache
def get_jwt_verifier() -> JwtVerifier:
    settings = get_settings()
    return JwtVerifier(
        public_key=settings.load_public_key(),
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        algorithm=settings.jwt_allowed_algorithm,
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    verifier: Annotated[JwtVerifier, Depends(get_jwt_verifier)],
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise InvalidTokenError("A Bearer access token is required.")
    return verifier.verify(credentials.credentials)


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
