from pathlib import Path
from dotenv import load_dotenv
import os
from dj_database_url import parse
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# 環境変数.envの読み込み
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# .envファイルの読み込みを確実に行う
load_dotenv(override=True)  # override=True を追加
# または以下のように詳細な設定も可能
load_dotenv(
    dotenv_path=BASE_DIR / '.env',
    override=True,
    verbose=True  # 読み込み状況をログ出力
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
# DEBUG = os.environ['DEBUG']
DEBUG = os.environ['DEBUG'].lower() == 'true'
# print(DEBUG)
# ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'toilet',
    'line_app',
    'lp',
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

ROOT_URLCONF = 'toiletproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'toilet.context_processors.common'
            ],
        },
    },
]

WSGI_APPLICATION = 'toiletproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        # localの場合はsqlite3を使用するように設定
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # DATABASE_URL 環境変数を取得
    DATABASES = {
        'default': parse(os.getenv('DATABASE_URL'))
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'assets')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL)

# 認証用のモデルとして設定
AUTH_USER_MODEL = 'accounts.User'

# ログインデフォルトURL
LOGIN_URL = 'accounts/user_login'

# LINE 環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']
LINE_LIFF_ID = os.environ['LINE_LIFF_ID']

# CSRF許可
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

# 開発環境
if DEBUG:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = os.environ['SECRET_KEY']

    # ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']
    # ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0:8000', 'localhost']

    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # メールの内容をコンソールに表示する。
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media') #djangoappプロジェクトフォルダ配下のmediaフォルダを指定。
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com' # GmailのSMTPサーバー
    EMAIL_PORT = 587 # Gmailサーバーのポート番号
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_USE_TLS = True # SMTPサーバーと通信する際に、TLS（セキュア）接続する

# 本番環境
if not DEBUG:
    SECRET_KEY = os.environ['SECRET_KEY']
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '')
    ALLOWED_HOSTS = ALLOWED_HOSTS.split(',') if ALLOWED_HOSTS else []
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com' # GmailのSMTPサーバー
    EMAIL_PORT = 587 # Gmailサーバーのポート番号
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_USE_TLS = True # SMTPサーバーと通信する際に、TLS（セキュア）接続する

# sentryの導入でエラーを検知する（sentryのウェブサイトでエラーの確認可能）
sentry_sdk.init(
    dsn=os.environ['DSN'],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)