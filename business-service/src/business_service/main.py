from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from business_service.infrastructure.config.settings import get_settings
from business_service.presentation.api.errors import register_error_handlers
from business_service.presentation.api.routes import clients, engines, repair_orders

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Engine Repair - Business Service",
        version="0.1.0",
        description="Clients, engines and repair orders. Every endpoint except /health requires an RS256 "
        "access token issued by the auth service.",
        docs_url=f"{API_PREFIX}/docs",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
    )
    register_error_handlers(app)

    @app.get("/health", tags=["Health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    for module in (clients, engines, repair_orders):
        app.include_router(module.router, prefix=API_PREFIX)
    return app


app = create_app()
