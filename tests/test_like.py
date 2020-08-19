# pylint: disable=attribute-defined-outside-init
import pytest

from .test_auth import login
from .utils.assertions import (
    assert_valid_schema,
    assert_valid_status_code
)


class Actions:

    def __init__(self, client, quote):
        self.client = client
        self.quote = quote

    def like(self):
        post_data = {'id': self.quote.id}
        return self.client.post('/v1/likes', data=post_data)

    def unlike(self):
        return self.client.delete(f'/v1/likes/{self.quote.id}')

    def get_favorites(self):
        return self.client.get('/v1/likes')


class TestViewer:

    @pytest.fixture(autouse=True)
    def init(self, client, quote):
        self.actions = Actions(client, quote)

    def test_like(self):
        resp = self.actions.like()
        assert_valid_status_code(resp, 401)

    def test_unlike(self):
        resp = self.actions.unlike()
        assert_valid_status_code(resp, 401)

    def test_get_favorites(self):
        resp = self.actions.get_favorites()
        assert_valid_status_code(resp, 401)


class TestContributor:

    @pytest.fixture(autouse=True)
    def init(self, client, quote, user):
        login(client, user)
        self.actions = Actions(client, quote)

    def test_like(self):
        resp = self.actions.like()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

        resp = self.actions.get_favorites()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')
        assert resp.json['total'] == 1

    def test_unlike(self):
        resp = self.actions.unlike()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

        resp = self.actions.get_favorites()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')
        assert resp.json['total'] == 0

    def test_get_favorites(self):
        resp = self.actions.get_favorites()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')
