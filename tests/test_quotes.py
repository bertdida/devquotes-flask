import json

from .utils.assertions import assert_valid_schema


def test_quotes(client, create_quotes):
    resp = client.get('/v1/quotes')
    json_data = json.loads(resp.data)

    assert resp.status_code == 200
    assert_valid_schema(json_data, 'quotes.json')


def test_quote(client, create_quotes):
    resp = client.get('/v1/quotes/1')
    json_data = json.loads(resp.data)

    assert resp.status_code == 200
    assert_valid_schema(json_data, 'quote.json')


def test_quote_random(client, create_quotes):
    resp = client.get('/v1/quotes/random')
    json_data = json.loads(resp.data)

    assert resp.status_code == 200
    assert_valid_schema(json_data, 'quote.json')


def test_quote_404(client):
    resp = client.get('/v1/quotes/1')

    assert resp.status_code == 404


def test_create_quote(client):
    pass


def test_update_quote(client):
    pass


def test_delete_quote(client):
    pass
