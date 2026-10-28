"""Verifies access tokens issued by the auth service. Decoding alone is never trusted."""

from dataclasses import dataclass
from uuid import UUID

import jwt

ALLOWED_ROLES = frozenset({"ADMIN", "OPERATOR"})
REQUIRED_CLAIMS = ["iss", "aud", "sub", "iat", "exp", "jti"]


class InvalidTokenError(Exception):
    pass


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: UUID
    role: str


class JwtVerifier:
    def __init__(self, public_key: str, issuer: str, audience: str, algorithm: str = "RS256") -> None:
        self._public_key = public_key
        self._issuer = issuer
        self._audience = audience
        self._algorithms = [algorithm]

    def verify(self, token: str) -> AuthenticatedUser:
        try:
            claims = jwt.decode(
                token,
                self._public_key,
                algorithms=self._algorithms,
                issuer=self._issuer,
                audience=self._audience,
                options={"require": REQUIRED_CLAIMS},
            )
            user_id = UUID(str(claims["sub"]))
        except (jwt.PyJWTError, ValueError) as error:
            raise InvalidTokenError("The access token is invalid or has expired.") from error

        role = claims.get("role")
        if role not in ALLOWED_ROLES:
            raise InvalidTokenError("The access token is invalid or has expired.")
        return AuthenticatedUser(user_id=user_id, role=role)
