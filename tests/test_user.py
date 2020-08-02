from .utils.assertions import assert_valid_schema


def test_get_user(client, user_admin):
    resp = client.get('/v1/users/{0.id}'.format(user_admin))
    assert resp.status_code == 401


def test_admin_get_user(client_admin, user_admin):
    resp = client_admin.get('/v1/users/{0.id}'.format(user_admin))

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'user.json')


def test_unauthorized_get_me(client):
    resp = client.get('/v1/users/me')
    assert resp.status_code == 401


def test_authorized_get_me(client_admin):
    resp = client_admin.get('/v1/users/me')

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'user.json')
