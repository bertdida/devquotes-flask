from contextlib import contextmanager

import pytest
import testing.postgresql as postgresql
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.orm.mapper import configure_mappers

import config
from devquotes import create_app
from devquotes.models import db
from devquotes.models.quote import Quote
from devquotes.models.quote_status import QuoteStatus
from devquotes.models.user import User

INITIAL_ADMIN = {
    'firebase_user_id': 'firebaseuserid',
    'firebase_jwt': 'firebasejwt',
    'name': 'Herbert Verdida',
    'is_admin': True,
}

INITIAL_QUOTE_STATUSES = [
    {
        'name': 'published',
        'display_name': 'Published',
    },
    {
        'name': 'pending_review',
        'display_name': 'Pending Review',
    },
]

INITIAL_QUOTES = [
    {
        'author': 'Linus Torvalds',
        'quotation': 'Talk is cheap. Show me the code.',
        'source': 'https://lkml.org/lkml/2000/8/25/132',
        'status': INITIAL_QUOTE_STATUSES[0]['name'],
    },
    {
        'author': 'Tim Kadlec',
        'quotation': 'Blame the implementation, not the technique.',
        'status': INITIAL_QUOTE_STATUSES[1]['name'],
    }
]


@pytest.fixture(name='initial_admin', scope='session')
def setup_and_teardown_initial_admin():
    return INITIAL_ADMIN


@pytest.fixture(name='initial_quote_statuses', scope='session')
def setup_and_teardown_initial_quote_statuses():
    return INITIAL_QUOTE_STATUSES


@pytest.fixture(name='initial_quotes', scope='session')
def setup_and_teardown_initial_quotes():
    return INITIAL_QUOTES


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


@pytest.fixture(name='client', scope='session')
def setup_and_teardown_client(app):
    return app.test_client()


@contextmanager
def db_session_no_expire():
    # https://stackoverflow.com/a/51452451/8062659
    session = db.session()
    session.expire_on_commit = False
    try:
        yield
    finally:
        session.expire_on_commit = True


@pytest.fixture(name='user_admin', scope='module', autouse=True)
def setup_and_teardown_user_admin(app, initial_admin):
    admin_copy = dict(initial_admin)
    admin_copy.pop('firebase_jwt')

    with app.app_context(), db_session_no_expire():
        user = User.create(**admin_copy)

    yield user
    user.delete()


@pytest.fixture(name='quote_statuses', scope='module', autouse=True)
def setup_and_teardown_quote_statuses(app, initial_quote_statuses):
    with app.app_context(), db_session_no_expire():
        for data in initial_quote_statuses:
            QuoteStatus.create(**data)

    yield QuoteStatus.query.all()

    QuoteStatus.query.delete()
    db.session.commit()


@pytest.fixture(name='quotes', scope='module', autouse=True)
def setup_and_teardown_quotes(app, initial_quotes, user_admin):
    with app.app_context(), db_session_no_expire():
        for data in initial_quotes:
            data_copy = dict(data)
            status_name = data_copy.pop('status')

            status = QuoteStatus.get_by(first=True, name=status_name)
            Quote.create(**data_copy, contributor=user_admin, status=status)

    yield Quote.query.all()

    Quote.query.delete()
    db.session.commit()


@pytest.fixture(name='quote', scope='module')
def setup_and_teardown_quote():
    return Quote.query.first()


@pytest.fixture(name='client_admin', scope='module')
def setup_and_teardown_client_admin(client, user_admin):
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
