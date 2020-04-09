from .utils.assertions import assert_valid_schema


def test_create_like(client):
    post_data = {
        'id': 1
    }

    resp = client.post('/v1/likes', data=post_data)
    assert resp.status_code == 401


def test_get_likes(client):
    resp = client.get('/v1/likes')
    assert resp.status_code == 401


def test_delete_like(client):
    resp = client.delete('/v1/likes/1')
    assert resp.status_code == 401


def test_create_like_admin(client_admin):
    post_data = {
        'id': 1
    }

    resp = client_admin.post('/v1/likes', data=post_data)

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quote.json')


def test_get_likes_admin(client_admin):
    resp = client_admin.get('/v1/likes')

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quotes.json')


def test_delete_like_admin(client_admin):
    resp = client_admin.delete('/v1/likes/1')

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quote.json')
