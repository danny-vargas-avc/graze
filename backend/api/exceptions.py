"""
Custom exception handling for consistent API error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Return consistent error format across all API errors."""
    response = exception_handler(exc, context)

    if response is not None:
        error_code = 'SERVER_ERROR'
        field = None

        if response.status_code == 400:
            error_code = 'INVALID_FILTER'
            if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
                field = list(exc.detail.keys())[0] if exc.detail else None
        elif response.status_code == 404:
            error_code = 'NOT_FOUND'
        elif response.status_code == 429:
            error_code = 'RATE_LIMIT'

        message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)

        error_response = {
            'error': {
                'code': error_code,
                'message': message,
            }
        }

        if field:
            error_response['error']['field'] = field

        return Response(error_response, status=response.status_code)

    return response


class InvalidFilterError(Exception):
    """Raised when filter parameters are invalid."""
    pass
