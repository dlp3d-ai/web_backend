import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.utils import is_body_allowed_for_status_code
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..utils.log import get_logger


class APIErrorMessage(BaseModel):
    """Standardized API error message model.

    This model provides a consistent structure for API error responses,
    including error message, status code, and optional detailed information.

    Args:
        message (str):
            Human-readable error message describing what went wrong.
        code (int):
            HTTP status code associated with the error.
        detail (dict | None, optional):
            Additional error details or context information.
            Defaults to None.
    """
    message: str
    code: int
    detail: dict | None = None


OPENAPI_RESPONSE_400 = {
    '400': {
        'description': 'Bad Request',
        'model': APIErrorMessage
    }
}
OPENAPI_RESPONSE_401 = {
    '401': {
        'description': 'Invalid Authentication',
        'model': APIErrorMessage
    }
}
OPENAPI_RESPONSE_403 = {
    '403': {
        'description': 'Forbidden',
        'model': APIErrorMessage
    }
}
OPENAPI_RESPONSE_404 = {
    '404': {
        'description': 'Not found',
        'model': APIErrorMessage
    }
}
OPENAPI_RESPONSE_422 = {
    '422': {
        'description': 'Validation Error',
        'model': APIErrorMessage
    }
}
OPENAPI_RESPONSE_500 = {
    '500': {
        'description': 'Internal Server Error',
        'model': APIErrorMessage
    }
}
OPENAPI_RESPONSE_501 = {
    '501': {
        'description': 'Not Implemented',
        'model': APIErrorMessage
    }
}
OPENAPI_RESPONSE_503 = {
    '503': {
        'description': 'Service Unavailable',
        'model': APIErrorMessage
    }
}

class NoLogFileException(HTTPException):
    """Exception raised when no log file is found or available.

    This exception is raised when the server attempts to access log files
    but cannot locate the log file path or the file does not exist.
    """
    pass

class ReadOnlyCharacterException(HTTPException):
    """Exception raised when attempting to modify a read-only character.

    This exception is raised when the server attempts to update a character
    that has been marked as read-only and cannot be modified.
    """
    pass

class NoUserException(HTTPException):
    """Exception raised when no user is found.

    This exception is raised when the server attempts to delete a user
    but the user does not exist.
    """
    pass

class NoCharacterException(HTTPException):
    """Exception raised when no character is found.

    This exception is raised when the server attempts to delete a character
    but the character does not exist.
    """
    pass

async def http_exception_handler(request, exc):
    """Handle HTTP exceptions and return standardized error responses.

    This handler processes HTTP exceptions and converts them into
    standardized API error responses with proper status codes and headers.

    Args:
        request:
            FastAPI request object.
        exc:
            HTTP exception instance to handle.

    Returns:
        Response | JSONResponse:
            Response object with appropriate status code and error details.
            Returns a simple Response for status codes that don't allow body,
            or JSONResponse with error details for other status codes.
    """
    headers = getattr(exc, 'headers', None)
    if headers is None:
        headers = {}
    if request.headers is not None:
        headers = {**headers, **request.headers}

    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)

    content = APIErrorMessage(
        message=f'HTTP Error {exc.status_code}',
        code=exc.status_code,
        detail={'error': exc.detail},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=content.model_dump(),
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc):
    """Handle request validation errors and return detailed error information.

    This handler processes Pydantic validation errors and returns
    structured error information including validation details and request body.

    Args:
        request (Request):
            FastAPI request object containing the invalid request.
        exc:
            RequestValidationError instance containing validation details.

    Returns:
        JSONResponse:
            JSON response with validation error details including
            specific field errors and the original request body.
    """
    content = APIErrorMessage(
        message='Validation Error',
        code=422,
        detail={
            'errors': exc.errors(),
            'body': exc.body
        },
    )

    return JSONResponse(
        content=content.model_dump(),
        status_code=422,
        headers=request.headers,
    )


async def exception_handler(request: Request, exc):
    """Handle general exceptions and return internal server error responses.

    This handler catches all unhandled exceptions and logs them while
    returning a generic internal server error response to the client.

    Args:
        request (Request):
            FastAPI request object where the exception occurred.
        exc:
            Exception instance that was not handled by other handlers.

    Returns:
        JSONResponse:
            JSON response with internal server error status and
            basic error information (exception type and message).
    """
    content = APIErrorMessage(
        message='Internal Server Error',
        code=500,
        detail={'error': f'{exc}, type: {type(exc)}'},
    )
    logger = get_logger()
    logger.error(traceback.format_exc())
    return JSONResponse(
        content=content.model_dump(),
        status_code=500,
        headers=request.headers,
    )


def register_error_handlers(app: FastAPI):
    """Register all exception handlers with the FastAPI application.

    This function registers the custom exception handlers for different
    types of exceptions to provide consistent error responses across
    the application.

    Args:
        app (FastAPI):
            FastAPI application instance to register handlers with.
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(ReadOnlyCharacterException, http_exception_handler)
    app.add_exception_handler(RequestValidationError,
                              validation_exception_handler)
    app.add_exception_handler(NoUserException, http_exception_handler)
    app.add_exception_handler(NoCharacterException, http_exception_handler)
    app.add_exception_handler(Exception, exception_handler)
