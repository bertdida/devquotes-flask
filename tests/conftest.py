import json

import pytest

from devquotes import create_app
from devquotes.models import db
from devquotes.models.quote import Quote


@pytest.fixture(scope='module')
def client():
    app = create_app('config.Testing')
    testing_client = app.test_client()

    with app.app_context():
        db.create_all()

    yield testing_client
    db.drop_all()


@pytest.fixture(scope='function')
def create_quotes():
    with open('./tests/utils/data/quotes.json') as json_file:
        quotes = json.load(json_file)
        for data in quotes:
            Quote.create(**data)

    yield
    Quote.query.delete()
