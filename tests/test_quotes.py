from .utils.assertions import (
    assert_post_data_in_response,
    assert_valid_schema,
)

NEW_QUOTE = {
    'author': 'Austin Freeman',
    'quotation': 'Simplicity is the soul of efficiency.',
}


def test_get_quotes(client):
    resp = client.get('/v1/quotes')

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quotes.json')


def test_get_quote(client, quote):
    resp = client.get('/v1/quotes/{0.id}'.format(quote))

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quote.json')


def test_get_quote_random(client):
    resp = client.get('/v1/quotes/random')

    assert resp.status_code == 200
    assert_valid_schema(resp.json, 'quote.json')


def test_search_quote(client, quote):
    resp = client.get('/v1/quotes/?={0.author}'.format(quote))
    assert resp.status_code == 200

    json = resp.json
    first_result = json['data'][0]['data']

    assert first_result['id'] == quote.id
    assert_valid_schema(json, 'quotes.json')


def test_get_quote_not_found(client):
    resp = client.get('/v1/quotes/2')
    assert resp.status_code == 404


def test_create_quote(client):
    resp = client.post('/v1/quotes', data=NEW_QUOTE)
    assert resp.status_code == 401


def test_update_quote(client, quote):
    post_data = {
        'author': 'Linus Benedict Torvalds',
        'quotation': quote.quotation,
    }

    resp = client.patch('/v1/quotes/{0.id}'.format(quote), data=post_data)
    assert resp.status_code == 401


def test_delete_quote(client, quote):
    resp = client.delete('/v1/quotes/{0.id}'.format(quote))
    assert resp.status_code == 401


def test_create_quote_admin(client_admin):
    resp = client_admin.post('/v1/quotes', data=NEW_QUOTE)

    assert resp.status_code == 201
    assert_post_data_in_response(NEW_QUOTE, resp)
    assert_valid_schema(resp.json, 'quote.json')


def test_update_quote_admin(client_admin, quote):
    post_data = {
        'author': 'Linus Benedict Torvalds',
        'quotation': quote.quotation,
    }

    resp = client_admin.patch('/v1/quotes/{0.id}'.format(quote), data=post_data)  # noqa

    assert resp.status_code == 200
    assert_post_data_in_response(post_data, resp)
    assert_valid_schema(resp.json, 'quote.json')


def test_delete_quote_admin(client_admin, quote):
    resp = client_admin.delete('/v1/quotes/{0.id}'.format(quote))
    assert resp.status_code == 204
