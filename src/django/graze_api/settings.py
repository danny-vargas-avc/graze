"""Django settings for Graze API."""
import os
from pathlib import Path
from decouple import config, Csv
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'api',
    'config',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'graze_api.urls'

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

WSGI_APPLICATION = 'graze_api.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = config('CORS_ORIGINS', default='http://localhost:5173', cast=Csv())

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': None,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

UNFOLD = {
    "SITE_TITLE": "Graze",
    "SITE_HEADER": "Graze",
    "SHOW_LANGUAGES": False,
    "COLORS": {
        "primary": {
            "50": "157 223 186",
            "100": "134 211 169",
            "200": "100 195 145",
            "300": "67 179 121",
            "400": "33 163 97",
            "500": "6 193 103",
            "600": "5 168 90",
            "700": "4 143 77",
            "800": "3 118 63",
            "900": "2 94 50",
            "950": "1 70 37",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Content",
                "items": [
                    {
                        "title": "Restaurants",
                        "icon": "restaurant",
                        "link": reverse_lazy("admin:api_restaurant_changelist"),
                    },
                    {
                        "title": "Menu Items",
                        "icon": "menu_book",
                        "link": reverse_lazy("admin:api_menuitem_changelist"),
                    },
                    {
                        "title": "Locations",
                        "icon": "location_on",
                        "link": reverse_lazy("admin:api_restaurantlocation_changelist"),
                    },
                ],
            },
            {
                "title": "Quality",
                "items": [
                    {
                        "title": "Data Flags",
                        "icon": "flag",
                        "link": reverse_lazy("admin:api_dataflag_changelist"),
                    },
                    {
                        "title": "Location Flags",
                        "icon": "report",
                        "link": reverse_lazy("admin:api_locationflag_changelist"),
                    },
                ],
            },
            {
                "title": "Configuration",
                "items": [
                    {
                        "title": "Filters",
                        "icon": "filter_alt",
                        "link": reverse_lazy("admin:config_filterconfiguration_changelist"),
                    },
                    {
                        "title": "Quick Filters",
                        "icon": "bolt",
                        "link": reverse_lazy("admin:config_quickfilter_changelist"),
                    },
                    {
                        "title": "Sort Options",
                        "icon": "sort",
                        "link": reverse_lazy("admin:config_sortoption_changelist"),
                    },
                    {
                        "title": "App Settings",
                        "icon": "settings",
                        "link": reverse_lazy("admin:config_appconfiguration_changelist"),
                    },
                ],
            },
            {
                "title": "Auth",
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}
