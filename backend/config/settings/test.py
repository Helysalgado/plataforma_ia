"""
Test settings
"""

from .base import *

DEBUG = False

# Use in-memory database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for tests (faster)
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# MIGRATION_MODULES = DisableMigrations()

# Email: Locmem backend (store in memory, no actual sending)
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable rate limiting in tests
RATELIMIT_ENABLE = False

# Simplify password hashing for speed
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging in tests
LOGGING['root']['level'] = 'ERROR'
LOGGING['loggers']['apps']['level'] = 'ERROR'
