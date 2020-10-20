"""This module contains the fixtures used across tests."""

import json
import os
from contextlib import contextmanager

import pytest
import testing.postgresql as postgresql
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


@pytest.fixture(name='postgres', scope='session')
def setup_and_teardown_postgres():
    """Setups and teardowns for postgresql."""

    # pylint: disable=invalid-name
    Postgresql = postgresql.PostgresqlFactory(cache_initialized_db=True)

    postgres = Postgresql()
    yield postgres

    postgres.stop()
    Postgresql.clear_cache()


@contextmanager
def db_session_no_expire():
    """Temporarily turn `expire_on_commit` off."""

    # https://stackoverflow.com/a/51452451/8062659
    session = db.session()
    session.expire_on_commit = False
    try:
        yield
    finally:
        session.expire_on_commit = True


@pytest.fixture(name='app', scope='session')
def setup_and_teardown_app(postgres):
    """Setups and teardowns for the application."""

    # pylint: disable=too-few-public-methods
    class TestingConfig(config.Testing):
        """Application config to use."""

        SQLALCHEMY_DATABASE_URI = postgres.url()

    return create_app(TestingConfig)


@pytest.fixture(name='database', scope='module', autouse=True)
def setup_and_teardown_database(app):
    """Setups and teardowns for the database."""

    with app.app_context():
        configure_mappers()
        db.create_all()

    yield db
    db.drop_all()


@pytest.fixture(name='seed', scope='module', autouse=True)
def seed(database, app):  # pylint: disable=unused-argument
    """Seeds the database."""

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
    """Setups and teardowns for a user."""

    yield User.get_by(first=True, is_admin=False)


@pytest.fixture(name='user_admin', scope='module')
def setup_and_teardown_user_admin():
    """Setups and teardowns for an admin user."""

    yield User.get_by(first=True, is_admin=True)


@pytest.fixture(name='quotes', scope='module')
def setup_and_teardown_quotes():
    """Setups and teardowns for quotes."""

    yield Quote.query.all()


@pytest.fixture(name='quote', scope='module')
def setup_and_teardown_quote():
    """Setups and teardowns for quote."""

    return Quote.query.first()


@pytest.fixture(name='client', scope='function')
def setup_and_teardown_client(app):
    """Setups and teardowns for app's client."""

    return app.test_client()


def load_data(filename):
    """Loads the JSON data for the given `filename`"""

    with open(f'{dir_path}/data/{filename}') as data_file:
        return json.load(data_file)


def create_model(model, data):
    """A helper that creates a model ignoring the unsupported
    keys from the `data`."""

    # https://stackoverflow.com/a/52638766/8062659
    return model.create(**{
        k: v for k, v in data.items()
        if k in class_mapper(model).attrs.keys()
    })
