# Django settings for speedjob project.
import os
import sys

# DEBUG = True
DEBUG = False
TEMPLATE_DEBUG = False
# TEMPLATE_DEBUG = DEBUG
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

ADMINS = (
        # ('Your Name', 'your_email@example.com'),
        )

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['speedjob.fr']

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr-FR'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
# USE_TZ = False

# ADMIN_MEDIA_PREFIX = '/static/admin/'
# MEDIA_ROOT    = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'media'))
# MEDIA_URL = '/media/'
# STATIC_ROOT = ''
# STATIC_ROOT = os.path.join( PROJECT_ROOT,  'static' )

MEDIA_ROOT  = '/kunden/homepages/11/d445074125/htdocs/media'
MEDIA_URL   = '/media/'
STATIC_ROOT = '/kunden/homepages/11/d445074125/htdocs/static'

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    # os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'static')),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = '2#3h@cf6osxw2r7)vd^e487ur@_5l%#39b&amp;^z8brsu9t44s4w%'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

PREPEND_WWW = True

ROOT_URLCONF = 'speedjob.urls'

WSGI_APPLICATION = 'speedjob.wsgi.application'

TEMPLATE_DIRS = (
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates')),
)

FIXTURE_DIRS = (os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', "fixtures")), )

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'utils.context_processors.get_user_status',
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suit',
    'django.contrib.admin',
    'crispy_forms',
    'payments',
    'main',
    'car_shop',
    'registration',
    'profile',
    'article',
    'offre',
    'debug_toolbar',
    'django.contrib.sitemaps',
)

# admin settings
SUIT_CONFIG = {
    'ADMIN_NAME': 'SpeedJob administration',
    'SHOW_REQUIRED_ASTERISK': True,
    'MENU_ICONS': {
        'sites': 'icon-leaf',
        'auth': 'icon-lock',
    },
    'MENU_OPEN_FIRST_CHILD': True,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'fqa.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            # 'class': 'ssweb.logger.FQAdminEmailHandler',
            'class': 'logging.StreamHandler',
        },
        'null': {
            'level': 'DEBUG',
            'class':'django.utils.log.NullHandler',
            },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
    },


    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console', 'default'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level':'DEBUG',
        },
        '': {
            'handlers': ['default', 'console'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

# profile settigns
AUTH_PROFILE_MODULE = "profile.ExUserProfile"
# now you are basically on your own .
# the django.contrib.auth framework can not help any more

LOGIN_REDIRECT_URL = '/profile_login'

# registration settigns
REGISTRATION_OPEN = True
ACCOUNT_ACTIVATION_DAYS = 14

# email configuration

EMAIL_USE_TLS = True
EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587


# Stripe payments

PAYMENTS_INVOICE_FROM_EMAIL = 'redatest7@gmail.com'

PAYMENTS_PLANS = {
    "mensuel": {
        "stripe_plan_id": "mensuel",
        "name": "mensuel",
        "description": "Abonnement mensuel",
        "price": 40,
        "currency": "eur",
        "interval": "month"
    },

    "annuel": {
        "stripe_plan_id": "annuel",
        "name": "annuel",
        "description": "Abonnement annuel",
        "price": 130,
        "currency": "eur",
        "interval": "year",
    },
}

# caching settings
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'caching/files'))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': CACHE_DIR,
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
