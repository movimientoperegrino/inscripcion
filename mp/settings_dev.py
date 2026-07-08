from .settings import *

DEBUG = True

# Add development apps
INSTALLED_APPS += (
    'django_extensions',
)

# Disable SSL/HTTPS related settings in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Use console email backend in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 