"""
Custom exception handler for consistent API error responses.
"""

from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Custom exception handler para DRF.
    
    Formato de respuesta de error:
    {
        "error": "Error message",
        "error_code": "ERROR_CODE",
        "details": {...}  # Opcional
    }
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize error response format
        custom_response = {
            'error': get_error_message(exc, response),
            'error_code': get_error_code(exc),
        }
        
        # Add details if available
        if hasattr(response, 'data') and isinstance(response.data, dict):
            if 'detail' not in response.data:
                custom_response['details'] = response.data
        
        response.data = custom_response
    
    return response


def get_error_message(exc, response):
    """Extract a user-friendly error message."""
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            # For validation errors, get first error
            for key, value in exc.detail.items():
                if isinstance(value, list):
                    return f"{key}: {value[0]}"
                return f"{key}: {value}"
        elif isinstance(exc.detail, list):
            return exc.detail[0]
        else:
            return str(exc.detail)
    
    return response.data.get('detail', 'An error occurred')


def get_error_code(exc):
    """Get error code based on exception type."""
    error_codes = {
        'NotAuthenticated': 'NOT_AUTHENTICATED',
        'AuthenticationFailed': 'AUTHENTICATION_FAILED',
        'PermissionDenied': 'PERMISSION_DENIED',
        'NotFound': 'NOT_FOUND',
        'MethodNotAllowed': 'METHOD_NOT_ALLOWED',
        'ValidationError': 'VALIDATION_ERROR',
        'Throttled': 'RATE_LIMIT_EXCEEDED',
    }
    
    exc_name = exc.__class__.__name__
    return error_codes.get(exc_name, 'INTERNAL_ERROR')
