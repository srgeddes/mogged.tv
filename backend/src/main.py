from __future__ import annotations

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Import models so SQLAlchemy relationships resolve at startup.
import friends.models as _friends_models  # noqa: F401
import organizations.models as _organizations_models  # noqa: F401
import streams.models as _streams_models  # noqa: F401
import trivia.models as _trivia_models  # noqa: F401
import users.models as _users_models  # noqa: F401
from auth.exceptions import InvalidTokenError
from auth.router import router as auth_router
from core.config import settings
from friends.router import router as friends_router
from organizations.router import router as orgs_router
from streams.router import router as streams_router
from trivia.router import router as trivia_router
from users.router import router as users_router


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=False,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_handler(_request: Request, exc: InvalidTokenError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": exc.message})

    app.include_router(auth_router, prefix="/api")
    app.include_router(streams_router, prefix="/api")
    app.include_router(users_router, prefix="/api")
    app.include_router(orgs_router, prefix="/api")
    app.include_router(friends_router, prefix="/api")
    app.include_router(trivia_router, prefix="/api")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
