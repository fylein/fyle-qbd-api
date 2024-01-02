"""
Django settings for quickbooks_desktop_api project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path
import sys


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get('DEBUG') == 'True' else False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Installed Apps
    'rest_framework',
    'corsheaders',
    'fyle_rest_auth',
    'fyle_accounting_mappings',
    'django_q',
    'django_filters',

    # Created Apps
    'apps.users',
    'apps.workspaces',
    'apps.fyle',
    'apps.tasks',
    'apps.mappings',
    'apps.qbd'
]

MIDDLEWARE = [
    'quickbooks_desktop_api.logging_middleware.ErrorHandlerMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quickbooks_desktop_api.urls'

AUTH_USER_MODEL = 'users.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

FYLE_REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'apps.users.serializers.UserSerializer'
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'apps.workspaces.permissions.WorkspacePermissions'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'fyle_rest_auth.authentication.FyleJWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

Q_CLUSTER = {
    'name': 'fyle_qbd_api',
    'save_limit': 0,
    'workers': int(os.environ.get('NO_WORKERS', 4)),
    'queue_limit': 30,
    'cached': False,
    'orm': 'default',
    'ack_failures': True,
    'poll': 1,
    'max_attempts': 1,
    'attempt_count': 1,
    'retry': 14400,
    'timeout': 3600,
    'catch_up': False
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '{levelname} %s {asctime} {module} {message} ' % 'QBD_API',
            'style': '{',
        },
        'requests': {
            'format': 'request {levelname} %s {asctime} {message}' % 'QBD_API',
            'style': '{'
        }
    },
    'handlers': {
        'debug_logs': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        },
        'request_logs': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'requests'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['request_logs'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_logs'],
            'propagate': False
        },
        'quickbooks_desktop_api': {
            'handlers': ['debug_logs'],
            'level': 'ERROR',
            'propagate': False
        },
        'apps': {
            'handlers': ['debug_logs'],
            'level': 'ERROR',
            'propagate': False
        },
        'django_q': {
            'handlers': ['debug_logs'],
            'propagate': True,
        },
        'fyle_integrations_platform_connector': {
            'handlers': ['debug_logs'],
            'propagate': True,
        },
    }
}

WSGI_APPLICATION = 'quickbooks_desktop_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}


DATABASE_ROUTERS = ['quickbooks_desktop_api.cache_router.CacheRouter']

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


FYLE_BASE_URL = os.environ.get('FYLE_BASE_URL')
FYLE_APP_URL = os.environ.get('FYLE_APP_URL')
FYLE_TOKEN_URI = os.environ.get('FYLE_TOKEN_URI')
FYLE_CLIENT_ID = os.environ.get('FYLE_CLIENT_ID')
FYLE_CLIENT_SECRET = os.environ.get('FYLE_CLIENT_SECRET')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_EMAIL_FROM')
