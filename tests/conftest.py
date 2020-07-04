import pytest
from contextlib import contextmanager

from flask_jwt_extended import create_access_token, create_refresh_token
import testing.postgresql as postgresql

import config
from devquotes import create_app
from devquotes.models import db
from devquotes.models.quote import Quote
from devquotes.models.user import User

MOCK_FIREBASE_USER_ID = 'firebaseuserid'
MOCK_FIREBASE_JWT = 'firebasejwt'


@pytest.fixture(name='firebase_user_id', scope='session')
def setup_and_teardown_user_id():
    return MOCK_FIREBASE_USER_ID


@pytest.fixture(name='firebase_jwt', scope='session')
def setup_and_teardown_jwt():
    return MOCK_FIREBASE_JWT


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


@pytest.fixture(name='quote', scope='module', autouse=True)
def setup_and_teardown_quote(app):
    data = {
        'author': 'Linus Torvalds',
        'quotation': 'Talk is cheap. Show me the code.',
        'source': 'https://lkml.org/lkml/2000/8/25/132',
    }

    with app.app_context():
        quote = Quote.create(**data)

    yield quote
    quote.delete()


@pytest.fixture(name='admin_user', scope='module', autouse=True)
def setup_and_teardown_firebase_admin_user(app, firebase_user_id):
    data = {
        'firebase_user_id': firebase_user_id,
        'is_admin': True,
    }

    with app.app_context(), db_session_no_expire():
        user = User.create(**data)

    yield user
    user.delete()


@pytest.fixture(name='client_admin', scope='module')
def setup_and_teardown_client_admin(client, admin_user):
    identity = {
        'firebase_user_id': admin_user.firebase_user_id,
        'is_admin': admin_user.is_admin,
        'id': admin_user.id,
    }

    access_token = create_access_token(identity)
    refresh_token = create_refresh_token(identity)

    client.set_cookie('localhost', 'access_token_cookie', access_token)
    client.set_cookie('localhost', 'refresh_token_cookie', refresh_token)

    yield client
    client.cookie_jar.clear()
