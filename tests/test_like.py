"""This module contains like related tests."""

import pytest

from .test_auth import login
from .utils.assertions import (
    assert_valid_schema,
    assert_valid_status_code
)


class Actions:
    """Class for common actions."""

    def __init__(self, client):
        self.client = client

    def like(self, quote_id):
        """Likes quote."""

        post_data = {'id': quote_id}
        return self.client.post('/v1/likes', data=post_data)

    def unlike(self, quote_id):
        """Unlikes quote."""

        return self.client.delete(f'/v1/likes/{quote_id}')

    def get_favorites(self):
        """Gets all liked quotes."""

        return self.client.get('/v1/likes')


class TestViewer:
    """Class for testing unauthenticated user."""

    @pytest.fixture(autouse=True)
    def init(self, client):
        """Initializes the actions."""

        # pylint: disable=attribute-defined-outside-init
        self.actions = Actions(client)

    def test_get_favorites(self):
        """Tests unauthenticated user getting its liked quotes."""

        resp = self.actions.get_favorites()
        assert_valid_status_code(resp, 401)

    def test_like(self, quote):
        """Tests unauthenticated user liking a quote."""

        resp = self.actions.like(quote.id)
        assert_valid_status_code(resp, 401)

    def test_unlike(self, quote):
        """Tests unauthenticated user unliking a quote."""

        resp = self.actions.unlike(quote.id)
        assert_valid_status_code(resp, 401)


class TestAuthenticatedUser:
    """Class for testing authenticated user."""

    @pytest.fixture(autouse=True)
    def init(self, client, user):
        """Initializes the actions."""

        # pylint: disable=attribute-defined-outside-init
        login(client, user)
        self.actions = Actions(client)

    def test_get_favorites(self):
        """Tests authenticated user getting its liked quotes."""

        resp = self.actions.get_favorites()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quotes.json')

    def test_like(self, quote):
        """Tests unauthenticated user liking a quote."""

        resp = self.actions.like(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

        resp = self.actions.get_favorites()
        assert resp.json['total'] == 1

    def test_unlike(self, quote):
        """Tests authenticated user unliking a quote."""

        resp = self.actions.unlike(quote.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'quote.json')

        resp = self.actions.get_favorites()
        assert resp.json['total'] == 0
