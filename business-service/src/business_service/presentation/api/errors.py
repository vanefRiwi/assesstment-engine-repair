"""Maps errors to RFC 9457 problem responses without leaking internals."""

import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from business_service.domain.exceptions import (
    BusinessRuleError,
    ConflictError,
    DomainError,
    NotFoundError,
)
from business_service.infrastructure.security.jwt_verifier import InvalidTokenError

logger = logging.getLogger(__name__)

DOMAIN_STATUS: list[tuple[type[DomainError], int]] = [
    (NotFoundError, 404),
    (ConflictError, 409),
    (BusinessRuleError, 400),
]


def problem(request: Request, status: int, detail: str, errors: list[dict] | None = None, **headers: str):
    body: dict = {
        "type": "about:blank",
        "title": HTTPStatus(status).phrase,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
    }
    if errors is not None:
        body["errors"] = errors
    return JSONResponse(body, status_code=status, media_type="application/problem+json", headers=headers or None)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidTokenError)
    async def _invalid_token(request: Request, exc: InvalidTokenError):
        return problem(request, 401, str(exc), **{"WWW-Authenticate": "Bearer"})

    @app.exception_handler(DomainError)
    async def _domain(request: Request, exc: DomainError):
        status = next((code for kind, code in DOMAIN_STATUS if isinstance(exc, kind)), 400)
        return problem(request, status, str(exc))

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(str(part) for part in err["loc"] if part != "body"), "message": err["msg"]}
            for err in exc.errors()
        ]
        return problem(request, 422, "The request contains invalid fields.", errors)

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException):
        return problem(request, exc.status_code, str(exc.detail))

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception):
        # Log the type only: driver errors can contain SQL and parameters.
        logger.error("Unhandled error %s on %s %s", type(exc).__name__, request.method, request.url.path)
        return problem(request, 500, "An unexpected error occurred.")
