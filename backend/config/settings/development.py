"""
Development settings
"""

from .base import *

DEBUG = True

# Development-specific settings
# INSTALLED_APPS += [
#     'debug_toolbar',  # Django Debug Toolbar (opcional)
# ]

# MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Email: Console backend (print to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Allow all CORS in development
CORS_ALLOW_ALL_ORIGINS = True
