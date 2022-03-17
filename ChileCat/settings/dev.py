'''
Author: 邹洋
Date: 2022-02-12 22:12:23
Email: 2810201146@qq.com
LastEditors:  
LastEditTime: 2022-03-17 22:23:52
Description: 线上环境
'''
from .base import *
DEBUG = True
ASGI_APPLICATION = 'ChileCat.asgidev.application'


password = 'Zhou24272592.' 
host = '127.0.0.1'
 
redis_password = ''
redis_host = "redis://:"+redis_password+"@"+'124.223.43.151'+":8379"

sql_host = host
sql_password = password

# WebSocket
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        "TIMEOUT": None,
        'CONFIG': {
            "hosts": [redis_host + "/2"],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": redis_host + "/1",
        "TIMEOUT": None,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": redis_password,
            "CONNECTION_POOL_KWARGS": {"decode_responses": True,"max_connections": 200},
        }
    }
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ChileCatTest',
        'USER': 'root',
        'PASSWORD': sql_password,
        'HOST': sql_host,
        'PORT': '3306',
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
            'isolation_level': None
        },
    }
}

# 日志配置
log_path = 'D:\\code\\Cat\\ChileCatLog\\'
if not os.path.exists(log_path): os.mkdir(log_path) # 若目录不存在则创建
LOGGING['handlers']['default']['filename'] = os.path.join(log_path, 'all-{}.log'.format(time.strftime('%Y-%m')))
LOGGING['handlers']['error']['filename'] = os.path.join(log_path, 'error-{}.log'.format(time.strftime('%Y-%m')))
LOGGING['handlers']['info']['filename'] = os.path.join(log_path, 'info-{}.log'.format(time.strftime('%Y-%m')))
LOGGING['loggers']['log']['handlers'] = ['default']

# pip install uvicorn
# uvicorn ChileCat.asgi:application --host '0.0.0.0' --port 8000 --reload