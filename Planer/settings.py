import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Der Pfad für MEDIA_ROOT sollte das Basisverzeichnis plus den 'media'-Ordner sein.
# Keine Notwendigkeit, 'Planer' hier einzuschließen, da dies Teil der URL, nicht des Dateipfads ist.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# MEDIA_URL definiert, wie die URLs für Medien-Dateien aussehen sollen.
# Da du '/Planer/media/' nutzen möchtest, setze dies entsprechend.
MEDIA_URL = '/Planer/media/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-t8pc16-t!zterq7qozjbjrv&wjh7lz=%9w@7bcz26#_^n8jty0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['planer4-e93a8s4x.b4a.run','node85a.containers.back4app.com', 'localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Terrassenplaner',
    'import_export',
    'bootstrap4',
    'debug_toolbar',
    'crispy_forms',
    'widget_tweaks',
    'corsheaders',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'Planer.urls'

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

WSGI_APPLICATION = 'Planer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# URL, unter der die statischen Dateien erreichbar sein werden
STATIC_URL = '/static/'

# Definiere das Verzeichnis, in dem Django nach statischen Dateien sucht
# Das beinhaltet deine App-Verzeichnisse und ein zentrales 'static'-Verzeichnis
STATICFILES_DIRS = [
    BASE_DIR / 'Terrassenplaner' / 'static',  # Pfad zu den statischen Dateien deiner App
    # Hier könntest du weitere Verzeichnisse hinzufügen
]

# Definiere den Ort, an dem statische Dateien gesammelt werden
# Wichtig für Produktionsumgebungen
STATIC_ROOT = BASE_DIR / 'staticfiles'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}
# Django CSRF-Schutz: CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1', 'http://localhost', 'http://node84a.containers.back4app.com', 'https://planer4-e93a8s4x.b4a.run']

# CORS-Konfiguration: CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS = ['http://127.0.0.1', 'http://localhost', 'http://node84a.containers.back4app.com', 'https://planer4-e93a8s4x.b4a.run']

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CUSTOM_TEMP_DIR = os.path.join(BASE_DIR, 'tmp')
