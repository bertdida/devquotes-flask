"""This module contains authorization related tests."""

from unittest import mock


def login(client, user):
    """Helper for logging in user."""

    with mock.patch('devquotes.routes.auth.auth.verify_id_token') as magic_mock:
        magic_mock.return_value = {
            'user_id': user.firebase_user_id,
        }
        post_data = {
            'token': 'firebase_user_id_token'
        }

        return client.post('/v1/auth/token', data=post_data)


def logout(client):
    """Helper for logging out user."""

    return client.post('/v1/auth/revoke')


def test_token(client, user):
    """Tests login."""

    resp = login(client, user)
    cookie_names = [cookie.name for cookie in client.cookie_jar]

    assert resp.status_code == 200
    assert 'access_token_cookie' in cookie_names
    assert 'refresh_token_cookie' in cookie_names


def test_refresh(client, user):
    """Tests refreshing token."""

    login(client, user)

    resp = client.post('/v1/auth/refresh')
    cookie_names = [cookie.name for cookie in client.cookie_jar]

    assert resp.status_code == 200
    assert 'access_token_cookie' in cookie_names
    assert 'refresh_token_cookie' in cookie_names


def test_revoke(client, user):
    """Tests revoking token."""

    login(client, user)

    resp = logout(client)
    cookie_names = [cookie.name for cookie in client.cookie_jar]

    assert resp.status_code == 204
    assert 'access_token_cookie' not in cookie_names
    assert 'refresh_token_cookie' not in cookie_names
