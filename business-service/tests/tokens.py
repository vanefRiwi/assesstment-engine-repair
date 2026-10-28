"""Test key pair and token factory that mimic the auth service's tokens."""

import time
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ISSUER = "engine-repair-auth"
AUDIENCE = "engine-repair-api"


def generate_key_pair() -> tuple[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    ).decode()
    public_pem = (
        key.public_key()
        .public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        .decode()
    )
    return private_pem, public_pem


PRIVATE_KEY, PUBLIC_KEY = generate_key_pair()


def make_token(private_key: str = PRIVATE_KEY, *, omit: tuple[str, ...] = (), **overrides) -> str:
    now = int(time.time())
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": str(uuid4()),
        "role": "OPERATOR",
        "iat": now,
        "exp": now + 900,
        "jti": str(uuid4()),
        **overrides,
    }
    for name in omit:
        claims.pop(name, None)
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": "test-key"})
