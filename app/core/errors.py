"""
Error response builder + global exception handlers.
One file, one responsibility: always return the same JSON shape.
"""

from datetime import datetime, timezone

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError


def _error_body(status_code: int, message: str, details: list | None = None) -> dict:
    body = {
        "status": "error",
        "code": status_code,
        "message": message,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if details is not None:
        body["details"] = details
    return body


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, exc.message),
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, message),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    for err in exc.errors():
        loc = err.get("loc", [])
        if "body" in loc and err.get("type") in ("missing", "value_error.missing", "string_type"):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=_error_body(
                    status.HTTP_400_BAD_REQUEST,
                    "Body is required",
                ),
            )
    details = [
        {
            "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
            "message": err.get("msg", "Invalid value"),
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=_error_body(
            status.HTTP_400_BAD_REQUEST,
            "Validation failed",
            details=details,
        ),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An unexpected error occurred.",
        ),
    )
