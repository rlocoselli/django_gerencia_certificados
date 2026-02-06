from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

def env(name: str, default=None):
    return os.environ.get(name, default)

# SECURITY
SECRET_KEY = env("DJANGO_SECRET_KEY", "django-insecure-replace-me")
DEBUG = env("DJANGO_DEBUG", "0").lower() in ("1", "true", "yes", "on")

# Hosts / site
ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in env("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
SITE_URL = env("SITE_URL", "https://leanway-consultores.eastus2.cloudapp.azure.com/")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'certificados',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# DATABASE (SQL Server via mssql-django + pyodbc)
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', 'mssql'),
        'NAME': env('DB_NAME', ''),
        'HOST': env('DB_HOST', ''),
        'PORT': env('DB_PORT', '1433'),
        'USER': env('DB_USER', ''),
        'PASSWORD': env('DB_PASSWORD', ''),
        'OPTIONS': {
            'driver': env('DB_DRIVER', 'ODBC Driver 18 for SQL Server'),
            'host_is_server': True,
            'extra_params': 'Encrypt=yes;TrustServerCertificate=no; loginTimeout=60;Connection Timeout=60;'
        },
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = env("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media (optional)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('SMTP_HOST', '')
EMAIL_PORT = int(env('SMTP_PORT', '587'))
EMAIL_HOST_USER = env('SMTP_USER', '')
EMAIL_HOST_PASSWORD = env('SMTP_PASSWORD', '')
EMAIL_USE_TLS = env('SMTP_USE_TLS', '1').lower() in ('1','true','yes','on')
EMAIL_USE_SSL = env('SMTP_USE_SSL', '0').lower() in ('1','true','yes','on')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

MS_GRAPH_TENANT_ID = env('TENANT', '')
MS_GRAPH_CLIENT_ID = env('CLIENT', '')
MS_GRAPH_CLIENT_SECRET = env('SECRET', '')

MS_GRAPH_SENDER = "certificado@leanway.com.br"

DEFAULT_FROM_EMAIL = "certificado@leanway.com.br"


# Optional: tighten security behind nginx (set these in prod)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
