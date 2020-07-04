from .utils.assertions import (
    assert_valid_response_data,
    assert_valid_schema,
)


def test_get_quotes(client):
    resp = client.get('/v1/quotes')

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quotes.json')


def test_get_quote(client):
    resp = client.get('/v1/quotes/1')

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quote.json')


def test_get_quote_random(client):
    resp = client.get('/v1/quotes/random')

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quote.json')


def test_get_quote_404(client):
    resp = client.get('/v1/quotes/2')
    assert resp.status_code == 404


def test_create_quote(client):
    post_data = {
        'author': 'Austin Freeman',
        'quotation': 'Simplicity is the soul of efficiency.',
    }

    resp = client.post('/v1/quotes', data=post_data)
    assert resp.status_code == 401


def test_update_quote(client):
    post_data = {
        'author': 'Linus Benedict Torvalds',
        'quotation': 'Talk is cheap. Show me the code.',
    }

    resp = client.patch('/v1/quotes/1', data=post_data)
    assert resp.status_code == 401


def test_delete_quote(client):
    resp = client.delete('/v1/quotes/1')
    assert resp.status_code == 401


def test_create_quote_admin(client_admin):
    post_data = {
        'author': 'Austin Freeman',
        'quotation': 'Simplicity is the soul of efficiency.',
    }

    resp = client_admin.post('/v1/quotes', data=post_data)

    assert resp.status_code == 201
    assert_valid_response_data(post_data, resp)
    assert_valid_schema(resp.json, 'quote.json')


def test_update_quote_admin(client_admin):
    post_data = {
        'author': 'Linus Benedict Torvalds',
        'quotation': 'Talk is cheap. Show me the code.',
    }

    resp = client_admin.patch('/v1/quotes/1', data=post_data)

    assert resp.status_code == 200
    assert_valid_response_data(post_data, resp)
    assert_valid_schema(resp.json, 'quote.json')


def test_delete_quote_admin(client_admin):
    resp = client_admin.delete('/v1/quotes/2')
    assert resp.status_code == 204
