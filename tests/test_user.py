# pylint: disable=attribute-defined-outside-init
import pytest

from .test_auth import login

from .utils.assertions import assert_valid_schema, assert_valid_status_code


class Actions:

    def __init__(self, client):
        self.client = client

    def get_me(self):
        return self.client.get('/v1/users/me')

    def get_user(self, user_id):
        return self.client.get(f'/v1/users/{user_id}')


class TestViewer:

    @pytest.fixture(autouse=True)
    def init(self, client):
        self.actions = Actions(client)

    def get_me(self):
        resp = self.actions.get_me()
        assert_valid_status_code(resp, 401)

    def test_get_user(self, user):
        resp = self.actions.get_user(user.id)
        assert_valid_status_code(resp, 401)


class TestContributor:

    @pytest.fixture(autouse=True)
    def init(self, client, user):
        login(client, user)
        self.actions = Actions(client)

    def get_me(self):
        resp = self.actions.get_me()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'user.json')

    def test_get_user(self, user_admin):
        resp = self.actions.get_user(user_admin.id)
        assert_valid_status_code(resp, 403)


class TestAdmin:

    @pytest.fixture(autouse=True)
    def init(self, client, user_admin):
        login(client, user_admin)
        self.actions = Actions(client)

    def get_me(self):
        resp = self.actions.get_me()
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'user.json')

    def test_get_user(self, user):
        resp = self.actions.get_user(user.id)
        assert_valid_status_code(resp, 200)
        assert_valid_schema(resp, 'user.json')
