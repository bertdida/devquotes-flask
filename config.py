import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'database.sqlite')

    ADMINS = os.environ['ADMINS'].split(',')


class Development(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True


class Production(Config):
    ENV = 'production'
    DEBUG = False
