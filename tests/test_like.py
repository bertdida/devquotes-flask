from .utils.assertions import assert_valid_schema


def test_unauthorized_like(client, quote):
    post_data = {
        'id': quote.id
    }

    resp = client.post('/v1/likes', data=post_data)
    assert resp.status_code == 401


def test_unauthorized_unlike(client, quote):
    resp = client.delete('/v1/likes/{0.id}'.format(quote))
    assert resp.status_code == 401


def test_unauthorized_get_favorites(client):
    resp = client.get('/v1/likes')
    assert resp.status_code == 401


def test_authorized_like(client_admin, quote):
    post_data = {
        'id': quote.id
    }

    resp = client_admin.post('/v1/likes', data=post_data)

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quote.json')


def test_authorized_unlike(client_admin, quote):
    resp = client_admin.delete('/v1/likes/{0.id}'.format(quote))

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quote.json')


def test_authorized_get_favorites(client_admin):
    resp = client_admin.get('/v1/likes')

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quotes.json')
