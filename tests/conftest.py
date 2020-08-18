import json
import os
from contextlib import contextmanager

import pytest
import testing.postgresql as postgresql
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.mapper import configure_mappers

import config
from devquotes import create_app
from devquotes.models import db
from devquotes.models.quote import Quote
from devquotes.models.quote_status import QuoteStatus
from devquotes.models.user import User

dir_path = os.path.dirname(os.path.realpath(__file__))

seed_configs = [
    {
        'model': User,
        'filename': 'users.json',
    },
    {
        'model': QuoteStatus,
        'filename': 'status.json',
    },
    {
        'model': Quote,
        'filename': 'quotes.json',
    }
]


def load_data(filename):
    with open(f'{dir_path}/data/{filename}') as data_file:
        return json.load(data_file)


def create_model(model, data):
    # https://stackoverflow.com/a/52638766/8062659
    return model.create(**{
        k: v for k, v in data.items()
        if k in class_mapper(model).attrs.keys()
    })


@contextmanager
def db_session_no_expire():
    # https://stackoverflow.com/a/51452451/8062659
    session = db.session()
    session.expire_on_commit = False
    try:
        yield
    finally:
        session.expire_on_commit = True


@pytest.fixture(name='postgres', scope='session')
def setup_and_teardown_postgres():
    Postgresql = postgresql.PostgresqlFactory(cache_initialized_db=True)

    postgres = Postgresql()
    yield postgres

    postgres.stop()
    Postgresql.clear_cache()


@pytest.fixture(name='app', scope='session')
def setup_and_teardown_app(postgres):
    class TestingConfig(config.Testing):
        SQLALCHEMY_DATABASE_URI = postgres.url()

    return create_app(TestingConfig)


@pytest.fixture(name='database', scope='module', autouse=True)
def setup_and_teardown_database(app):
    with app.app_context():
        configure_mappers()
        db.create_all()

    yield db
    db.drop_all()


@pytest.fixture(name='seed', scope='module', autouse=True)
def seed(database, app):
    for seed_config in seed_configs:
        model, filename = seed_config.values()
        data = load_data(filename)

        for dict_data in data:
            with app.app_context(), db_session_no_expire():
                create_model(model, dict_data)

    yield

    # must truncate `quote` table first to avoid
    # foreign key violation
    Quote.query.delete()
    QuoteStatus.query.delete()
    User.query.delete()
    db.session.commit()


@pytest.fixture(name='user', scope='module')
def setup_and_teardown_user():
    yield User.get_by(first=True, is_admin=False)


@pytest.fixture(name='user_admin', scope='module')
def setup_and_teardown_user_admin():
    yield User.get_by(first=True, is_admin=True)


@pytest.fixture(name='quote_statuses', scope='module')
def setup_and_teardown_quote_statuses():
    yield QuoteStatus.query.all()


@pytest.fixture(name='quotes', scope='module')
def setup_and_teardown_quotes():
    yield Quote.query.all()


@pytest.fixture(name='quote', scope='module')
def setup_and_teardown_quote():
    return Quote.query.first()


@pytest.fixture(name='client', scope='session')
def setup_and_teardown_client(app):
    return app.test_client()


@pytest.fixture(name='client_admin', scope='module')
def setup_and_teardown_client_admin(app, user_admin):
    client = app.test_client()

    identity = {
        'firebase_user_id': user_admin.firebase_user_id,
        'is_admin': user_admin.is_admin,
        'id': user_admin.id,
    }

    access_token = create_access_token(identity)
    refresh_token = create_refresh_token(identity)

    client.set_cookie('localhost', 'access_token_cookie', access_token)
    client.set_cookie('localhost', 'refresh_token_cookie', refresh_token)

    yield client
    client.cookie_jar.clear()
