"""
Django settings for wc project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wo70@zd@^5a8$xom(!n!nw9f-*cxs9pg^(mf_*o9dh6-^^(r^z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG
if DEBUG is False:
    ALLOWED_HOSTS = ['192.168.1.119','*','127.0.0.1','192.168.1.137','192.168.1.151']

if DEBUG is True:
    ALLOWED_HOSTS = ['192.168.1.119', '*','192.168.1.137','192.168.1.151','104.130.29.253']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'weightcalculation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  #'C:/python/automation/calendar/template'
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

WSGI_APPLICATION = 'wc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""
DATABASES = {
        'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'weight',
        'HOST': 'INDXX-194',
        'PASSWORD': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 11 for SQL Server',
        }
    }
}
# 'default': {
# 	 'ENGINE': 'sql_server.pyodbc',
# 	 'NAME': 'index_automation',
# 	 'HOST': '162.242.166.128',
# 	 #'PORT': 1433,
# 	 'USER': 'Database',
# 	 'PASSWORD': 'Welcome.1',
# 	 'OPTIONS': {
# 		 'host_is_server': True,
# 		 'driver':'ODBC Driver 11 for SQL Server',
# 	 }
# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
SITE_ROOT = PROJECT_ROOT

MEDIA_DIR = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'



STATICFILES_DIRS = (
                os.path.join(BASE_DIR,'staticfiles'), # if your static files folder is named "staticfiles"
)

MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'

DATE_INPUT_FORMATS = ['%d-%m-%Y']
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = '/accounts/login/'