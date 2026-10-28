from uuid import uuid4

import jwt
import pytest

from tests.tokens import generate_key_pair, make_token

URL = "/api/v1/clients"


def test_health_is_public(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_missing_token_returns_401_problem(client):
    response = client.get(URL)
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.headers["www-authenticate"] == "Bearer"


def test_valid_token_is_accepted(client, auth_headers):
    assert client.get(URL, headers=auth_headers).status_code == 200


@pytest.mark.parametrize(
    "token",
    [
        make_token(generate_key_pair()[0]),  # signed with another private key
        make_token(exp=1_000_000, iat=999_000),  # expired
        make_token(iss="someone-else"),
        make_token(aud="other-api"),
        make_token(role="ROOT"),
        make_token(sub="not-a-uuid"),
        make_token(omit=("jti",)),
        make_token(omit=("exp",)),
        "not.a.jwt",
    ],
    ids=["foreign-key", "expired", "issuer", "audience", "role", "sub", "no-jti", "no-exp", "garbage"],
)
def test_invalid_tokens_are_rejected(client, token):
    response = client.get(URL, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_unsigned_tokens_are_rejected(client):
    claims = {"iss": "engine-repair-auth", "aud": "engine-repair-api", "sub": str(uuid4()), "role": "ADMIN"}
    unsigned = jwt.encode(claims, None, algorithm="none")
    assert client.get(URL, headers={"Authorization": f"Bearer {unsigned}"}).status_code == 401
