import os


class Config:
    SECRET_KEY = os.environ['SECRET_KEY']

    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_TOKEN_LOCATION = 'cookies'
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ERROR_MESSAGE_KEY = 'message'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        os.environ['SQLALCHEMY_DATABASE_URI']

    ADMINS = os.environ['ADMINS'].split(',')
    FIREBASE_CREDENTIAL = os.environ['FIREBASE_CREDENTIAL']

    ALLOWED_ORIGINS = os.environ['ALLOWED_ORIGINS'].split(',')


class Development(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True
    JWT_COOKIE_SECURE = False
    JWT_ACCESS_TOKEN_EXPIRES = 10  # seconds


class Production(Config):
    ENV = 'production'
    DEBUG = False

    # workaround for ExpiredSignatureError raising
    # 500 status code instead of 401
    # https://github.com/vimalloc/flask-jwt-extended/issues/20
    # https://github.com/vimalloc/flask-jwt-extended/issues/86
    PROPAGATE_EXCEPTIONS = True


class Testing(Config):
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
