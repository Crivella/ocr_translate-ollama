"""Minimal django settings for tests."""
INSTALLED_APPS = [
    'ocr_translate',
    'ocr_translate_ollama'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

USE_TZ = True
