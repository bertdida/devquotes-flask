"""This module defines the app's configuration classes."""

import os

# pylint: disable=too-few-public-methods


class Config:
    """Default configurations."""

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

    # this value should match the name on `quote_status` seeder
    PUBLISHED_STATUS_NAME = 'published'


class Development(Config):
    """Development configurations."""

    ENV = 'development'
    DEBUG = True
    SERVER_NAME = os.environ.get('SERVER_NAME')

    SQLALCHEMY_ECHO = True
    JWT_ACCESS_TOKEN_EXPIRES = 10  # seconds
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False


class Production(Config):
    """Production configurations."""

    ENV = 'production'
    DEBUG = False

    # workaround for ExpiredSignatureError raising
    # 500 status code instead of 401
    # https://github.com/vimalloc/flask-jwt-extended/issues/20
    # https://github.com/vimalloc/flask-jwt-extended/issues/86
    PROPAGATE_EXCEPTIONS = True


class Testing(Config):
    """Testing configurations."""

    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
