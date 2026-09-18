"""
Custom application exceptions.
Raise these from services/routes — never import HTTPException in business logic.
"""

from fastapi import status


class AppError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictException(AppError):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, status.HTTP_409_CONFLICT)


class UnauthorizedException(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class BadRequestException(AppError):
    def __init__(self, message: str = "Bad Request") -> None:
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
