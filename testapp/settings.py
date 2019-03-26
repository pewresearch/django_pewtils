# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "testapp"
]

TEMPLATES = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SECRET_KEY = "testing"