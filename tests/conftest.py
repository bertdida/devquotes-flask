from contextlib import contextmanager

import pytest
import testing.postgresql as postgresql
from flask_jwt_extended import create_access_token, create_refresh_token

import config
from devquotes import create_app
from devquotes.models import db
from devquotes.models.quote import Quote
from devquotes.models.user import User

INITIAL_ADMIN_DATA = {
    'firebase_user_id': 'firebaseuserid',
    'firebase_jwt': 'firebasejwt',
    'is_admin': True,
}

INITIAL_QUOTES_DATA = [
    {
        'author': 'Linus Torvalds',
        'quotation': 'Talk is cheap. Show me the code.',
        'source': 'https://lkml.org/lkml/2000/8/25/132',
        'is_published': True,
    },
    {
        'author': 'Tim Kadlec',
        'quotation': 'Blame the implementation, not the technique.',
    }
]


@pytest.fixture(name='initial_admin_data', scope='session')
def setup_and_teardown_initial_admin_data():
    return INITIAL_ADMIN_DATA


@pytest.fixture(name='initial_quotes_data', scope='session')
def setup_and_teardown_initial_quotes_data():
    return INITIAL_QUOTES_DATA


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


@pytest.fixture(name='quotes', scope='module', autouse=True)
def setup_and_teardown_quotes(app, initial_quotes_data):
    with app.app_context(), db_session_no_expire():
        for data in initial_quotes_data:
            Quote.create(**data)

    yield Quote.query.all()

    Quote.query.delete()
    db.session.commit()


@pytest.fixture(name='quote', scope='module')
def setup_and_teardown_quote():
    return Quote.query.first()


@pytest.fixture(name='user_admin', scope='module', autouse=True)
def setup_and_teardown_user_admin(app, initial_admin_data):
    admin_data_copy = dict(initial_admin_data)
    admin_data_copy.pop('firebase_jwt')

    with app.app_context(), db_session_no_expire():
        user = User.create(**admin_data_copy)

    yield user
    user.delete()


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
