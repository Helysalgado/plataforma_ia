"""
Production settings
"""

from .base import *

DEBUG = False

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Allowed hosts (must be configured via environment variable)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Email: SMTP backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Logging: Production level
LOGGING['root']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'INFO'
