"""This module contains user related tests."""

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

    def get_me(self):
        """Gets the current user details."""

        return self.client.get('/v1/users/me')

    def get_user(self, user_id):
        """Gets the user by id."""

        return self.client.get(f'/v1/users/{user_id}')


class TestViewer:
    """Class for testing unauthenticated user."""

    @pytest.fixture(autouse=True)
    def init(self, client):
        """Initializes the actions."""

        # pylint: disable=attribute-defined-outside-init
        self.actions = Actions(client)

    def get_me(self):
        """Tests unauthenticated user getting its details."""

        resp = self.actions.get_me()
        assert_valid_status_code(resp, 401)

    def test_get_user(self, user):
        """Tests unauthenticated user getting other user's details."""

        resp = self.actions.get_user(user.id)
        assert_valid_status_code(resp, 401)


class TestContributor:
    """Class for testing authenticated user."""

    @pytest.fixture(autouse=True)
    def init(self, client, user):
        """Initializes the actions."""

        # pylint: disable=attribute-defined-outside-init
        login(client, user)
        self.actions = Actions(client)

    def get_me(self):
        """Tests authenticated user getting its details."""

        resp = self.actions.get_me()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'user.json')

    def test_get_user(self, user_admin):
        """Tests authenticated user getting other user's details."""

        resp = self.actions.get_user(user_admin.id)
        assert_valid_status_code(resp, 403)


class TestAdmin:
    """Class for testing admin user."""

    @pytest.fixture(autouse=True)
    def init(self, client, user_admin):
        """Initializes the actions."""

        # pylint: disable=attribute-defined-outside-init
        login(client, user_admin)
        self.actions = Actions(client)

    def get_me(self):
        """Tests admin user getting its details."""

        resp = self.actions.get_me()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'user.json')

    def test_get_user(self, user):
        """Tests admin user getting other user's details."""

        resp = self.actions.get_user(user.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'user.json')
