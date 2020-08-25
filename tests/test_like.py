# pylint: disable=attribute-defined-outside-init
import pytest

from .test_auth import login
from .utils.assertions import (
    assert_valid_schema,
    assert_valid_status_code
)


class Actions:

    def __init__(self, client):
        self.client = client

    def like(self, quote_id):
        post_data = {'id': quote_id}
        return self.client.post('/v1/likes', data=post_data)

    def unlike(self, quote_id):
        return self.client.delete(f'/v1/likes/{quote_id}')

    def get_favorites(self):
        return self.client.get('/v1/likes')


class TestViewer:

    @pytest.fixture(autouse=True)
    def init(self, client):
        self.actions = Actions(client)

    def test_get_favorites(self):
        resp = self.actions.get_favorites()
        assert_valid_status_code(resp, 401)

    def test_like(self, quote):
        resp = self.actions.like(quote.id)
        assert_valid_status_code(resp, 401)

    def test_unlike(self, quote):
        resp = self.actions.unlike(quote.id)
        assert_valid_status_code(resp, 401)


class TestAuthenticatedUser:

    @pytest.fixture(autouse=True)
    def init(self, client, user):
        login(client, user)
        self.actions = Actions(client)

    def test_get_favorites(self):
        resp = self.actions.get_favorites()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')

    def test_like(self, quote):
        resp = self.actions.like(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

        resp = self.actions.get_favorites()
        assert resp.json['total'] == 1

    def test_unlike(self, quote):
        resp = self.actions.unlike(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

        resp = self.actions.get_favorites()
        assert resp.json['total'] == 0
