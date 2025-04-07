from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from http import HTTPStatus
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base error class for application-specific exceptions"""

    def __init__(self, message: str, code: HTTPStatus = HTTPStatus.BAD_REQUEST):
        self.message = message
        self.code = code


class NotFoundError(AppError):
    """Resource not found exception"""

    def __init__(self, resource: str):
        super().__init__(
            message=f"{resource} not found",
            code=HTTPStatus.NOT_FOUND
        )


class RateLimitExceededError(AppError):
    """Rate limiting exception"""

    def __init__(self):
        super().__init__(
            message="Rate limit exceeded",
            code=HTTPStatus.TOO_MANY_REQUESTS
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers"""

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(exc: ValidationError):
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "details": exc.errors()
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(exc: SQLAlchemyError):
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            content={
                "error": "database_error",
                "message": "Service temporarily unavailable"
            }
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(exc: NotFoundError):
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": "not_found",
                "message": exc.message
            }
        )

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(exc: RateLimitExceededError):
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": "rate_limit_exceeded",
                "message": exc.message
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(exc: Exception):
        logger.critical(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": "Internal server error"
            }
        )
