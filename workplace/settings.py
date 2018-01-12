import logging
import os

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

DEBUG = False

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)

SECRET_KEY = os.environ['SECRET_KEY']

DATABASE = {
    'database': os.environ['PG_DATABASE'],
    'password': os.environ['PG_PASSWORD'],
    'user': os.environ['PG_USER'],
    'host': os.environ['PG_HOST'],
}

REDIS = {
    'host': os.environ['REDIS_HOST'],
    'port': os.environ['REDIS_PORT'],
}

REDIRECT_URI = os.environ['REDIRECT_URI']
OAUTH_REDIRECT_PATH = '/oauth/login'  # path of oauth callback in your app
OAUTH_ID = os.environ['OAUTH_ID']
OAUTH_SECRET = os.environ['OAUTH_SECRET']
OAUTH_CACHE_EXPIRE = 3600

try:
    from .settings_local import *  # noqa
except ImportError:
    pass
