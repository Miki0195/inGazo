"""
Development settings for InGazo project.
"""

from datetime import timedelta

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Add browsable API renderer in development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# Disable throttling in development
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {  # noqa
    'anon': '10000/hour',
    'user': '100000/hour',
}

# Email Backend - Console for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug Toolbar (optional, install separately if needed)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
# INTERNAL_IPS = ['127.0.0.1']

# More verbose logging in development
LOGGING['handlers']['console']['level'] = 'DEBUG'  # noqa
LOGGING['loggers']['django']['level'] = 'DEBUG'  # noqa

# Shorter token lifetimes for testing
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(hours=24)  # noqa
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(days=30)  # noqa

# Static files
STATICFILES_DIRS = []

# Cache - Use local memory cache in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Security settings - relaxed for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

