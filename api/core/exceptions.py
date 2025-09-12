from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Exception raised when a requested resource does not exist."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AlreadyExistsException(HTTPException):
    """Exception raised when a resource already exists and cannot be duplicated."""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnauthorizedException(HTTPException):
    """Exception raised when authentication fails or is missing."""

    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    """Exception raised when access is forbidden due to insufficient permissions."""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BusinessRuleViolationException(HTTPException):
    """Exception raised when a business rule is violated (e.g. invalid state transition)."""

    def __init__(self, detail: str = "Business rule violated"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class ConflictException(HTTPException):
    """Exception raised when operation cannot be completed due to conflicts."""

    def __init__(self, detail: str = "Operation conflicts with current state"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
