from .base import *
import os

# Força a obrigatoriedade da SECRET_KEY em produção
SECRET_KEY = env('SECRET_KEY')

DEBUG = False

# Segurança
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)

# Static files storage for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email (Placeholder para futuro se necessário)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
