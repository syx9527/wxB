"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-#h6ayt-y3=hhk75^-5%3ccn2_w!#9zot1ig9$ftuo5$i*ms7&x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# DEBUG = True

ALLOWED_HOSTS = ["bhynrzjs.mynatapp.cc", '127.0.0.1', "172.18.40.147", "*"]

# Application definition

INSTALLED_APPS = [
    # "adminlteui",
    "simpleui",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework",

    "api.apps.ApiConfig",
    'werkzeug_debugger_runserver',
    'django_extensions',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "wechartdev",
        "PASSWORD": "123456",
        "USER": "root",
        "HOST": "127.0.0.1",
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': "wechartdev",
#         "PASSWORD": "bhyn123456",
#         "USER": "root",
#         "HOST": "127.0.0.1",
#     }
# }



# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-Hans'
# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 配置redis缓存
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        'LOCATION': 'redis://127.0.0.1:6379/0',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100
            },
        },
    },
    # new_wx
    "new_wx": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },

    "user_info": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },

    "base_user": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "new_to_old": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },

}

# 设置验证码缓存时效
CACHES_TIME_OUT = 60 * 5

# 图片访问目录
# 图片访问目录
MEDIA_ROOT = os.path.join(BASE_DIR, "img")
MEDIA_URL = '/img/'
# IMG_ROOT=os.path.join((MEDIA_ROOT))

FOREIGN_WORKERS_DIR = os.path.join(BASE_DIR, "foreign_workers/")

# 配置邮箱服务
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = '1275241305@qq.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = "alvjgjuasbvwibdb"
# 收件人看到的发件人
EMAIL_FROM = '小邵邵'

# APPID = "wxafe035d3c21ea4ef"
# SECRET = "2b8b42cdce57e83bfdcfb3b21fe9b857"

GRANT_TYPE = "authorization_code"

# 恒健
APPID = "wx9169ab3b0af56871"
SECRET = "a6bc811b381bd82a1fefff3cc83761bc"

# 腾讯云短信

# 以下配置信息已全部隐藏个人信息内容
SMS_SECRET_ID = "FSDKNf***********************sDKfSX"  # API秘钥管理SecretId
SMS_SECRET_KEY = "fvszl************************zpislf"  # API秘钥管理SecretKey
SMS_APPID = '1400594329'  # 应用列表SDK AppID
SMS_SIGN = '耿马出入审批'  # 签名管理的内容

# 正文模板管理ID
SMS_TEMPLATE_ID = {
    'login': '123456',  # 登录模板ID
    'register': '123456',  # 注册模板ID
    're_password': '123456',  # 改密模板ID
}

SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False

SIMPLEUI_CONFIG = {
    # 'system_keep':False,
    'dynamic': True, }

# SIMPLEUI_LOGO = '/img/static/img/banner2.png'

# SECURITY安全设置 - 支持http时建议开启
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = True  # 将所有非SSL请求永久重定向到SSL
# SESSION_COOKIE_SECURE = True  # 仅通过https传输cookie
# CSRF_COOKIE_SECURE = True  # 仅通过https传输cookie
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # 严格要求使用https协议传输
# SECURE_HSTS_PRELOAD = True  # HSTS为
# SECURE_HSTS_SECONDS = 60
# SECURE_CONTENT_TYPE_NOSNIFF = True  # 防止浏览器猜测资产的内容类型


#                                _ooOoo_
#                               o8888888o
#                               88" . "88
#                               (| -_- |)
#                               O\  =  /O
#                            ____/`---'\____
#                          .'  \\|     |//  `.
#                         /  \\|||  :  |||//  \
#                        /  _||||| -:- |||||-  \
#                        |   | \\\  -  /// |   |
#                        | \_|  ''\---/''  |   |
#                        \  .-\__  `-`  ___/-. /
#                      ___`. .'  /--.--\  `. . __
#                   ."" '<  `.___\_<|>_/___.'  >'"".
#                  | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#                  \  \ `-.   \_ __\ /__ _/   .-` /  /
#             ======`-.____`-.___\_____/___.-`____.-'======
#                                `=---='
#          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                         佛祖保佑       永无BUG

#                                  .::::.
#                                .::::::::.
#                               :::::::::::
#                            ..:::::::::::'
#                         '::::::::::::'
#                           .::::::::::
#                      '::::::::::::::..
#                           ..::::::::::::.
#                         ``::::::::::::::::
#                          ::::``:::::::::'        .:::.
#                         ::::'   ':::::'       .::::::::.
#                       .::::'      ::::     .:::::::'::::.
#                      .:::'       :::::  .:::::::::' ':::::.
#                     .::'        :::::.:::::::::'      ':::::.
#                    .::'         ::::::::::::::'         ``::::.
#                ...:::           ::::::::::::'              ``::.
#               ```` ':.          ':::::::::'                  ::::..
#                                  '.:::::'                    ':'````..
