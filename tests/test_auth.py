from unittest import mock


def test_token(client, user_admin):
    with mock.patch('devquotes.routes.auth.auth.verify_id_token') as magic_mock:
        magic_mock.return_value = {
            'user_id': user_admin.firebase_user_id,
        }

        post_data = {
            'token': 'firebase_user_id_token'
        }

        resp = client.post('/v1/auth/token', data=post_data)
        cookie_names = [cookie.name for cookie in client.cookie_jar]

    assert resp.status_code == 200
    assert 'access_token_cookie' in cookie_names
    assert 'refresh_token_cookie' in cookie_names


def test_refresh(client):
    resp = client.post('/v1/auth/refresh')
    cookie_names = [cookie.name for cookie in client.cookie_jar]

    assert resp.status_code == 200
    assert 'access_token_cookie' in cookie_names
    assert 'refresh_token_cookie' in cookie_names


def test_revoke(client):
    resp = client.post('/v1/auth/revoke')
    cookie_names = [cookie.name for cookie in client.cookie_jar]

    assert resp.status_code == 204
    assert 'access_token_cookie' not in cookie_names
    assert 'refresh_token_cookie' not in cookie_names
