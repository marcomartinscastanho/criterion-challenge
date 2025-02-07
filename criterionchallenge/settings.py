"""
Django settings for criterionchallenge project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = os.getenv("DEBUG", None) == "True"

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a , between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1,[::1]'
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #
    "categories.apps.CategoryConfig",
    "common.apps.CommonConfig",
    "directors.apps.DirectorsConfig",
    "films.apps.FilmsConfig",
    "home.apps.HomeConfig",
    "picks.apps.PicksConfig",
    "users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "criterionchallenge.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "criterionchallenge.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME", "db"),
        "USER": os.getenv("DATABASE_USERNAME", "user"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "password"),
        "HOST": os.getenv("DATABASE_HOST", "127.0.0.1"),
        "PORT": os.getenv("DATABASE_PORT", 5432),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.User"

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# https://django-jazzmin.readthedocs.io/configuration/
JAZZMIN_SETTINGS = {
    "site_title": "Criterion Challenge Admin",
    "site_header": "Criterion Challenge",
    "site_brand": "Criterion Challenge",
    "welcome_sign": "Criterion Challenge Admin",
    "copyright": "Marco Martins Castanho",
    "hide_models": ["auth.Group"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "categories.Category": "fa-solid fa-list",
        "common.Country": "fa-solid fa-globe",
        "common.Gender": "fa-solid fa-venus-mars",
        "common.Genre": "fa-solid fa-masks-theater",
        "common.Keyword": "fa-solid fa-tags",
        "common.Region": "fa-solid fa-earth-africa",
        "common.Venue": "fa-solid fa-building",
        "directors.Director": "fa-solid fa-clapperboard",
        "films.Film": "fa-solid fa-film",
        "films.FilmSession": "fa-solid fa-bars-staggered",
        "picks.Pick": "fa-solid fa-check",
        "users.User": "fa-solid fa-user",
        "users.UserPreference": "fa-solid fa-sliders",
        "users.UserWatchlist": "fa-regular fa-square",
        "users.UserWatched": "fa-solid fa-square-check",
    },
}

CRITERION_CF_CLEARANCE = os.getenv("CRITERION_CF_CLEARANCE")
TMDB_API_TOKEN = os.getenv("TMDB_API_TOKEN")

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 2048
