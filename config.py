import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ['SECRET_KEY']

    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_TOKEN_LOCATION = 'cookies'
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ERROR_MESSAGE_KEY = 'message'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'database.sqlite')

    ADMINS = os.environ['ADMINS'].split(',')
    FIREBASE_CREDENTIAL = os.environ['FIREBASE_CREDENTIAL']

    ELASTICSEARCH_URL = os.environ.get('AWS_ELASTICSEARCH_URL')
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    AWS_REGION = os.environ.get('AWS_REGION')


class Development(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')


class Production(Config):
    ENV = 'production'
    DEBUG = False


class Testing(Config):
    TESTING = True
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
