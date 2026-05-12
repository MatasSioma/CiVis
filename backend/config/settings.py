import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def get_csv_env(name, default=''):
	return [value.strip() for value in os.environ.get(name, default).split(',') if value.strip()]


SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')
PERSONAL_CODE_PEPPER = os.environ.get('PERSONAL_CODE_PEPPER', SECRET_KEY)
# Env var is OPEN_API_KEY (note: misspelled in .env) — normalize on the Python side.
OPENAI_API_KEY = os.environ.get('OPEN_API_KEY', '')

DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'rest_framework',
	'corsheaders',
	'api',
]

MIDDLEWARE = [
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
	'default': dj_database_url.config(
		default='postgres://civis:civis@db:5432/civis',
		conn_max_age=600,
	)
}

AUTH_PASSWORD_VALIDATORS = [
	{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
	{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
	{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
	{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'api.User'

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = get_csv_env(
	'CSRF_TRUSTED_ORIGINS',
	'http://localhost:5173,http://127.0.0.1:5173',
)

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG

REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': [
		'rest_framework.authentication.SessionAuthentication',
	],
	'DEFAULT_PERMISSION_CLASSES': [
		'rest_framework.permissions.AllowAny',
	],
	'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
	'PAGE_SIZE': 10,
}
