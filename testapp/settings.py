# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOCAL_CACHE_ROOT = "cache"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "testapp_installed",
    "testapp",
]

TEMPLATES = []

SECRET_KEY = "testing"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "",
    }
}

TEST_SETTINGS_FOLDERS = ["testapp"]
