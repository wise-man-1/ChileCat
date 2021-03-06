"""
Django settings for ChileCat project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
# import os
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static")
# ]
# 获取环境数值
ENV_PROFILE = os.getenv("ENV")



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b-u)^cel(1#+=&ian1b2m0e07hr*k8^96fuh*tq+cf^+!!__qd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'Apps.Ask',
    'Apps.User',
    'Apps.Career',
    'Apps.Life',
    'Apps.Permission',
    'Manage',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 跨域
    'django.middleware.common.CommonMiddleware',  # 跨域
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'Manage.utils.middleware.LoadUserObject',
]

ROOT_URLCONF = 'ChileCat.urls'

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
                # 'Manage.utils.context_processors.get_permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'ChileCat.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if ENV_PROFILE == "production":   
    # 生产环境
    db_url = "chilecat_1"
else:
    db_url = "chilecat_qiuzhe_test"
    # db_url = "chilecat_1"


DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': str(os.path.join(BASE_DIR, "db.sqlite3"))
        'ENGINE': 'django.db.backends.mysql',
        'NAME': db_url,
        'USER': 'root',
        'PASSWORD': '314418',
        'HOST': '47.111.1.18',
        'PORT': '3306'
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = ('*')#跨域增加忽略
# 跨域允许的请求方式(可选)
CORS_ALLOW_METHODS = ('DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'VIEW',)
# 跨域允许的头部参数(可选)
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
    'access-control-allow-origin',
    'Access-Control-Allow-Origin',
    'token',
)

# JWT 密钥
SECRET_KEY = 'AHABsyAS.ASD.?SA&&w1dsa.1.sdssagrh.;ASLKI'

# 全局权限控制
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        "Apps.Permission.utils.auth.AuthPermission",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
       "Apps.Permission.utils.permission.ApiPublicPermission",
    ],
    'EXCEPTION_HANDLER': 'Apps.Permission.utils.expand_permission.custom_exception_handler',
}
